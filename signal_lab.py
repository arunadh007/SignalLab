#!/usr/bin/env python3
import json
import os
import platform
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime

APP_NAME = "SignalLab"
VERSION = "4.1.0"
LOG_FILE = "signallab.log"

MAILTM_API = "https://api.mail.tm"
RANDOM_USER_API = "https://randomuser.me/api/"

RESET="\033[0m"; BOLD="\033[1m"; CYAN="\033[96m"; GREEN="\033[92m"
YELLOW="\033[93m"; RED="\033[91m"; BLUE="\033[94m"; WHITE="\033[97m"

MAILBOX = None  # {"address": ..., "password": ..., "token": ..., "id": ...}

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    print(f"""{CYAN}{BOLD}
   _____ _                   _  _      _          _
  / ____(_)                 | || |    | |        | |
 | (___  _  __ _ _ __   __ _| || |    | |     ___| |__
  \\___ \\| |/ _` | '_ \\ / _` | || |_   | |    / _ \\ '_ \\
  ____) | | (_| | | | | (_| |__   _|  | |___|  __/ |_) |
 |_____/|_|\\__, |_| |_|\\__,_|  |_|    |______\\___|_.__/
             __/ |
            |___/
{RESET}{WHITE}Network, Domain, Mail & OSINT Toolkit{RESET}
{YELLOW}Version {VERSION} • Linux / Termux / Windows{RESET}
""")

def pause():
    input(f"\n{YELLOW}Press Enter to continue...{RESET}")

def write_log(message):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}\n")
    except OSError:
        pass

def success(message):
    print(f"{GREEN}[+] {message}{RESET}")
    write_log(message)

def error(message):
    print(f"{RED}[!] {message}{RESET}")
    write_log("ERROR: " + message)

def info(message):
    print(f"{BLUE}[*] {message}{RESET}")

def http_request(url, method="GET", payload=None, headers=None, timeout=20):
    headers = {"User-Agent": "SignalLab/4.1", **(headers or {})}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8", errors="replace")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(body)
            detail = detail.get("message") or detail.get("detail") or body
        except Exception:
            detail = body
        raise RuntimeError(f"HTTP {e.code}: {detail}".strip())
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}")

def api_get(url, headers=None, timeout=20):
    return http_request(url, "GET", headers=headers, timeout=timeout)

def normalize_domain(value):
    value = value.strip().lower()
    if "://" in value:
        value = urllib.parse.urlparse(value).hostname or ""
    return value.split("/")[0].split(":")[0].rstrip(".")

