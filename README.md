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

### Clone the repository

```bash
git clone https://github.com/arunadh007/SignalLab.git
cd SignalLab

Run SignalLab python signal_lab.py

On Linux or some Termux installations: python3 signal_lab.py

📱 Termux Installation

Install Git and Python: pkg update
pkg install git python

Clone SignalLab: git clone https://github.com/arunadh007/SignalLab.git
cd SignalLab

Start SignalLab: python signal_lab.py

🐧 Linux

Install Git and Python if they are not already installed: sudo apt update
sudo apt install git python3 

Clone the repository: git clone https://github.com/arunadh007/SignalLab.git
cd SignalLab 

Run: python3 signal_lab.py

🪟 Windows

Install Python and Git, then open Command Prompt or PowerShell:

git clone https://github.com/arunadh007/SignalLab.git
cd SignalLab
python signal_lab.py

| Option | Tool                   | Description                                   |
| ------ | ---------------------- | --------------------------------------------- |
| 1      | Phone Number Validator | Checks basic phone number formatting          |
| 2      | DNS / Host Lookup      | Resolves a hostname to an IPv4 address        |
| 3      | Network Information    | Displays local system and network information |
| 4      | HTTP / API Tester      | Tests an HTTP/HTTPS endpoint                  |
| 5      | Connectivity Test      | Checks TCP connectivity on port 443           |
| 6      | View Logs              | Displays SignalLab activity logs              |
| 7      | About SignalLab        | Shows project information                     |
| 0      | Exit                   | Closes SignalLab                              |


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

🔍 Example Usage
DNS Lookup

SignalLab > 2

Enter hostname: example.com

[+] DNS lookup successful.

Host : example.com
IPv4 : 93.184.216.34

API Testing 
SignalLab > 4

Enter URL: https://example.com

[*] Testing endpoint...

[+] Request completed.

Status        : 200
Response time : 123.45 ms
Content-Type  : text/html

📝 Logging

SignalLab automatically records local testing activity in: signallab.log

Example: [2026-08-21 01:00:00] DNS lookup successful.
[2026-08-21 01:01:10] API test: https://example.com | status=200 | time=123.45ms

📂 Project Structure

SignalLab/
├── signal_lab.py
├── requirements.txt
├── .gitignore
├── LICENSE
├── README.md
└── signallab.log

signallab.log is generated automatically when SignalLab is used.

🔐 Responsible Use

SignalLab is intended for:

Educational purposes
Software development
Network diagnostics
API testing
Authorized security testing
Local experimentation

Only test systems and services that you own or have explicit permission to test.

SignalLab does not provide SMS/call bombing, unsolicited messaging, or service-disruption functionality.

🧪 Development

SignalLab is written in Python and is designed to remain lightweight and dependency-free.

Future versions may introduce additional diagnostic and testing modules while keeping the project simple and accessible.

🗺️ Roadmap
 Command-line interface
 Phone number validation
 DNS lookup
 Network information
 HTTP/API testing
 TCP connectivity testing
 Local logging
 Modular plugin system
 Configuration system
 JSON output mode
 Advanced network diagnostics
 Automated test reports

 📄 License

SignalLab is released under the MIT License.

See the LICENSE file for details.

👤 Author

Arun Adhikari

GitHub: https://github.com/arunadh007

⭐ Support

If you find SignalLab useful, consider giving the repository a ⭐ star and sharing it with other developers.

SignalLab — Simple tools. Clean testing. Better diagnostics.



