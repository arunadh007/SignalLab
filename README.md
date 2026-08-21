# 📡 SignalLab

> A lightweight and modular Python toolkit for domain intelligence, network diagnostics, disposable inbox testing, synthetic identity generation, and developer-focused research.

SignalLab is designed for developers, testers, students, and security researchers who need a simple command-line toolkit for authorized testing, network diagnostics, domain research, and synthetic test-data generation.

---

## ✨ Features

- 🔎 Domain Investigator
- 📧 Disposable Inbox
- 🌐 DNS / Host Lookup
- 🖥️ Network Information
- 👤 Synthetic Identity Generator
- ⚡ TCP Connectivity Testing
- 📝 Local Activity Logging
- 🎨 Clean command-line interface
- 🐧 Linux support
- 📱 Termux support
- 🪟 Windows support
- 🐍 Built with Python
- 🌍 Cross-platform support
- 🔒 Designed for authorized testing

---

## 🛠️ Requirements

- Python 3.8 or newer
- Linux, Termux, or Windows
- Git
- Internet connection for online features

SignalLab primarily uses Python standard-library modules.

The Identity Generator uses the Random User API for synthetic test data.

---

## 🚀 Installation

### Clone the Repository

```bash
git clone https://github.com/arunadh007/SignalLab.git
cd SignalLab
```

### Run SignalLab

```bash
python signal_lab.py
```

If your system uses the Python launcher:

```bash
py signal_lab.py
```

On Linux:

```bash
python3 signal_lab.py
```

---

## 📱 Termux Installation

### 1. Install Git and Python

```bash
pkg update
pkg install git python
```

### 2. Clone SignalLab

```bash
git clone https://github.com/arunadh007/SignalLab.git
cd SignalLab
```

### 3. Start SignalLab

```bash
python signal_lab.py
```

---

## 🐧 Linux

### 1. Install Git and Python

```bash
sudo apt update
sudo apt install git python3
```

### 2. Clone the Repository

```bash
git clone https://github.com/arunadh007/SignalLab.git
cd SignalLab
```

### 3. Run SignalLab

```bash
python3 signal_lab.py
```

---

## 🪟 Windows

Install Python and Git, then open **PowerShell** or **Command Prompt**.

### Clone the Repository

```powershell
git clone https://github.com/arunadh007/SignalLab.git
cd SignalLab
```

### Run SignalLab

```powershell
python signal_lab.py
```

If `python` is unavailable:

```powershell
py signal_lab.py
```

---

## 🧰 Available Tools

| Option | Tool | Description |
|--------|------|-------------|
| `1` | 🔎 Domain Investigator | Looks up public domain registration and RDAP information |
| `2` | 📧 Disposable Inbox | Creates and checks a temporary development mailbox |
| `3` | 🌐 DNS / Host Lookup | Resolves hostnames and displays IPv4 addresses |
| `4` | 🖥️ Network Information | Displays local system and network information |
| `5` | 👤 Identity Generator | Generates synthetic test identity data |
| `6` | ⚡ Connectivity Test | Checks TCP connectivity on port 443 |
| `7` | 📝 View Logs | Displays SignalLab activity logs |
| `8` | ℹ️ About SignalLab | Shows project information |
| `0` | 🚪 Exit | Closes SignalLab |

---

## 🎨 Interface

