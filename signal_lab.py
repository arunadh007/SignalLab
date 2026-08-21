#!/usr/bin/env python3

import json
import os
import platform
import random
import re
import socket
import string
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime


APP_NAME = "SignalLab"
VERSION = "3.0.0"

LOG_FILE = "signallab.log"
MAIL_SESSION_FILE = "tempmail_session.json"
MAIL_API = "https://api.mail.tm"

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
WHITE = "\033[97m"


# ============================================================
# GENERAL
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
{WHITE}Network, Domain, Mail & OSINT Toolkit{RESET}
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
    return domain.rstrip(".")


def valid_domain(domain):
    pattern = (
        r"^(?=.{1,253}$)"
        r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
        r"[a-z]{2,63}$"
    )
    return bool(re.match(pattern, domain, re.I))


# ============================================================
# HTTP / API
# ============================================================

def api_request(url, method="GET", data=None, headers=None, timeout=15):
    request_headers = {
        "User-Agent": "SignalLab/3.0"
    }

    if headers:
        request_headers.update(headers)

    body = None

    if data is not None:
        body = json.dumps(data).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        url,
        data=body,
        headers=request_headers,
        method=method
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace"
            )

            if not raw:
                return response.status, {}

            try:
                return response.status, json.loads(raw)
            except json.JSONDecodeError:
                return response.status, raw

    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(
            "utf-8",
            errors="replace"
        )

        try:
            data = json.loads(raw)
        except Exception:
            data = raw

        raise RuntimeError(
            f"HTTP {exc.code}: {data}"
        )


# ============================================================
# DISPOSABLE INBOX
# ============================================================

def save_mail_session(session):
    try:
        with open(
            MAIL_SESSION_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                session,
                file,
                indent=2
            )
    except OSError as exc:
        error(f"Unable to save mail session: {exc}")


def load_mail_session():
    if not os.path.exists(MAIL_SESSION_FILE):
        return None

    try:
        with open(
            MAIL_SESSION_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)
    except Exception:
        return None


def delete_mail_session():
    try:
        if os.path.exists(MAIL_SESSION_FILE):
            os.remove(MAIL_SESSION_FILE)
    except OSError:
        pass


def random_username():
    chars = string.ascii_lowercase + string.digits

    return (
        "".join(
            random.choice(chars)
            for _ in range(8)
        )
        + str(random.randint(100, 999))
    )


def random_password():
    chars = (
        string.ascii_letters
        + string.digits
        + "!@#$%^&*"
    )

    return "".join(
        random.choice(chars)
        for _ in range(18)
    )


def get_temp_domains():
    _, data = api_request(
        f"{MAIL_API}/domains"
    )

    domains = []

    for item in data.get(
        "hydra:member",
        []
    ):
        domain = item.get("domain")

        if domain and item.get(
            "isActive",
            True
        ):
            domains.append(domain)

    return domains


def create_disposable_mail():
    print()

    info(
        "Getting available disposable mail domains..."
    )

    try:
        domains = get_temp_domains()

        if not domains:
            error(
                "No temporary mail domains are available."
            )
            return

        domain = domains[0]
        username = random_username()
        password = random_password()

        address = f"{username}@{domain}"

        info(
            f"Creating mailbox: {address}"
        )

        status, account = api_request(
            f"{MAIL_API}/accounts",
            method="POST",
            data={
                "address": address,
                "password": password
            }
        )

        if status not in (200, 201):
            error(
                "Unable to create mailbox."
            )
            return

        _, token_data = api_request(
            f"{MAIL_API}/token",
            method="POST",
            data={
                "address": address,
                "password": password
            }
        )

        token = token_data.get("token")

        if not token:
            error(
                "Mailbox created but authentication token was not received."
            )
            return

        session = {
            "id": account.get("id"),
            "address": address,
            "password": password,
            "token": token,
            "created_at": datetime.now().isoformat()
        }

        save_mail_session(session)

        print()

        success(
            "Disposable mailbox created."
        )

        print(
            f"\n{BOLD}Your Disposable Email:{RESET}"
        )

        print(
            f"{CYAN}{address}{RESET}"
        )

        print(
            f"\nCreated: {session['created_at']}"
        )

        write_log(
            f"Disposable mailbox created: {address}"
        )

    except Exception as exc:
        error(
            f"Disposable Inbox error: {exc}"
        )


