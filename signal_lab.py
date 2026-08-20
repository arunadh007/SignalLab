#!/usr/bin/env python3

import json
import os
import platform
import socket
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

APP_NAME = "SignalLab"
VERSION = "1.0.0"
LOG_FILE = "signallab.log"

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
WHITE = "\033[97m"


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
{WHITE}Network & API Testing Toolkit{RESET}
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


def validate_phone():
    clear_screen()
    banner()

    print(f"{BOLD}{WHITE}PHONE NUMBER VALIDATOR{RESET}\n")

    number = input("Enter phone number: ").strip()

    if not number:
        error("No phone number entered.")
        pause()
        return

    cleaned = number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

    if cleaned.startswith("+"):
        digits = cleaned[1:]
    else:
        digits = cleaned

    if digits.isdigit() and 7 <= len(digits) <= 15:
        success("Number format looks valid.")
        print(f"\n  Number : {number}")
        print(f"  Digits : {len(digits)}")
        print("  Format : International/local numeric format")
    else:
        error("Invalid phone number format.")

    pause()


def dns_lookup():
    clear_screen()
    banner()

    print(f"{BOLD}{WHITE}DNS / HOST LOOKUP{RESET}\n")

    hostname = input("Enter hostname: ").strip()

    if not hostname:
        error("Hostname cannot be empty.")
        pause()
        return

    try:
        ip_address = socket.gethostbyname(hostname)

        print()
        success("DNS lookup successful.")
        print(f"  Host : {hostname}")
        print(f"  IPv4 : {ip_address}")

    except socket.gaierror:
        error("Unable to resolve hostname.")

    pause()


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

    print(f"\n{YELLOW}Testing endpoint...{RESET}\n")

    start = time.perf_counter()

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "SignalLab/1.0"
            }
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            elapsed = (time.perf_counter() - start) * 1000

            status = response.status
            content_type = response.headers.get("Content-Type", "Unknown")

            success("Request completed.")

            print(f"  Status       : {status}")
            print(f"  Response time: {elapsed:.2f} ms")
            print(f"  Content-Type : {content_type}")

            write_log(
                f"API test: {url} | status={status} | "
                f"time={elapsed:.2f}ms"
            )

    except urllib.error.HTTPError as exc:
        elapsed = (time.perf_counter() - start) * 1000
        error(f"HTTP error: {exc.code}")
        print(f"  Response time: {elapsed:.2f} ms")

    except urllib.error.URLError as exc:
        error(f"Connection failed: {exc.reason}")

    except Exception as exc:
        error(f"Unexpected error: {exc}")

    pause()


def connectivity_test():
    clear_screen()
    banner()

    print(f"{BOLD}{WHITE}CONNECTIVITY TEST{RESET}\n")

    host = input("Enter host (example.com): ").strip()

    if not host:
        error("Host cannot be empty.")
        pause()
        return

    print()

    try:
        start = time.perf_counter()

        socket.create_connection((host, 443), timeout=5)

        elapsed = (time.perf_counter() - start) * 1000

        success("TCP connectivity available.")
        print(f"  Host : {host}")
        print(f"  Port : 443")
        print(f"  Time : {elapsed:.2f} ms")

        write_log(
            f"Connectivity test: {host}:443 | {elapsed:.2f}ms"
        )

    except OSError as exc:
        error(f"Connection failed: {exc}")

    pause()


def show_logs():
    clear_screen()
    banner()

    print(f"{BOLD}{WHITE}SIGNALLAB LOGS{RESET}\n")

    if not os.path.exists(LOG_FILE):
        info("No logs available yet.")
        pause()
        return

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            content = file.read()

        if content.strip():
            print(content)
        else:
            info("Log file is empty.")

    except OSError as exc:
        error(f"Unable to read logs: {exc}")

    pause()


def about():
    clear_screen()
    banner()

    print(f"{BOLD}{WHITE}ABOUT SIGNAL LAB{RESET}\n")

    print("SignalLab is a lightweight Python toolkit")
    print("for network diagnostics and authorized API testing.")
    print()
    print("Features:")
    print("  • Phone number format validation")
    print("  • DNS / hostname lookup")
    print("  • Network information")
    print("  • HTTP/API response testing")
    print("  • TCP connectivity testing")
    print("  • Local activity logging")
    print()
    print("Designed for developers, testers and learning.")
    print()
    print(f"Version : {VERSION}")
    print("Author  : arunadh007")
    print("License : MIT")

    pause()


def main_menu():
    while True:
        clear_screen()
        banner()

        print(f"{BOLD}{WHITE}MAIN MENU{RESET}\n")

        print(f"{CYAN}[1]{RESET} Phone Number Validator")
        print(f"{CYAN}[2]{RESET} DNS / Host Lookup")
        print(f"{CYAN}[3]{RESET} Network Information")
        print(f"{CYAN}[4]{RESET} HTTP / API Tester")
        print(f"{CYAN}[5]{RESET} Connectivity Test")
        print(f"{CYAN}[6]{RESET} View Logs")
        print(f"{CYAN}[7]{RESET} About SignalLab")
        print(f"{RED}[0]{RESET} Exit")

        print()
        choice = input(f"{BOLD}SignalLab > {RESET}").strip()

        if choice == "1":
            validate_phone()

        elif choice == "2":
            dns_lookup()

        elif choice == "3":
            network_info()

        elif choice == "4":
            api_test()

        elif choice == "5":
            connectivity_test()

        elif choice == "6":
            show_logs()

        elif choice == "7":
            about()

        elif choice == "0":
            clear_screen()
            print(f"\n{GREEN}Thanks for using SignalLab! 👋{RESET}\n")
            sys.exit(0)

        else:
            error("Invalid option.")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}SignalLab stopped by user.{RESET}\n")
        sys.exit(0)
