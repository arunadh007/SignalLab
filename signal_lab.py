#!/usr/bin/env python3

import json
import os
import platform
import random
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime


APP_NAME = "SignalLab"
VERSION = "4.0.0"
LOG_FILE = "signallab.log"

API_URL = "https://randomuser.me/api/"

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
    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    try:
        with open(
            LOG_FILE,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                f"[{timestamp}] {message}\n"
            )

    except OSError:
        pass


def success(message):
    print(
        f"{GREEN}[+] {message}{RESET}"
    )

    write_log(message)


def error(message):
    print(
        f"{RED}[!] {message}{RESET}"
    )

    write_log(
        f"ERROR: {message}"
    )


def info(message):
    print(
        f"{BLUE}[*] {message}{RESET}"
    )


# ============================================================
# HTTP / API
# ============================================================

def api_get(url, timeout=20):

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent":
            "SignalLab/4.0"
        }
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

            return json.loads(raw)

    except urllib.error.HTTPError as exc:

        raise RuntimeError(
            f"HTTP error {exc.code}"
        )

    except urllib.error.URLError as exc:

        raise RuntimeError(
            f"Network error: {exc.reason}"
        )

    except json.JSONDecodeError:

        raise RuntimeError(
            "API returned invalid JSON."
        )


# ============================================================
# DOMAIN
# ============================================================

def normalize_domain(domain):

    domain = domain.strip().lower()

    if "://" in domain:

        parsed = urllib.parse.urlparse(
            domain
        )

        domain = parsed.hostname or ""

    domain = domain.split("/")[0]
    domain = domain.split(":")[0]

    return domain.rstrip(".")


def valid_domain(domain):

    pattern = (
        r"^(?=.{1,253}$)"
        r"(?:[a-z0-9]"
        r"(?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
        r"[a-z]{2,63}$"
    )

    return bool(
        re.match(
            pattern,
            domain,
            re.I
        )
    )