def show_current_mail():
    session = load_mail_session()

    if not session:
        print(
            f"{YELLOW}No disposable mailbox is active.{RESET}"
        )
        return

    print(
        f"{BOLD}{WHITE}"
        "CURRENT DISPOSABLE INBOX"
        f"{RESET}"
    )

    print(
        "--------------------------------"
    )

    print(
        f"Address : "
        f"{CYAN}{session.get('address')}{RESET}"
    )

    print(
        f"Created : "
        f"{session.get('created_at', 'Unknown')}"
    )


def get_mail_messages():
    session = load_mail_session()

    if not session:
        raise RuntimeError(
            "No active disposable mailbox."
        )

    headers = {
        "Authorization":
            f"Bearer {session['token']}"
    }

    _, data = api_request(
        f"{MAIL_API}/messages",
        headers=headers
    )

    return data.get(
        "hydra:member",
        []
    )


def refresh_inbox():
    clear_screen()
    banner()

    print(
        f"{BOLD}{WHITE}"
        "DISPOSABLE INBOX"
        f"{RESET}\n"
    )

    session = load_mail_session()

    if not session:
        info(
            "No disposable mailbox exists."
        )
        print(
            "\nUse option 1 to generate one."
        )
        pause()
        return

    print(
        f"Address : "
        f"{CYAN}{session['address']}{RESET}\n"
    )

    try:
        messages = get_mail_messages()

        if not messages:
            info(
                "Inbox is empty."
            )
            pause()
            return

        print(
            f"{BOLD}MESSAGES{RESET}"
        )

        print(
            "--------------------------------"
        )

        for index, message in enumerate(
            messages,
            1
        ):
            sender = (
                message
                .get("from", {})
                .get("address", "Unknown")
            )

            subject = message.get(
                "subject",
                "(No subject)"
            )

            status = (
                "READ"
                if message.get("seen")
                else "NEW"
            )

            print(
                f"[{index}] {status:<4} {sender}"
            )

            print(
                f"    Subject: {subject}"
            )

            print()

        write_log(
            f"Disposable Inbox refreshed: "
            f"{len(messages)} messages"
        )

    except Exception as exc:
        error(
            f"Unable to fetch inbox: {exc}"
        )

    pause()


def read_message():
    clear_screen()
    banner()

    print(
        f"{BOLD}{WHITE}"
        "READ MESSAGE"
        f"{RESET}\n"
    )

    session = load_mail_session()

    if not session:
        error(
            "No active disposable mailbox."
        )
        pause()
        return

    try:
        messages = get_mail_messages()

        if not messages:
            info(
                "Inbox is empty."
            )
            pause()
            return

        print(
            "Available messages:\n"
        )

        for index, message in enumerate(
            messages,
            1
        ):
            print(
                f"[{index}] "
                f"{message.get('subject', '(No subject)')}"
            )

        print()

        choice = input(
            "Select message number: "
        ).strip()

        if not choice.isdigit():
            error(
                "Invalid message number."
            )
            pause()
            return

        index = int(choice) - 1

        if index < 0 or index >= len(messages):
            error(
                "Message does not exist."
            )
            pause()
            return

        message_id = messages[index].get("id")

        headers = {
            "Authorization":
                f"Bearer {session['token']}"
        }

        _, message = api_request(
            f"{MAIL_API}/messages/{message_id}",
            headers=headers
        )

        sender = (
            message
            .get("from", {})
            .get("address", "Unknown")
        )

        subject = message.get(
            "subject",
            "(No subject)"
        )

        created = message.get(
            "createdAt",
            "Unknown"
        )

        text = message.get(
            "text",
            ""
        )

        print()

        print(
            f"{BOLD}MESSAGE{RESET}"
        )

        print(
            "--------------------------------"
        )

        print(
            f"From    : {sender}"
        )

        print(
            f"Subject : {subject}"
        )

        print(
            f"Date    : {created}"
        )

        print(
            "\nMessage Body:"
        )

        print(
            "--------------------------------"
        )

        print(
            text
            if text
            else "(No plain-text body available.)"
        )

        write_log(
            f"Disposable Inbox message opened: "
            f"{subject}"
        )

    except Exception as exc:
        error(
            f"Unable to read message: {exc}"
        )

    pause()


