#!/usr/bin/env python3

import json
import os
import platform
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime


APP_NAME = "SignalLab"
VERSION = "2.0.0"
LOG_FILE = "signallab.log"

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"


# ============================================================
# BASIC FUNCTIONS
# ============================================================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    print(f"""
{CYAN}{BOLD}
   _____ _                   _  _      _          _
  / ____(_)                 | || |    | |        | |
 | (___  _  __ _ _ __   __ _| || |    | |     ___| |__
  \\___ \\| |/ _` | '_ \\ / _` | || |_   | |    / _ \\ '_ \\
  ____) | | (_| | | | | (_| |__   _|  | |___|  __/ |_) |
 |_____/|_|\\__, |_| |_|\\__,_|  |_|    |______\\___|_.__/
             __/ |
            |___/
{RESET}
{WHITE}Network, Domain & Mail Intelligence Toolkit{RESET}
{YELLOW}Version {VERSION} • Linux / Termux / Windows{RESET}
""")


def pause():
    input(f"\n{YELLOW}Press Enter to continue...{RESET}")


def write_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as file:
            file.write(f"[{timestamp}] {message}\n")
    except OSError:
        pass


def success(message):
    print(f"{GREEN}[+] {message}{RESET}")
    write_log(message)


def error(message):
    print(f"{RED}[!] {message}{RESET}")
    write_log(f"ERROR: {message}")


def info(message):
    print(f"{BLUE}[*] {message}{RESET}")


def normalize_domain(domain):
    domain = domain.strip().lower()

    if "://" in domain:
        parsed = urllib.parse.urlparse(domain)
        domain = parsed.hostname or ""

    domain = domain.split("/")[0]
    domain = domain.split(":")[0]
    domain = domain.rstrip(".")

    return domain


def valid_domain(domain):
    if not domain or len(domain) > 253:
        return False

    pattern = r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$"

    return bool(re.match(pattern, domain, re.IGNORECASE))


def http_get_json(url, timeout=12):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "SignalLab/2.0",
            "Accept": "application/json"
        }
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = response.read().decode("utf-8", errors="replace")
        return response.status, json.loads(data)


def http_get_text(url, timeout=12):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "SignalLab/2.0"
        }
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = response.read().decode("utf-8", errors="replace")
        return response.status, response.headers, data


# ============================================================
# RDAP / DOMAIN REGISTRATION LOOKUP
# ============================================================

def get_rdap_server(domain):
    tld = domain.split(".")[-1].lower()

    bootstrap_url = "https://data.iana.org/rdap/dns.json"

    try:
        _, data = http_get_json(bootstrap_url)

        for service in data.get("services", []):
            if not service or len(service) < 2:
                continue

            tlds = service[0]
            servers = service[1]

            if tld in [str(x).lower() for x in tlds]:
                if servers:
                    return servers[0].rstrip("/")

    except Exception:
        return None

    return None


def format_rdap_date(value):
    if not value:
        return "Not available"

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.strftime("%Y-%m-%d")
    except Exception:
        return value[:10] if len(value) >= 10 else value


def extract_event(events, event_name):
    for event in events or []:
        if event.get("eventAction") == event_name:
            return format_rdap_date(event.get("eventDate"))

    return "Not available"


def extract_registrar(entities):
    for entity in entities or []:
        roles = entity.get("roles", [])

        if "registrar" in roles:
            vcard = entity.get("vcardArray", [])

            if (
                isinstance(vcard, list)
                and len(vcard) > 1
                and isinstance(vcard[1], list)
            ):
                for item in vcard[1]:
                    if len(item) >= 4 and item[0] == "fn":
                        return item[3]

    return "Not available"


def domain_registration_lookup():
    clear_screen()
    banner()

    print(f"{BOLD}{WHITE}DOMAIN REGISTRATION LOOKUP{RESET}\n")

    domain = input("Enter domain: ").strip()
    domain = normalize_domain(domain)

    if not valid_domain(domain):
        error("Please enter a valid domain name.")
        pause()
        return

    print()
    info(f"Looking up registration data for {domain}...")

    rdap_server = get_rdap_server(domain)

    if not rdap_server:
        error("No RDAP server found for this domain's TLD.")
        pause()
        return

    rdap_url = f"{rdap_server}/domain/{urllib.parse.quote(domain)}"

    try:
        status_code, data = http_get_json(rdap_url)

        if status_code == 404:
            print()
            print(f"{BOLD}DOMAIN INFORMATION{RESET}")
            print("--------------------------------")
            print(f"Domain : {domain}")
            print("Status : NOT REGISTERED")
            write_log(f"RDAP lookup: {domain} | not registered")
            pause()
            return

        statuses = data.get("status", [])

        registration_status = "Registered"

        if statuses:
            status_text = ", ".join(statuses)
        else:
            status_text = "Not available"

        registration_date = extract_event(
            data.get("events"),
            "registration"
        )

        expiration_date = extract_event(
            data.get("events"),
            "expiration"
        )

        updated_date = extract_event(
            data.get("events"),
            "last changed"
        )

        registrar = extract_registrar(
            data.get("entities")
        )

        nameservers = []

        for ns in data.get("nameservers", []):
            name = ns.get("ldhName")

            if name:
                nameservers.append(name.rstrip("."))

        print()
        print(f"{BOLD}{WHITE}DOMAIN INFORMATION{RESET}")
        print("--------------------------------")
        print(f"Domain          : {domain}")
        print(f"Status          : {registration_status}")
        print(f"Registration    : {registration_date}")
        print(f"Expiration      : {expiration_date}")
        print(f"Last Updated    : {updated_date}")
        print(f"Registrar       : {registrar}")
        print(f"RDAP Server     : {rdap_server}")

        print("\nDomain Status:")
        print(f"  {status_text}")

        print("\nName Servers:")

        if nameservers:
            for server in nameservers:
                print(f"  • {server}")
        else:
            print("  Not available")

        write_log(
            f"RDAP lookup: {domain} | "
            f"registered={registration_status} | "
            f"expiration={expiration_date}"
        )

    except urllib.error.HTTPError as exc:

        if exc.code == 404:
            print()
            print(f"{BOLD}DOMAIN INFORMATION{RESET}")
            print("--------------------------------")
            print(f"Domain : {domain}")
            print("Status : NOT REGISTERED")

            write_log(
                f"RDAP lookup: {domain} | not registered"
            )

        else:
            error(f"RDAP server returned HTTP {exc.code}.")

    except Exception as exc:
        error(f"Unable to retrieve registration data: {exc}")

    pause()


# ============================================================
# DNS OVER HTTPS
# ============================================================

def doh_query(name, record_type):
    encoded_name = urllib.parse.quote(name)

    url = (
        "https://cloudflare-dns.com/dns-query"
        f"?name={encoded_name}&type={record_type}"
    )

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/dns-json",
            "User-Agent": "SignalLab/2.0"
        }
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        data = response.read().decode("utf-8", errors="replace")
        return json.loads(data)


def get_dns_records(name, record_type):
    try:
        data = doh_query(name, record_type)

        answers = data.get("Answer", [])

        records = []

        for answer in answers:
            value = answer.get("data")

            if value:
                records.append(value)

        return records

    except Exception:
        return []


# ============================================================
# TEAM MAIL / EMAIL SECURITY
# ============================================================

def team_mail():
    clear_screen()
    banner()

    print(f"{BOLD}{WHITE}TEAM MAIL / DOMAIN MAIL INTELLIGENCE{RESET}\n")

    domain = input("Enter domain: ").strip()
    domain = normalize_domain(domain)

    if not valid_domain(domain):
        error("Please enter a valid domain.")
        pause()
        return

    print()
    info(f"Checking mail configuration for {domain}...")

    mx_records = get_dns_records(domain, "MX")
    txt_records = get_dns_records(domain, "TXT")
    dmarc_records = get_dns_records(
        f"_dmarc.{domain}",
        "TXT"
    )

    print()
    print(f"{BOLD}{WHITE}MAIL CONFIGURATION{RESET}")
    print("--------------------------------")
    print(f"Domain : {domain}")

    print("\nMX Records:")

    if mx_records:

        for record in mx_records:
            print(f"  • {record}")

    else:
        print("  No MX records found.")

    spf_records = []

    for record in txt_records:

        clean_record = record.strip('"')

        if clean_record.lower().startswith("v=spf1"):
            spf_records.append(clean_record)

    print("\nSPF:")

    if spf_records:

        for record in spf_records:
            print(f"  [+] {record}")

    else:
        print("  [!] SPF record not found.")

    print("\nDMARC:")

    if dmarc_records:

        for record in dmarc_records:
            print(f"  [+] {record}")

    else:
        print("  [!] DMARC record not found.")

    print("\nMail Status:")

    if mx_records:
        print("  [+] Domain has mail servers.")
    else:
        print("  [!] No MX mail server found.")

    if spf_records:
        print("  [+] SPF configured.")
    else:
        print("  [!] SPF not detected.")

    if dmarc_records:
        print("  [+] DMARC configured.")
    else:
        print("  [!] DMARC not detected.")

    print("\nSuggested Team Addresses:")
    print("  • contact@" + domain)
    print("  • support@" + domain)
    print("  • hello@" + domain)
    print("  • info@" + domain)
    print("  • team@" + domain)

    print(
        "\nNote: SignalLab does not create mailboxes or "
        "retrieve private email accounts."
    )

    write_log(
        f"Team Mail lookup: {domain} | "
        f"MX={len(mx_records)} | "
        f"SPF={len(spf_records)} | "
        f"DMARC={len(dmarc_records)}"
    )

    pause()


# ============================================================
# DNS / HOST LOOKUP
# ============================================================

def dns_lookup():
    clear_screen()
    banner()

    print(f"{BOLD}{WHITE}DNS / HOST LOOKUP{RESET}\n")

    hostname = input("Enter hostname: ").strip()

    if not hostname:
        error("Hostname cannot be empty.")
        pause()
        return

    hostname = normalize_domain(hostname)

    try:
        start = time.perf_counter()

        addresses = socket.getaddrinfo(
            hostname,
            None,
            socket.AF_INET
        )

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        ips = sorted(
            set(
                item[4][0]
                for item in addresses
            )
        )

        print()
        success("DNS lookup successful.")

        print(f"  Host          : {hostname}")

        for index, ip in enumerate(ips, 1):
            print(f"  IPv4 #{index:<6}: {ip}")

        print(f"  Lookup time   : {elapsed:.2f} ms")

        write_log(
            f"DNS lookup: {hostname} | "
            f"IPs={','.join(ips)}"
        )

    except socket.gaierror:
        error("Unable to resolve hostname.")

    pause()


# ============================================================
# NETWORK INFORMATION
# ============================================================

def network_info():
    clear_screen()
    banner()

    print(f"{BOLD}{WHITE}NETWORK INFORMATION{RESET}\n")

    hostname = socket.gethostname()

    try:
        local_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        local_ip = "Unavailable"

    print(f"  Hostname : {hostname}")
    print(f"  Local IP : {local_ip}")
    print(f"  System   : {platform.system()}")
    print(f"  Release  : {platform.release()}")
    print(f"  Machine  : {platform.machine()}")
    print(f"  Python   : {platform.python_version()}")

    write_log("Displayed network/system information.")

    pause()


# ============================================================
# HTTP / API TESTER
# ============================================================

def api_test():
    clear_screen()
    banner()

    print(f"{BOLD}{WHITE}HTTP / API RESPONSE TESTER{RESET}\n")

    url = input("Enter URL: ").strip()

    if not url:
        error("URL cannot be empty.")
        pause()
        return

    if not url.startswith(("http://", "https://")):
        error("URL must start with http:// or https://")
        pause()
        return

    print()
    info("Testing endpoint...")

    start = time.perf_counter()

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "SignalLab/2.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            elapsed = (
                time.perf_counter() - start
            ) * 1000

            status = response.status
            content_type = response.headers.get(
                "Content-Type",
                "Unknown"
            )

            server = response.headers.get(
                "Server",
                "Not disclosed"
            )

            print()
            success("Request completed.")

            print(f"  Status        : {status}")
            print(f"  Response time : {elapsed:.2f} ms")
            print(f"  Content-Type  : {content_type}")
            print(f"  Server        : {server}")

            write_log(
                f"API test: {url} | "
                f"status={status} | "
                f"time={elapsed:.2f}ms"
            )

    except urllib.error.HTTPError as exc:

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        error(f"HTTP error: {exc.code}")

        print(
            f"  Response time : {elapsed:.2f} ms"
        )

    except urllib.error.URLError as exc:
        error(f"Connection failed: {exc.reason}")

    except Exception as exc:
        error(f"Unexpected error: {exc}")

    pause()


# ============================================================
# CONNECTIVITY TEST
# ============================================================

def connectivity_test():
    clear_screen()
    banner()

    print(f"{BOLD}{WHITE}CONNECTIVITY TEST{RESET}\n")

    host = input(
        "Enter host (example.com): "
    ).strip()

    if not host:
        error("Host cannot be empty.")
        pause()
        return

    host = normalize_domain(host)

    print()

    try:
        start = time.perf_counter()

        with socket.create_connection(
            (host, 443),
            timeout=5
        ):
            elapsed = (
                time.perf_counter() - start
            ) * 1000

        success("TCP connectivity available.")

        print(f"  Host : {host}")
        print("  Port : 443")
        print(f"  Time : {elapsed:.2f} ms")

        write_log(
            f"Connectivity test: "
            f"{host}:443 | {elapsed:.2f}ms"
        )

    except OSError as exc:
        error(f"Connection failed: {exc}")

    pause()


# ============================================================
# LOGS
# ============================================================

def show_logs():
    clear_screen()
    banner()

    print(f"{BOLD}{WHITE}SIGNALLAB LOGS{RESET}\n")

    if not os.path.exists(LOG_FILE):
        info("No logs available yet.")
        pause()
        return

    try:

        with open(
            LOG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read()

        if content.strip():
            print(content)
        else:
            info("Log file is empty.")

    except OSError as exc:
        error(f"Unable to read logs: {exc}")

    pause()


# ============================================================
# ABOUT
# ============================================================

def about():
    clear_screen()
    banner()

    print(f"{BOLD}{WHITE}ABOUT SIGNAL LAB{RESET}\n")

    print(
        "SignalLab is a lightweight toolkit for "
        "domain, network and mail diagnostics."
    )

    print()
    print("Features:")
    print("  • Domain registration lookup")
    print("  • Team mail configuration")
    print("  • DNS / hostname lookup")
    print("  • Network information")
    print("  • HTTP/API testing")
    print("  • TCP connectivity testing")
    print("  • Local activity logging")

    print()
    print(f"Version : {VERSION}")
    print("Author  : Arun Adhikari")
    print("License : MIT")

    pause()


# ============================================================
# MAIN MENU
# ============================================================

def main_menu():

    while True:

        clear_screen()
        banner()

        print(f"{BOLD}{WHITE}MAIN MENU{RESET}\n")

        print(
            f"{CYAN}[1]{RESET} "
            "Domain Registration Lookup"
        )

        print(
            f"{CYAN}[2]{RESET} "
            "Team Mail"
        )

        print(
            f"{CYAN}[3]{RESET} "
            "DNS / Host Lookup"
        )

        print(
            f"{CYAN}[4]{RESET} "
            "Network Information"
        )

        print(
            f"{CYAN}[5]{RESET} "
            "HTTP / API Tester"
        )

        print(
            f"{CYAN}[6]{RESET} "
            "Connectivity Test"
        )

        print(
            f"{CYAN}[7]{RESET} "
            "View Logs"
        )

        print(
            f"{CYAN}[8]{RESET} "
            "About SignalLab"
        )

        print(
            f"{RED}[0]{RESET} "
            "Exit"
        )

        print()

        choice = input(
            f"{BOLD}SignalLab > {RESET}"
        ).strip()

        if choice == "1":
            domain_registration_lookup()

        elif choice == "2":
            team_mail()

        elif choice == "3":
            dns_lookup()

        elif choice == "4":
            network_info()

        elif choice == "5":
            api_test()

        elif choice == "6":
            connectivity_test()

        elif choice == "7":
            show_logs()

        elif choice == "8":
            about()

        elif choice == "0":

            clear_screen()

            print(
                f"\n{GREEN}"
                "Thanks for using SignalLab!"
                f"{RESET}\n"
            )

            sys.exit(0)

        else:

            error("Invalid option.")
            time.sleep(1)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    try:
        main_menu()

    except KeyboardInterrupt:

        print(
            f"\n\n{YELLOW}"
            "SignalLab stopped by user."
            f"{RESET}\n"
        )

        sys.exit(0)