def get_rdap_server(domain):

    tld = domain.split(
        "."
    )[-1].lower()

    try:

        data = api_get(
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

        return datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00"
            )
        ).strftime(
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
                event.get(
                    "eventDate"
                )
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


def domain_investigator():

    clear_screen()
    banner()

    print(
        f"{BOLD}{WHITE}"
        "DOMAIN INVESTIGATOR"
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

        server = get_rdap_server(
            domain
        )

        if not server:

            error(
                "No RDAP server found."
            )

            pause()
            return

        url = (
            f"{server}/domain/"
            f"{urllib.parse.quote(domain)}"
        )

        data = api_get(url)

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

        print()

        print(
            f"{BOLD}DOMAIN INFORMATION{RESET}"
        )

        print(
            "--------------------------------"
        )

        print(
            f"Domain       : {domain}"
        )

        print(
            "Status       : Registered"
        )

        print(
            f"Registration : {registration}"
        )

        print(
            f"Expiration   : {expiration}"
        )

        print(
            f"Last Updated : {updated}"
        )

        print(
            f"Registrar    : {registrar}"
        )

        print(
            f"RDAP Server  : {server}"
        )

        print(
            "\nDomain Status:"
        )

        statuses = data.get(
            "status",
            []
        )

        for status in statuses:

            print(
                f"  • {status}"
            )

        print(
            "\nName Servers:"
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

        if nameservers:

            for ns in nameservers:

                print(
                    f"  • {ns}"
                )

        else:

            print(
                "  Not available"
            )

        write_log(
            f"Domain Investigator: {domain}"
        )

    except Exception as exc:

        error(
            f"Domain lookup failed: {exc}"
        )

    pause()


# ============================================================
# DNS
# ============================================================

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

        results = socket.getaddrinfo(
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
                for item in results
            )
        )

        success(
            "DNS lookup successful."
        )

        print(
            f"\nHost        : {hostname}"
        )

        for index, ip in enumerate(
            ips,
            1
        ):

            print(
                f"IPv4 #{index}  : {ip}"
            )

        print(
            f"Lookup time : {elapsed:.2f} ms"
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

    except Exception:

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

    print(
        f"FQDN          : {socket.getfqdn()}"
    )

    write_log(
        "Displayed network information."
    )

    pause()


# ============================================================
# IDENTITY GENERATOR
# ============================================================

NATIONALITIES = {
    "1": ("United States", "us"),
    "2": ("India", "in"),
    "3": ("United Kingdom", "gb"),
    "4": ("Canada", "ca"),
    "5": ("Australia", "au"),
    "6": ("Germany", "de"),
    "7": ("France", "fr"),
    "8": ("Random", None),
}


def generate_identity(
    nationality=None,
    gender=None,
    results=1
):

    params = {
        "results": results,
        "inc": (
            "gender,name,location,email,"
            "login,dob,phone,cell,picture,nat"
        )
    }

    if nationality:

        params["nat"] = nationality

    if gender in (
        "male",
        "female"
    ):

        params["gender"] = gender

    query = urllib.parse.urlencode(
        params
    )

    url = (
        f"{API_URL}?{query}"
    )

    return api_get(url)


def print_identity(user, number=None):

    if number is not None:

        print(
            f"\n{BOLD}{CYAN}"
            f"IDENTITY #{number}"
            f"{RESET}"
        )

    else:

        print(
            f"\n{BOLD}{CYAN}"
            "GENERATED TEST IDENTITY"
            f"{RESET}"
        )

    print(
        "================================"
    )

    name = user.get(
        "name",
        {}
    )

    location = user.get(
        "location",
        {}
    )

    street = location.get(
        "street",
        {}
    )

    dob = user.get(
        "dob",
        {}
    )

    print(
        f"Name         : "
        f"{name.get('title', '')} "
        f"{name.get('first', '')} "
        f"{name.get('last', '')}"
    )

    print(
        f"Gender       : "
        f"{user.get('gender', 'Unknown').title()}"
    )

    print(
        f"Country      : "
        f"{location.get('country', 'Unknown')}"
    )

    print(
        f"Address      : "
        f"{street.get('number', '')} "
        f"{street.get('name', '')}"
    )

    print(
        f"City         : "
        f"{location.get('city', 'Unknown')}"
    )

    print(
        f"State        : "
        f"{location.get('state', 'Unknown')}"
    )

    print(
        f"ZIP/Postcode : "
        f"{location.get('postcode', 'Unknown')}"
    )

    print(
        f"Email        : "
        f"{user.get('email', 'Unknown')}"
    )

    print(
        f"Phone        : "
        f"{user.get('phone', 'Unknown')}"
    )

    print(
        f"Mobile       : "
        f"{user.get('cell', 'Unknown')}"
    )

    print(
        f"Date of Birth: "
        f"{dob.get('date', 'Unknown')[:10]}"
    )

    print(
        f"Age          : "
        f"{dob.get('age', 'Unknown')}"
    )

    print(
        f"Username     : "
        f"{user.get('login', {}).get('username', 'Unknown')}"
    )

    print(
        f"Nationality  : "
        f"{user.get('nat', 'Unknown')}"
    )

    picture = user.get(
        "picture",
        {}
    )

    print(
        f"Picture      : "
        f"{picture.get('large', 'Unavailable')}"
    )

    print(
        "================================"
    )

    print(
        f"{YELLOW}"
        "⚠ SYNTHETIC TEST DATA"
        f"{RESET}"
    )

    print(
        "For software testing and development."
    )


def identity_generator():

    while True:

        clear_screen()
        banner()

        print(
            f"{BOLD}{WHITE}"
            "IDENTITY GENERATOR"
            f"{RESET}\n"
        )

        print(
            f"{CYAN}[1]{RESET} "
            "Generate Random Identity"
        )

        print(
            f"{CYAN}[2]{RESET} "
            "Generate US Identity"
        )

        print(
            f"{CYAN}[3]{RESET} "
            "Generate Indian Identity"
        )

        print(
            f"{CYAN}[4]{RESET} "
            "Generate UK Identity"
        )

        print(
            f"{CYAN}[5]{RESET} "
            "Choose Nationality"
        )

        print(
            f"{CYAN}[6]{RESET} "
            "Choose Gender"
        )

        print(
            f"{CYAN}[7]{RESET} "
            "Generate Multiple Identities"
        )

        print(
            f"{CYAN}[0]{RESET} "
            "Back"
        )

        print()

        choice = input(
            f"{BOLD}Identity Generator > {RESET}"
        ).strip()

        nationality = None
        gender = None
        count = 1

        if choice == "1":

            pass

        elif choice == "2":

            nationality = "us"

        elif choice == "3":

            nationality = "in"

        elif choice == "4":

            nationality = "gb"

        elif choice == "5":

            clear_screen()
            banner()

            print(
                f"{BOLD}SELECT NATIONALITY{RESET}\n"
            )

            for key, value in NATIONALITIES.items():

                print(
                    f"[{key}] {value[0]}"
                )

            print()

            nat_choice = input(
                "Select: "
            ).strip()

            if nat_choice not in NATIONALITIES:

                error(
                    "Invalid nationality."
                )

                pause()
                continue

            nationality = NATIONALITIES[
                nat_choice
            ][1]

        elif choice == "6":

            print()

            print(
                "[1] Male"
            )

            print(
                "[2] Female"
            )

            print(
                "[3] Random"
            )

            gender_choice = input(
                "Select gender: "
            ).strip()

            if gender_choice == "1":

                gender = "male"

            elif gender_choice == "2":

                gender = "female"

            elif gender_choice == "3":

                gender = None

            else:

                error(
                    "Invalid gender."
                )

                pause()
                continue

        elif choice == "7":

            try:

                count = int(
                    input(
                        "How many identities (1-20): "
                    ).strip()
                )

                if count < 1 or count > 20:

                    error(
                        "Choose between 1 and 20."
                    )

                    pause()
                    continue

            except ValueError:

                error(
                    "Please enter a number."
                )

                pause()
                continue

        elif choice == "0":

            break

        else:

            error(
                "Invalid option."
            )

            time.sleep(1)
            continue

        try:

            info(
                "Requesting synthetic identity data..."
            )

            data = generate_identity(
                nationality=nationality,
                gender=gender,
                results=count
            )

            users = data.get(
                "results",
                []
            )

            if not users:

                error(
                    "API returned no users."
                )

                pause()
                continue

            clear_screen()
            banner()

            for index, user in enumerate(
                users,
                1
            ):

                print_identity(
                    user,
                    index if count > 1 else None
                )

            write_log(
                f"Identity Generator: "
                f"{len(users)} synthetic identities generated."
            )

        except Exception as exc:

            error(
                f"Identity API failed: {exc}"
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
        "network, domain, mail and "
        "developer testing toolkit."
    )

    print()

    print(
        "Modules:"
    )

    print(
        "  • Domain Investigator"
    )

    print(
        "  • Disposable Inbox"
    )

    print(
        "  • DNS / Host Lookup"
    )

    print(
        "  • Network Information"
    )

    print(
        "  • Identity Generator"
    )

    print(
        "  • Connectivity Test"
    )

    print(
        "  • Local Activity Logs"
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
        "Identity Generator uses "
        "synthetic data for testing."
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
            "Domain Investigator"
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
            "Identity Generator"
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

            domain_investigator()

        elif choice == "2":

            # Existing Disposable Inbox
            # from your previous version.
            print(
                "\nDisposable Inbox module "
                "is available in your previous build."
            )

            print(
                "If you want it merged with this "
                "version, keep your existing "
                "Disposable Inbox functions."
            )

            pause()

        elif choice == "3":

            dns_lookup()

        elif choice == "4":

            network_info()

        elif choice == "5":

            identity_generator()

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