def valid_domain(domain):
    return bool(re.match(r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$", domain, re.I))

# ---------------- Domain Investigator ----------------

def domain_investigator():
    clear_screen(); banner()
    print(f"{BOLD}DOMAIN INVESTIGATOR{RESET}\n")
    domain = normalize_domain(input("Enter domain: "))
    if not valid_domain(domain):
        error("Please enter a valid domain."); pause(); return
    info(f"Looking up public RDAP data for {domain}...")
    try:
        tld = domain.rsplit(".", 1)[-1]
        iana = api_get("https://data.iana.org/rdap/dns.json")
        server = None
        for service in iana.get("services", []):
            if len(service) >= 2 and tld in [str(x).lower() for x in service[0]]:
                if service[1]:
                    server = service[1][0].rstrip("/")
                    break
        if not server:
            raise RuntimeError("No RDAP server found for this TLD.")
        data = api_get(f"{server}/domain/{urllib.parse.quote(domain)}")
        def event(name):
            for e in data.get("events", []):
                if e.get("eventAction") == name:
                    return str(e.get("eventDate", ""))[:10] or "Not available"
            return "Not available"
        registrar = "Not available"
        for ent in data.get("entities", []):
            if "registrar" in ent.get("roles", []):
                for item in ent.get("vcardArray", [[], []])[1]:
                    if len(item) >= 4 and item[0] == "fn":
                        registrar = item[3]; break
        print("\nDOMAIN INFORMATION")
        print("--------------------------------")
        print(f"Domain       : {domain}")
        print(f"Status       : Registered")
        print(f"Registration : {event('registration')}")
        print(f"Expiration   : {event('expiration')}")
        print(f"Last Updated : {event('last changed')}")
        print(f"Registrar    : {registrar}")
        print(f"RDAP Server  : {server}")
        print("\nDomain Status:")
        for s in data.get("status", []): print(f"  • {s}")
        print("\nName Servers:")
        ns = [x.get("ldhName","").rstrip(".") for x in data.get("nameservers", []) if x.get("ldhName")]
        for x in ns: print(f"  • {x}")
        if not ns: print("  Not available")
        write_log(f"Domain Investigator: {domain}")
    except Exception as e:
        error(f"Domain lookup failed: {e}")
    pause()

# ---------------- Disposable Inbox: Mail.tm ----------------

def mailtm_get_domains():
    data = api_get(f"{MAILTM_API}/domains")
    domains = data.get("hydra:member", [])
    active = [d["domain"] for d in domains if d.get("isActive") and d.get("domain")]
    if not active:
        raise RuntimeError("Mail.tm returned no active domains.")
    return active

def mailtm_create_account():
    global MAILBOX
    domain = mailtm_get_domains()[0]
    local = "signal" + uuid.uuid4().hex[:10]
    address = f"{local}@{domain}"
    password = uuid.uuid4().hex + "A9!"
    account = http_request(
        f"{MAILTM_API}/accounts",
        method="POST",
        payload={"address": address, "password": password}
    )
    token_data = http_request(
        f"{MAILTM_API}/token",
        method="POST",
        payload={"address": address, "password": password}
    )
    MAILBOX = {
        "id": account.get("id"),
        "address": address,
        "password": password,
        "token": token_data.get("token")
    }
    if not MAILBOX["token"]:
        raise RuntimeError("Mail.tm did not return an access token.")
    return address

def mailtm_auth_headers():
    if not MAILBOX or not MAILBOX.get("token"):
        raise RuntimeError("Generate a temporary email first.")
    return {"Authorization": "Bearer " + MAILBOX["token"]}

def mailtm_messages():
    data = api_get(f"{MAILTM_API}/messages", headers=mailtm_auth_headers())
    return data.get("hydra:member", [])

def mailtm_read(message_id):
    return api_get(
        f"{MAILTM_API}/messages/{urllib.parse.quote(str(message_id))}",
        headers=mailtm_auth_headers()
    )

def disposable_inbox():
    global MAILBOX
    while True:
        clear_screen(); banner()
        print(f"{BOLD}DISPOSABLE INBOX{RESET}\n")
        if MAILBOX:
            print(f"{GREEN}Current Email:{RESET} {BOLD}{MAILBOX['address']}{RESET}")
        else:
            print(f"{YELLOW}No temporary email generated.{RESET}")
        print("\n[1] Generate New Email")
        print("[2] Refresh Inbox")
        print("[3] Read Message")
        print("[4] Show Current Email")
        print("[0] Back")
        choice = input("\nDisposable Inbox > ").strip()

        if choice == "1":
            try:
                info("Creating temporary mailbox...")
                address = mailtm_create_account()
                success(f"Temporary email created: {address}")
                print(f"\n{YELLOW}This mailbox is receive-only and intended for testing/privacy use.{RESET}")
            except Exception as e:
                error(f"Unable to create mailbox: {e}")
            pause()

        elif choice == "2":
            try:
                messages = mailtm_messages()
                print("\nINBOX")
                print("=" * 64)
                if not messages:
                    info("No messages received yet.")
                for i, m in enumerate(messages, 1):
                    sender = (m.get("from") or {}).get("address", "Unknown")
                    print(f"[{i}] {m.get('subject') or '(No subject)'}")
                    print(f"    From : {sender}")
                    print(f"    Date : {m.get('createdAt','Unknown')}")
                    print(f"    ID   : {m.get('id','Unknown')}")
                    print("-" * 64)
                write_log(f"Disposable Inbox refreshed: {MAILBOX['address']}")
            except Exception as e:
                error(f"Inbox request failed: {e}")
            pause()

        elif choice == "3":
            try:
                messages = mailtm_messages()
                if not messages:
                    info("No messages available."); pause(); continue
                print("\nAVAILABLE MESSAGES")
                for i, m in enumerate(messages, 1):
                    print(f"[{i}] {m.get('subject') or '(No subject)'}")
                try:
                    selected = int(input("\nSelect message: "))
                    if not 1 <= selected <= len(messages): raise ValueError
                except ValueError:
                    error("Invalid message selection."); pause(); continue
                m = mailtm_read(messages[selected-1]["id"])
                sender = (m.get("from") or {}).get("address", "Unknown")
                text = m.get("text") or ""
                print("\nMESSAGE")
                print("=" * 64)
                print(f"From    : {sender}")
                print(f"Subject : {m.get('subject') or '(No subject)'}")
                print(f"Date    : {m.get('createdAt','Unknown')}")
                print("-" * 64)
                print(text if text.strip() else "(No plain-text body; HTML message available.)")
                print("=" * 64)
                write_log(f"Disposable Inbox message read: {MAILBOX['address']} | {m.get('id')}")
            except Exception as e:
                error(f"Unable to read message: {e}")
            pause()

        elif choice == "4":
            print()
            if MAILBOX:
                print(f"Current Email:\n\n{MAILBOX['address']}")
            else:
                info("No temporary email generated.")
            pause()

        elif choice == "0":
            return
        else:
            error("Invalid option."); time.sleep(1)

# ---------------- DNS ----------------

def dns_lookup():
    clear_screen(); banner()
    print(f"{BOLD}DNS / HOST LOOKUP{RESET}\n")
    host = normalize_domain(input("Enter hostname: "))
    if not host:
        error("Hostname cannot be empty."); pause(); return
    try:
        start = time.perf_counter()
        results = socket.getaddrinfo(host, None, socket.AF_INET)
        elapsed = (time.perf_counter() - start) * 1000
        ips = sorted(set(x[4][0] for x in results))
        success("DNS lookup successful.")
        print(f"\nHost        : {host}")
        for i, ip in enumerate(ips, 1): print(f"IPv4 #{i}    : {ip}")
        print(f"Lookup time : {elapsed:.2f} ms")
        write_log(f"DNS lookup: {host}")
    except socket.gaierror:
        error("Unable to resolve hostname.")
    pause()

# ---------------- Network Information ----------------

def network_info():
    clear_screen(); banner()
    print(f"{BOLD}NETWORK INFORMATION{RESET}\n")
    hostname = socket.gethostname()
    try: local_ip = socket.gethostbyname(hostname)
    except Exception: local_ip = "Unavailable"
    try:
        public_ip = urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode()
    except Exception:
        public_ip = "Unavailable"
    print(f"Hostname      : {hostname}")
    print(f"Local IP      : {local_ip}")
    print(f"Public IPv4   : {public_ip}")
    print(f"System        : {platform.system()}")
    print(f"Release       : {platform.release()}")
    print(f"Machine       : {platform.machine()}")
    print(f"Python        : {platform.python_version()}")
    print(f"FQDN          : {socket.getfqdn()}")
    write_log("Displayed network information.")
    pause()

# ---------------- Identity Generator ----------------

def identity_generator():
    clear_screen(); banner()
    print(f"{BOLD}IDENTITY GENERATOR{RESET}\n")
    print("Synthetic test identities only.\n")
    print("[1] Random Identity")
    print("[2] US Identity")
    print("[3] Indian Identity")
    print("[4] UK Identity")
    print("[0] Back")
    choice = input("\nIdentity Generator > ").strip()
    if choice == "0": return
    nat = {"2":"us", "3":"in", "4":"gb"}.get(choice)
    if choice not in ("1","2","3","4"):
        error("Invalid option."); pause(); return
    try:
        params = {"results":1, "inc":"gender,name,location,email,login,dob,phone,cell,picture,nat"}
        if nat: params["nat"] = nat
        data = api_get(RANDOM_USER_API + "?" + urllib.parse.urlencode(params))
        u = data["results"][0]
        n=u.get("name",{}); loc=u.get("location",{}); dob=u.get("dob",{})
        print("\nGENERATED TEST IDENTITY")
        print("="*48)
        print(f"Name         : {n.get('title','')} {n.get('first','')} {n.get('last','')}")
        print(f"Gender       : {u.get('gender','Unknown')}")
        print(f"Country      : {loc.get('country','Unknown')}")
        print(f"City         : {loc.get('city','Unknown')}")
        print(f"State        : {loc.get('state','Unknown')}")
        print(f"Email        : {u.get('email','Unknown')}")
        print(f"Phone        : {u.get('phone','Unknown')}")
        print(f"Mobile       : {u.get('cell','Unknown')}")
        print(f"Date of Birth: {dob.get('date','Unknown')[:10]}")
        print(f"Age          : {dob.get('age','Unknown')}")
        print(f"Username     : {u.get('login',{}).get('username','Unknown')}")
        print(f"Nationality  : {u.get('nat','Unknown')}")
        print("="*48)
        print(f"{YELLOW}Synthetic data — for testing only.{RESET}")
        write_log("Generated synthetic test identity.")
    except Exception as e:
        error(f"Identity API failed: {e}")
    pause()

# ---------------- Connectivity ----------------

def connectivity_test():
    clear_screen(); banner()
    print(f"{BOLD}CONNECTIVITY TEST{RESET}\n")
    host = normalize_domain(input("Enter host (example.com): "))
    try:
        start=time.perf_counter()
        with socket.create_connection((host,443), timeout=5): pass
        ms=(time.perf_counter()-start)*1000
        success("TCP connectivity available.")
        print(f"Host : {host}\nPort : 443\nTime : {ms:.2f} ms")
        write_log(f"Connectivity test: {host}:443")
    except OSError as e:
        error(f"Connection failed: {e}")
    pause()

# ---------------- Logs / About ----------------

def show_logs():
    clear_screen(); banner()
    print(f"{BOLD}SIGNALLAB LOGS{RESET}\n")
    if not os.path.exists(LOG_FILE):
        info("No logs available."); pause(); return
    try:
        with open(LOG_FILE, encoding="utf-8") as f: print(f.read() or "Log file is empty.")
    except OSError as e: error(str(e))
    pause()

def about():
    clear_screen(); banner()
    print(f"""{BOLD}ABOUT SIGNAL LAB{RESET}

Lightweight network, domain, mail and OSINT toolkit.

Modules:
  • Domain Investigator
  • Disposable Inbox
  • DNS / Host Lookup
  • Network Information
  • Identity Generator
  • Connectivity Test
  • Local Activity Logs

Version : {VERSION}
Author  : Arun Adhikari
License : MIT

Disposable Inbox uses Mail.tm's free REST API.
Identity Generator uses synthetic test data.
""")
    pause()

def main():
    while True:
        clear_screen(); banner()
        print(f"{BOLD}MAIN MENU{RESET}\n")
        print("[1] Domain Investigator")
        print("[2] Disposable Inbox")
        print("[3] DNS / Host Lookup")
        print("[4] Network Information")
        print("[5] Identity Generator")
        print("[6] Connectivity Test")
        print("[7] View Logs")
        print("[8] About SignalLab")
        print("[0] Exit")
        choice=input("\nSignalLab > ").strip()
        if choice=="1": domain_investigator()
        elif choice=="2": disposable_inbox()
        elif choice=="3": dns_lookup()
        elif choice=="4": network_info()
        elif choice=="5": identity_generator()
        elif choice=="6": connectivity_test()
        elif choice=="7": show_logs()
        elif choice=="8": about()
        elif choice=="0":
            print(f"\n{GREEN}Thanks for using SignalLab!{RESET}\n"); return
        else:
            error("Invalid option."); time.sleep(1)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}SignalLab stopped by user.{RESET}")