def delete_disposable_mailbox():
    clear_screen()
    banner()

    print(
        f"{BOLD}{WHITE}"
        "DELETE DISPOSABLE MAILBOX"
        f"{RESET}\n"
    )

    session = load_mail_session()

    if not session:
        info(
            "No active mailbox."
        )
        pause()
        return

    address = session.get(
        "address"
    )

    confirm = input(
        f"Delete {address}? (yes/no): "
    ).strip().lower()

    if confirm != "yes":
        info(
            "Mailbox deletion cancelled."
        )
        pause()
        return

    try:
        headers = {
            "Authorization":
                f"Bearer {session['token']}"
        }

        api_request(
            f"{MAIL_API}/accounts/{session['id']}",
            method="DELETE",
            headers=headers
        )

        delete_mail_session()

        success(
            "Disposable mailbox deleted."
        )

        write_log(
            f"Disposable mailbox deleted: {address}"
        )

    except Exception as exc:
        error(
            f"Unable to delete mailbox: {exc}"
        )

    pause()


def disposable_inbox():
    while True:
        clear_screen()
        banner()

        print(
            f"{BOLD}{WHITE}"
            "DISPOSABLE INBOX"
            f"{RESET}\n"
        )

        show_current_mail()

        print()

        print(
            f"{CYAN}[1]{RESET} "
            "Generate New Disposable Email"
        )

        print(
            f"{CYAN}[2]{RESET} "
            "Refresh Inbox"
        )

        print(
            f"{CYAN}[3]{RESET} "
            "Read Message"
        )

        print(
            f"{CYAN}[4]{RESET} "
            "Delete Mailbox"
        )

        print(
            f"{CYAN}[5]{RESET} "
            "Generate Another Address"
        )

        print(
            f"{CYAN}[0]{RESET} "
            "Back"
        )

        print()

        choice = input(
            f"{BOLD}Disposable Inbox > {RESET}"
        ).strip()

        if choice == "1":
            create_disposable_mail()
            pause()

        elif choice == "2":
            refresh_inbox()

        elif choice == "3":
            read_message()

        elif choice == "4":
            delete_disposable_mailbox()

        elif choice == "5":
            create_disposable_mail()
            pause()

        elif choice == "0":
            break

        else:
            error(
                "Invalid option."
            )
            time.sleep(1)


# ============================================================
# DOMAIN REGISTRATION / RDAP
# ============================================================

def get_rdap_server(domain):
    tld = domain.split(".")[-1].lower()

    try:
        _, data = api_request(
            "https://data.iana.org/rdap/dns.json"
        )

        for service in data.get(
            "services",
            []
        ):
            if len(service) < 2:
                continue

            tlds = service[0]
            servers = service[1]

            if tld in [
                str(x).lower()
                for x in tlds
            ]:
                if servers:
                    return servers[0].rstrip("/")

    except Exception:
        pass

    return None


def format_rdap_date(value):
    if not value:
        return "Not available"

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        return parsed.strftime(
            "%Y-%m-%d"
        )

    except Exception:
        return value[:10]


def extract_event(events, event_name):
    for event in events or []:
        if event.get(
            "eventAction"
        ) == event_name:
            return format_rdap_date(
                event.get("eventDate")
            )

    return "Not available"


def extract_registrar(entities):
    for entity in entities or []:
        if "registrar" not in entity.get(
            "roles",
            []
        ):
            continue

        vcard = entity.get(
            "vcardArray",
            []
        )

        if isinstance(vcard, list) and len(vcard) > 1:
            for item in vcard[1]:
                if (
                    len(item) >= 4
                    and item[0] == "fn"
                ):
                    return item[3]

    return "Not available"


