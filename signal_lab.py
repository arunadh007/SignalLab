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
MAGENTA = "\033[95m"
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
    domain = domain.rstrip(".")

    return domain


def valid_domain(domain):
    if not domain or len(domain) > 253:
        return False

    pattern = (
        r"^(?=.{1,253}$)"
        r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
        r"[a-z]{2,63}$"
    )

    return bool(re.match(pattern, domain, re.IGNORECASE))


def random_username():
    chars = string.ascii_lowercase + string.digits

    return (
        "".join(random.choice(chars) for _ in range(8))
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


# ============================================================
# HTTP HELPERS
# ============================================================

def api_request(
    url,
    method="GET",
    data=None,
    headers=None,
    timeout=15
):

    request_headers = {
        "User-Agent": "SignalLab/3.0"
    }

    if headers:
        request_headers.update(headers)

    body = None

    if data is not None:

        body = json.dumps(data).encode("utf-8")

        request_headers[
            "Content-Type"
        ] = "application/json"

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


def http_get_json(url, timeout=12):

    return api_request(
        url,
        method="GET",
        timeout=timeout
    )


# ============================================================
# TEMP MAIL SESSION
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

        error(
            f"Unable to save mail session: {exc}"
        )


def load_mail_session():

    if not os.path.exists(
        MAIL_SESSION_FILE
    ):
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

        if os.path.exists(
            MAIL_SESSION_FILE
        ):
            os.remove(
                MAIL_SESSION_FILE
            )

    except OSError:
        pass


# ============================================================
# TEMP MAIL - DOMAIN
# ============================================================

def get_temp_domains():

    status, data = http_get_json(
        f"{MAIL_API}/domains"
    )

    domains = []

    for item in data.get(
        "hydra:member",
        []
    ):

        domain = item.get(
            "domain"
        )

        if (
            domain
            and item.get(
                "isActive",
                True
            )
        ):

            domains.append(domain)

    return domains


# ============================================================
# TEMP MAIL - CREATE ACCOUNT
# ============================================================

def create_temp_mail():

    print()

    info(
        "Getting available temporary mail domains..."
    )

    try:

        domains = get_temp_domains()

        if not domains:
            error(
                "No temporary mail domains are currently available."
            )

            return None

        domain = domains[0]

        username = random_username()
        password = random_password()

        address = (
            f"{username}@{domain}"
        )

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

        if status not in (
            200,
            201
        ):

            error(
                "Unable to create temporary mailbox."
            )

            return None

        status, token_data = api_request(
            f"{MAIL_API}/token",
            method="POST",
            data={
                "address": address,
                "password": password
            }
        )

        token = token_data.get(
            "token"
        )

        if not token:

            error(
                "Mailbox created, but token was not received."
            )

            return None

        session = {
            "id": account.get(
                "id"
            ),
            "address": address,
            "password": password,
            "token": token,
            "created_at": datetime.now().isoformat()
        }

        save_mail_session(
            session
        )

        print()
        success(
            "Temporary mailbox created."
        )

        print(
            f"\n{BOLD}Your Temporary Email:{RESET}"
        )

        print(
            f"{CYAN}{address}{RESET}"
        )

        print(
            f"\nCreated: "
            f"{session['created_at']}"
        )

        return session

    except Exception as exc:

        error(
            f"Temporary mail error: {exc}"
        )

        return None


# ============================================================
# TEMP MAIL - CURRENT ADDRESS
# ============================================================

def show_current_mail():

    session = load_mail_session()

    if not session:

        print()
        info(
            "No temporary mailbox is active."
        )

        return

    print()
    print(
        f"{BOLD}{WHITE}"
        "CURRENT TEMPORARY MAILBOX"
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


# ============================================================
# TEMP MAIL - LIST MESSAGES
# ============================================================

def get_mail_messages():

    session = load_mail_session()

    if not session:
        error(
            "No active temporary mailbox."
        )
        return []

    token = session.get(
        "token"
    )

    headers = {
        "Authorization":
            f"Bearer {token}"
    }

    status, data = api_request(
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
        "TEMP MAIL INBOX"
        f"{RESET}\n"
    )

    session = load_mail_session()

    if not session:

        info(
            "No mailbox exists."
        )

        print(
            "\nUse option 1 to generate one."
        )

        pause()
        return

    print(
        f"Address : "
        f"{CYAN}{session['address']}{RESET}"
    )

    print()

    try:

        messages = get_mail_messages()

        if not messages:

            info(
                "Inbox is empty."
            )

            pause()
            return

        print(
            f"{BOLD}"
            "MESSAGES"
            f"{RESET}"
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

            seen = message.get(
                "seen",
                False
            )

            status_text = (
                "READ"
                if seen
                else "NEW"
            )

            print(
                f"[{index}] "
                f"{status_text:<4} "
                f"{sender}"
            )

            print(
                f"    Subject: {subject}"
            )

            print()

        write_log(
            f"Temp Mail inbox refreshed: "
            f"{len(messages)} messages"
        )

    except Exception as exc:

        error(
            f"Unable to fetch inbox: {exc}"
        )

    pause()


# ============================================================
# TEMP MAIL - READ MESSAGE
# ============================================================

def read_message():

    clear_screen()
    banner()

    print(
        f"{BOLD}{WHITE}"
        "READ TEMP MAIL MESSAGE"
        f"{RESET}\n"
    )

    session = load_mail_session()

    if not session:

        error(
            "No active temporary mailbox."
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

        if index < 0 or index >= len(
            messages
        ):

            error(
                "Message does not exist."
            )

            pause()
            return

        message_id = messages[
            index
        ].get("id")

        token = session.get(
            "token"
        )

        headers = {
            "Authorization":
                f"Bearer {token}"
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
            f"{BOLD}{WHITE}"
            "MESSAGE"
            f"{RESET}"
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

        if text:

            print(text)

        else:

            print(
                "(No plain-text body available.)"
            )

        write_log(
            f"Temp Mail message opened: "
            f"{subject}"
        )

    except Exception as exc:

        error(
            f"Unable to read message: {exc}"
        )

    pause()


# ============================================================
# TEMP MAIL - DELETE MAILBOX
# ============================================================

def delete_temp_mailbox():

    clear_screen()
    banner()

    print(
        f"{BOLD}{WHITE}"
        "DELETE TEMPORARY MAILBOX"
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
        f"Delete {address}? "
        "(yes/no): "
    ).strip().lower()

    if confirm != "yes":

        info(
            "Mailbox deletion cancelled."
        )

        pause()
        return

    try:

        token = session.get(
            "token"
        )

        headers = {
            "Authorization":
                f"Bearer {token}"
        }

        mailbox_id = session.get(
            "id"
        )

        api_request(
            f"{MAIL_API}/accounts/{mailbox_id}",
            method="DELETE",
            headers=headers
        )

        delete_mail_session()

        success(
            "Temporary mailbox deleted."
        )

        write_log(
            f"Temp Mail mailbox deleted: "
            f"{address}"
        )

    except Exception as exc:

        error(
            f"Unable to delete mailbox: {exc}"
        )

    pause()


# ============================================================
# TEAM MAIL MENU
# ============================================================

def team_mail():

    while True:

        clear_screen()
        banner()

        print(
            f"{BOLD}{WHITE}"
            "TEAM MAIL / TEMP MAIL"
            f"{RESET}\n"
        )

        show_current_mail()

        print()

        print(
            f"{CYAN}[1]{RESET} "
            "Generate New Temporary Email"
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
            "Delete Current Mailbox"
        )

        print(
            f"{CYAN}[5]{RESET} "
            "Generate Another Email"
        )

        print(
            f"{CYAN}[0]{RESET} "
            "Back"
        )

        print()

        choice = input(
            f"{BOLD}Team Mail > {RESET}"
        ).strip()

        if choice == "1":

            create_temp_mail()
            pause()

        elif choice == "2":

            refresh_inbox()

        elif choice == "3":

            read_message()

        elif choice == "4":

            delete_temp_mailbox()

        elif choice == "5":

            create_temp_mail()
            pause()

        elif choice == "0":

            break

        else:

            error(
                "Invalid option."
            )

            time.sleep(1)


# ============================================================
# RDAP DOMAIN LOOKUP
# ============================================================

def get_rdap_server(domain):

    tld = domain.split(".")[-1].lower()

    bootstrap_url = (
        "https://data.iana.org/rdap/dns.json"
    )

    try:

        _, data = http_get_json(
            bootstrap_url
        )

        for service in data.get(
            "services",
            []
        ):

            if not service or len(service) < 2:
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
        return None

    return None


def format_rdap_date(value):

    if not value:
        return "Not available"

    try:

        parsed = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00"
            )
        )

        return parsed.strftime(
            "%Y-%m-%d"
        )

    except Exception:

        return (
            value[:10]
            if len(value) >= 10
            else value
        )


def extract_event(events, event_name):

    for event in events or []:

        if event.get(
            "eventAction"
        ) == event_name:

            return format_rdap_date(
                event.get(
                    "eventDate"
                )
            )

    return "Not available"


def extract_registrar(entities):

    for entity in entities or []:

        roles = entity.get(
            "roles",
            []
        )

        if "registrar" not in roles:
            continue

        vcard = entity.get(
            "vcardArray",
            []
        )

        if (
            isinstance(vcard, list)
            and len(vcard) > 1
        ):

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

    print()

    info(
        f"Looking up registration data "
        f"for {domain}..."
    )

    rdap_server = get_rdap_server(
        domain
    )

    if not rdap_server:

        error(
            "No RDAP server found."
        )

        pause()
        return

    rdap_url = (
        f"{rdap_server}/domain/"
        f"{urllib.parse.quote(domain)}"
    )

    try:

        status_code, data = http_get_json(
            rdap_url
        )

        statuses = data.get(
            "status",
            []
        )

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
            f"{BOLD}{WHITE}"
            "DOMAIN INFORMATION"
            f"{RESET}"
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
            f"Registration    : "
            f"{registration_date}"
        )

        print(
            f"Expiration      : "
            f"{expiration_date}"
        )

        print(
            f"Last Updated    : "
            f"{updated_date}"
        )

        print(
            f"Registrar       : "
            f"{registrar}"
        )

        print(
            f"RDAP Server     : "
            f"{rdap_server}"
        )

        print(
            "\nDomain Status:"
        )

        if statuses:

            for status in statuses:
                print(
                    f"  • {status}"
                )

        else:

            print(
                "  Not available"
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
# DNS LOOKUP
# ============================================================

def doh_query(name, record_type):

    encoded_name = urllib.parse.quote(
        name
    )

    url = (
        "https://cloudflare-dns.com/dns-query"
        f"?name={encoded_name}"
        f"&type={record_type}"
    )

    request = urllib.request.Request(
        url,
        headers={
            "Accept":
                "application/dns-json",
            "User-Agent":
                "SignalLab/3.0"
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


def get_dns_records(
    name,
    record_type
):

    try:

        data = doh_query(
            name,
            record_type
        )

        answers = data.get(
            "Answer",
            []
        )

        records = []

        for answer in answers:

            value = answer.get(
                "data"
            )

            if value:
                records.append(
                    value
                )

        return records

    except Exception:

        return []


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
            time.perf_counter()
            - start
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
            f"  Lookup time : "
            f"{elapsed:.2f} ms"
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
        f"System        : "
        f"{platform.system()}"
    )

    print(
        f"Release       : "
        f"{platform.release()}"
    )

    print(
        f"Machine       : "
        f"{platform.machine()}"
    )

    print(
        f"Python        : "
        f"{platform.python_version()}"
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

    print(
        f"\n{BOLD}HOST INFORMATION{RESET}"
    )

    try:

        fqdn = socket.getfqdn()

        print(
            f"FQDN          : {fqdn}"
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
# HTTP API TESTER
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
        (
            "http://",
            "https://"
        )
    ):

        error(
            "URL must start with "
            "http:// or https://"
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
                time.perf_counter()
                - start
            ) * 1000

            print()

            success(
                "Request completed."
            )

            print(
                f"Status        : "
                f"{response.status}"
            )

            print(
                f"Response time : "
                f"{elapsed:.2f} ms"
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
            f"Connection failed: "
            f"{exc.reason}"
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
                time.perf_counter()
                - start
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
            f"Connectivity test: "
            f"{host}:443"
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

    if not os.path.exists(
        LOG_FILE
    ):

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
        "network, domain and mail "
        "intelligence toolkit."
    )

    print()
    print(
        "Features:"
    )

    print(
        "  • Domain registration lookup"
    )

    print(
        "  • Temporary email mailbox"
    )

    print(
        "  • Inbox refresh and reader"
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
        "  • Local logging"
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
        "Temporary Mail API:"
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
            "Team Mail / Temp Mail"
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