```text
   _____ _                   _  _      _          _
  / ____(_)                 | || |    | |        | |
 | (___  _  __ _ _ __   __ _| || |    | |     ___| |__
  \___ \| |/ _` | '_ \ / _` | || |_   | |    / _ \ '_ \
  ____) | | (_| | | | | (_| |__   _|  | |___|  __/ |_) |
 |_____/|_|\__, |_| |_|_|\__,_|  |_|    |______\___|_.__/
             __/ |
            |___/

Network, Domain, Mail & OSINT Toolkit
Version 4.0.0

[1] Domain Investigator
[2] Disposable Inbox
[3] DNS / Host Lookup
[4] Network Information
[5] Identity Generator
[6] Connectivity Test
[7] View Logs
[8] About SignalLab
[0] Exit

SignalLab >
```

---

## 🔎 Domain Investigator

Domain Investigator retrieves publicly available RDAP registration information for a domain.

### Example

```text
SignalLab > 1

DOMAIN INVESTIGATOR

Enter domain: example.com

[*] Looking up registration data...

DOMAIN INFORMATION
--------------------------------

Domain       : example.com
Status       : Registered
Registration : YYYY-MM-DD
Expiration   : YYYY-MM-DD
Last Updated : YYYY-MM-DD
Registrar    : Example Registrar
RDAP Server  : https://...

Domain Status:
  • active

Name Servers:
  • example.ns.cloudflare.com
  • example2.ns.cloudflare.com
```

### Information Available

- Domain name
- Registration date
- Expiration date
- Last updated date
- Registrar
- RDAP server
- Domain status
- Name servers

Only publicly available registration information is used.

---

## 📧 Disposable Inbox

The Disposable Inbox module provides a temporary mailbox for development and testing workflows.

### Features

- Generate disposable email address
- Refresh inbox
- View received messages
- Delete mailbox
- Maintain local mailbox session

### Example

```text
DISPOSABLE INBOX

Address : example123@temporary-domain.com

[1] Generate New Disposable Email
[2] Refresh Inbox
[3] Read Message
[4] Delete Mailbox
[5] Generate Another Address
[0] Back
```

Use disposable mailboxes only for legitimate testing and development purposes.

---

## 🌐 DNS / Host Lookup

Resolve a hostname and display its IPv4 address.

### Example

```text
SignalLab > 3

DNS / HOST LOOKUP

Enter hostname: example.com

[+] DNS lookup successful.

Host        : example.com
IPv4 #1     : 93.184.216.34
Lookup time : 25.42 ms
```

Useful for DNS troubleshooting, connectivity diagnostics, and development testing.

---

## 🖥️ Network Information

Displays basic information about the local system and network environment.

### Example

```text
NETWORK INFORMATION

SYSTEM

Hostname      : Arun-PC
System        : Windows
Release       : 11
Machine       : AMD64
Python        : 3.x.x

NETWORK

Local IP      : 192.168.x.x
Public IPv4   : xxx.xxx.xxx.xxx
FQDN          : Arun-PC
```

The module is intended for local diagnostics and development.

---

## 👤 Identity Generator

SignalLab includes a synthetic identity generator for application development and testing.

The generator uses the Random User API to retrieve randomly generated test identities.

### Available Options

```text
IDENTITY GENERATOR

[1] Generate Random Identity
[2] Generate US Identity
[3] Generate Indian Identity
[4] Generate UK Identity
[5] Choose Nationality
[6] Choose Gender
[7] Generate Multiple Identities
[0] Back
```

### Example Output

```text
GENERATED TEST IDENTITY
================================

Name         : Example User
Gender       : Female
Country      : United States

Address      : 123 Example Street
City         : Austin
State        : Texas
ZIP/Postcode : 78701

Email        : example@example.com
Phone        : (000) 000-0000
Mobile       : (000) 000-0000

Date of Birth: 1994-07-18
Age          : 30
Username     : example_user
Nationality  : US

Picture      : https://...

================================

⚠ SYNTHETIC TEST DATA
For software testing and development.
```

### Supported Nationalities

- 🇺🇸 United States
- 🇮🇳 India
- 🇬🇧 United Kingdom
- 🇨🇦 Canada
- 🇦🇺 Australia
- 🇩🇪 Germany
- 🇫🇷 France
- 🌍 Random

The generated information is synthetic test data and should not be treated as the identity of a real person.

---

## ⚡ Connectivity Test

Tests TCP connectivity to port `443`.

### Example

```text
SignalLab > 6

CONNECTIVITY TEST

Enter host (example.com): example.com

[+] TCP connectivity available.

Host : example.com
Port : 443
Time : 42.31 ms
```

Useful for basic connectivity troubleshooting and authorized diagnostics.

---

## 📝 Logging

SignalLab automatically records local activity in:

```text
signallab.log
```

Example:

```text
[2026-08-21 12:00:00] DNS lookup: example.com
[2026-08-21 12:01:20] Domain Investigator: example.com
[2026-08-21 12:02:10] Identity Generator: 1 synthetic identities generated.
```

The log file is generated automatically when SignalLab is used.

---

## 📂 Project Structure

```text
SignalLab/
├── signal_lab.py
├── requirements.txt
├── .gitignore
├── LICENSE
├── README.md
└── signallab.log
```

> `signallab.log` is generated automatically when SignalLab is used.

---

## 🔐 Responsible Use

SignalLab is intended for:

- Educational purposes
- Software development
- Network diagnostics
- Domain research
- Authorized security testing
- Local experimentation
- Synthetic test-data generation

Only test systems, services, APIs, domains, and resources that you own or have explicit permission to test.

SignalLab should not be used to:

- Access accounts without authorization
- Collect private personal information
- Bypass authentication
- Intercept third-party verification codes
- Disrupt services
- Conduct unauthorized security testing

Users are responsible for complying with applicable laws, service policies, and authorization requirements.

---

## 🧪 Development

SignalLab is written in Python and is designed to remain lightweight, portable, and easy to extend.

Most modules use Python's standard library. Online features use public APIs and RDAP services where applicable.

---

## 🗺️ Roadmap

- [x] Command-line interface
- [x] Domain Investigator
- [x] RDAP domain lookup
- [x] DNS / hostname lookup
- [x] Network information
- [x] TCP connectivity testing
- [x] Local logging
- [x] Disposable Inbox
- [x] Synthetic Identity Generator
- [x] Multiple identity generation
- [ ] Modular plugin system
- [ ] Configuration system
- [ ] JSON output mode
- [ ] Export test data
- [ ] Advanced network diagnostics
- [ ] Automated diagnostic reports

---

## 🤝 Contributing

Contributions, suggestions, bug reports, and improvements are welcome.

Before submitting a change:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Test the changes locally.
5. Submit a pull request.

Please keep contributions focused, documented, and respectful of the project's responsible-use policy.

---

## 📦 Version

```text
SignalLab v4.0.0
```

---

## 📄 License

SignalLab is released under the **MIT License**.

See the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Arun Adhikari**

GitHub: https://github.com/arunadh007

---

## ⭐ Support

If you find SignalLab useful, consider giving the repository a ⭐ star and sharing it with other developers.

---

<div align="center">

### 📡 SignalLab

**Simple tools. Clean testing. Better diagnostics.**

Made with ❤️ using Python.

</div>