def domain_registration_lookup():
    clear_screen()
    banner()

    print(
        f"{BOLD}{WHITE}"
        "DOMAIN REGISTRATION LOOKUP"
        f"{RESET}\n"
    )

    domain = input(
        "Enter domain: "
    ).strip()

    domain = normalize_domain(
        domain
    )

    if not valid_domain(domain):
        error(
            "Please enter a valid domain."
        )
        pause()
        return

    info(
        f"Looking up registration data "
        f"for {domain}..."
    )

    try:
        rdap_server = get_rdap_server(
            domain
        )

        if not rdap_server:
            error(
                "No RDAP server found."
            )
            pause()
            return

        url = (
            f"{rdap_server}/domain/"
            f"{urllib.parse.quote(domain)}"
        )

        _, data = api_request(url)

        registration = extract_event(
            data.get("events"),
            "registration"
        )

        expiration = extract_event(
            data.get("events"),
            "expiration"
        )

        updated = extract_event(
            data.get("events"),
            "last changed"
        )

        registrar = extract_registrar(
            data.get("entities")
        )

        statuses = data.get(
            "status",
            []
        )

        nameservers = []

        for ns in data.get(
            "nameservers",
            []
        ):
            name = ns.get(
                "ldhName"
            )

            if name:
                nameservers.append(
                    name.rstrip(".")
                )

        print()

        print(
            f"{BOLD}DOMAIN INFORMATION{RESET}"
        )

        print(
            "--------------------------------"
        )

        print(
            f"Domain          : {domain}"
        )

        print(
            "Status          : Registered"
        )

        print(
            f"Registration    : {registration}"
        )

        print(
            f"Expiration      : {expiration}"
        )

        print(
            f"Last Updated    : {updated}"
        )

        print(
            f"Registrar       : {registrar}"
        )

        print(
            f"RDAP Server     : {rdap_server}"
        )

        print(
            "\nDomain Status:"
        )

        for status in statuses:
            print(
                f"  • {status}"
            )

        print(
            "\nName Servers:"
        )

        if nameservers:
            for server in nameservers:
                print(
                    f"  • {server}"
                )
        else:
            print(
                "  Not available"
            )

        write_log(
            f"RDAP lookup: {domain}"
        )

    except urllib.error.HTTPError as exc:

        if exc.code == 404:
            print(
                f"\nDomain : {domain}"
            )

            print(
                "Status : NOT REGISTERED"
            )

        else:
            error(
                f"RDAP HTTP error: {exc.code}"
            )

    except Exception as exc:
        error(
            f"RDAP lookup failed: {exc}"
        )

    pause()


# ============================================================
# DNS
# ============================================================

def doh_query(name, record_type):
    encoded = urllib.parse.quote(name)

    url = (
        "https://cloudflare-dns.com/dns-query"
        f"?name={encoded}&type={record_type}"
    )

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/dns-json",
            "User-Agent": "SignalLab/3.0"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=10
    ) as response:
        return json.loads(
            response.read().decode(
                "utf-8",
                errors="replace"
            )
        )


def dns_lookup():
    clear_screen()
    banner()

    print(
        f"{BOLD}{WHITE}"
        "DNS / HOST LOOKUP"
        f"{RESET}\n"
    )

    hostname = input(
        "Enter hostname: "
    ).strip()

    hostname = normalize_domain(
        hostname
    )

    if not hostname:
        error(
            "Hostname cannot be empty."
        )
        pause()
        return

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

        success(
            "DNS lookup successful."
        )

        print(
            f"  Host        : {hostname}"
        )

        for index, ip in enumerate(
            ips,
            1
        ):
            print(
                f"  IPv4 #{index}: {ip}"
            )

        print(
            f"  Lookup time : {elapsed:.2f} ms"
        )

        write_log(
            f"DNS lookup: {hostname}"
        )

    except socket.gaierror:
        error(
            "Unable to resolve hostname."
        )

    pause()


# ============================================================
# NETWORK INFORMATION
# ============================================================

def network_info():
    clear_screen()
    banner()

    print(
        f"{BOLD}{WHITE}"
        "NETWORK INFORMATION"
        f"{RESET}\n"
    )

    hostname = socket.gethostname()

    try:
        local_ip = socket.gethostbyname(
            hostname
        )
    except socket.gaierror:
        local_ip = "Unavailable"

    print(
        f"{BOLD}SYSTEM{RESET}"
    )

    print(
        f"Hostname      : {hostname}"
    )

    print(
        f"System        : {platform.system()}"
    )

    print(
        f"Release       : {platform.release()}"
    )

    print(
        f"Machine       : {platform.machine()}"
    )

    print(
        f"Python        : {platform.python_version()}"
    )

    print(
        f"\n{BOLD}NETWORK{RESET}"
    )

    print(
        f"Local IP      : {local_ip}"
    )

    try:
        public_ip = urllib.request.urlopen(
            "https://api.ipify.org",
            timeout=5
        ).read().decode()
    except Exception:
        public_ip = "Unavailable"

    print(
        f"Public IPv4   : {public_ip}"
    )

    try:
        print(
            f"FQDN          : {socket.getfqdn()}"
        )
    except Exception:
        print(
            "FQDN          : Unavailable"
        )

    write_log(
        "Displayed network information."
    )

    pause()


# ============================================================
# HTTP / API TEST
# ============================================================

