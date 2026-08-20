# 📡 SignalLab

> A lightweight and modular Python toolkit for network diagnostics, API testing, connectivity checks, and developer-focused communication service testing.

SignalLab is designed for developers, testers, students, and security researchers who need a simple command-line toolkit for authorized testing and network diagnostics.

---

## ✨ Features

- 📱 Phone number format validation
- 🌐 DNS / hostname lookup
- 🖥️ System and network information
- 🔗 HTTP / API endpoint testing
- ⚡ TCP connectivity testing
- 📝 Local activity logging
- 🎨 Clean command-line interface
- 🐧 Linux support
- 📱 Termux support
- 🪟 Windows support
- 🐍 Built with Python
- 🔒 Designed for authorized testing

---

## 🛠️ Requirements

- Python 3.8 or newer
- Linux, Termux, or Windows
- Git

SignalLab currently uses only Python standard-library modules, so no external Python packages are required.

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

On Linux or some Termux installations:

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

Install Python and Git, then open **Command Prompt** or **PowerShell**.

### Clone the Repository

```powershell
git clone https://github.com/arunadh007/SignalLab.git
cd SignalLab
```

### Run SignalLab

```powershell
python signal_lab.py
```

---

## 🧰 Available Tools

| Option | Tool | Description |
|--------|------|-------------|
| `1` | Phone Number Validator | Checks basic phone number formatting |
| `2` | DNS / Host Lookup | Resolves a hostname to an IPv4 address |
| `3` | Network Information | Displays local system and network information |
| `4` | HTTP / API Tester | Tests an HTTP/HTTPS endpoint |
| `5` | Connectivity Test | Checks TCP connectivity on port 443 |
| `6` | View Logs | Displays SignalLab activity logs |
| `7` | About SignalLab | Shows project information |
| `0` | Exit | Closes SignalLab |

---

## 🎨 Interface

```text
   _____ _                   _  _      _          _
  / ____(_)                 | || |    | |        | |
 | (___  _  __ _ _ __   __ _| || |    | |     ___| |__
  \___ \| |/ _` | '_ \ / _` | || |_   | |    / _ \ '_ \
  ____) | | (_| | | | | (_| |__   _|  | |___|  __/ |_) |
 |_____/|_|\__, |_| |_|\__,_|  |_|    |______\___|_.__/
             __/ |
            |___/

Network & API Testing Toolkit
Version 1.0.0

[1] Phone Number Validator
[2] DNS / Host Lookup
[3] Network Information
[4] HTTP / API Tester
[5] Connectivity Test
[6] View Logs
[7] About SignalLab
[0] Exit

SignalLab >
```

---

## 🔍 Example Usage

### DNS Lookup

```text
SignalLab > 2

Enter hostname: example.com

[+] DNS lookup successful.

Host : example.com
IPv4 : 93.184.216.34
```

### API Testing

```text
SignalLab > 4

Enter URL: https://example.com

[*] Testing endpoint...

[+] Request completed.

Status        : 200
Response time : 123.45 ms
Content-Type  : text/html
```

### Connectivity Test

```text
SignalLab > 5

Enter host (example.com): example.com

[+] TCP connectivity available.

Host : example.com
Port : 443
Time : 45.32 ms
```

### Phone Number Validation

```text
SignalLab > 1

Enter phone number: +911234567890

[+] Number format looks valid.

Number : +911234567890
Digits : 12
Format : International/local numeric format
```

---

## 📝 Logging

SignalLab automatically records local testing activity in:

```text
signallab.log
```

Example:

```text
[2026-08-21 01:00:00] DNS lookup successful.
[2026-08-21 01:01:10] API test: https://example.com | status=200 | time=123.45ms
[2026-08-21 01:02:15] Connectivity test: example.com:443 | 45.32ms
```

The log file is generated automatically when SignalLab performs activities that create log entries.

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

> `signallab.log` is generated automatically when SignalLab is used and is excluded from Git tracking through `.gitignore`.

---

## 🔐 Responsible Use

SignalLab is intended for:

- Educational purposes
- Software development
- Network diagnostics
- API testing
- Authorized security testing
- Local experimentation

Only test systems, services, APIs, and resources that you own or have explicit permission to test.

SignalLab does **not** provide functionality for:

- SMS bombing
- Call bombing
- Unsolicited messaging
- Service disruption
- Unauthorized access
- Abuse of third-party services

Users are responsible for complying with applicable laws, service policies, and authorization requirements.

---

## 🧪 Development

SignalLab is written in Python and is designed to remain lightweight and dependency-free.

The project currently uses Python's standard library and does not require external packages.

Future versions may introduce additional diagnostic and testing modules while keeping the project simple, portable, and accessible.

---

## 🗺️ Roadmap

- [x] Command-line interface
- [x] Phone number validation
- [x] DNS / hostname lookup
- [x] Network information
- [x] HTTP / API testing
- [x] TCP connectivity testing
- [x] Local logging
- [ ] Modular plugin system
- [ ] Configuration system
- [ ] JSON output mode
- [ ] Advanced network diagnostics
- [ ] Automated test reports
- [ ] Improved error handling
- [ ] Cross-platform improvements

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