def api_test():
    clear_screen()
    banner()

    print(
        f"{BOLD}{WHITE}"
        "HTTP / API RESPONSE TESTER"
        f"{RESET}\n"
    )

    url = input(
        "Enter URL: "
    ).strip()

    if not url.startswith(
        ("http://", "https://")
    ):
        error(
            "URL must start with http:// or https://"
        )
        pause()
        return

    info(
        "Testing endpoint..."
    )

    start = time.perf_counter()

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    "SignalLab/3.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            elapsed = (
                time.perf_counter() - start
            ) * 1000

            print()

            success(
                "Request completed."
            )

            print(
                f"Status        : {response.status}"
            )

            print(
                f"Response time : {elapsed:.2f} ms"
            )

            print(
                f"Content-Type  : "
                f"{response.headers.get('Content-Type', 'Unknown')}"
            )

            print(
                f"Server        : "
                f"{response.headers.get('Server', 'Not disclosed')}"
            )

            write_log(
                f"API test: {url} | "
                f"status={response.status}"
            )

    except urllib.error.HTTPError as exc:
        error(
            f"HTTP error: {exc.code}"
        )

    except urllib.error.URLError as exc:
        error(
            f"Connection failed: {exc.reason}"
        )

    except Exception as exc:
        error(
            f"Unexpected error: {exc}"
        )

    pause()


# ============================================================
# CONNECTIVITY
# ============================================================

def connectivity_test():
    clear_screen()
    banner()

    print(
        f"{BOLD}{WHITE}"
        "CONNECTIVITY TEST"
        f"{RESET}\n"
    )

    host = input(
        "Enter host (example.com): "
    ).strip()

    host = normalize_domain(
        host
    )

    try:
        start = time.perf_counter()

        with socket.create_connection(
            (host, 443),
            timeout=5
        ):
            elapsed = (
                time.perf_counter() - start
            ) * 1000

        success(
            "TCP connectivity available."
        )

        print(
            f"Host : {host}"
        )

        print(
            "Port : 443"
        )

        print(
            f"Time : {elapsed:.2f} ms"
        )

        write_log(
            f"Connectivity test: {host}:443"
        )

    except OSError as exc:
        error(
            f"Connection failed: {exc}"
        )

    pause()


# ============================================================
# LOGS
# ============================================================

def show_logs():
    clear_screen()
    banner()

    print(
        f"{BOLD}{WHITE}"
        "SIGNALLAB LOGS"
        f"{RESET}\n"
    )

    if not os.path.exists(LOG_FILE):
        info(
            "No logs available."
        )
        pause()
        return

    try:
        with open(
            LOG_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            content = file.read()

        print(
            content
            if content.strip()
            else "Log file is empty."
        )

    except OSError as exc:
        error(
            f"Unable to read logs: {exc}"
        )

    pause()


# ============================================================
# ABOUT
# ============================================================

def about():
    clear_screen()
    banner()

    print(
        f"{BOLD}{WHITE}"
        "ABOUT SIGNAL LAB"
        f"{RESET}\n"
    )

    print(
        "SignalLab is a lightweight "
        "network, domain, mail and "
        "OSINT toolkit."
    )

    print()

    print(
        "Features:"
    )

    print(
        "  • Domain registration lookup"
    )

    print(
        "  • Disposable Inbox"
    )

    print(
        "  • Disposable email generation"
    )

    print(
        "  • Inbox refresh and message reader"
    )

    print(
        "  • DNS lookup"
    )

    print(
        "  • Network information"
    )

    print(
        "  • HTTP/API testing"
    )

    print(
        "  • TCP connectivity testing"
    )

    print(
        "  • Local activity logging"
    )

    print()

    print(
        f"Version : {VERSION}"
    )

    print(
        "Author  : Arun Adhikari"
    )

    print(
        "License : MIT"
    )

    print()

    print(
        "Disposable mail service:"
    )

    print(
        "https://mail.tm"
    )

    pause()


# ============================================================
# MAIN MENU
# ============================================================

def main_menu():
    while True:

        clear_screen()
        banner()

        print(
            f"{BOLD}{WHITE}"
            "MAIN MENU"
            f"{RESET}\n"
        )

        print(
            f"{CYAN}[1]{RESET} "
            "Domain Registration Lookup"
        )

        print(
            f"{CYAN}[2]{RESET} "
            "Disposable Inbox"
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
            disposable_inbox()

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

            error(
                "Invalid option."
            )

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
