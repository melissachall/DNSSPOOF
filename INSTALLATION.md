# Installation Guide - DNS Spoof MITM

## Prerequisites

### Operating System Requirements
- **Kali Linux 2023.x+** (Recommended)
- **Parrot OS 5.x+**
- **Ubuntu 20.04+ with security tools**

### Hardware Requirements
- CPU: 2 cores minimum
- RAM: 2 GB minimum
- Network: Ethernet adapter (Wi-Fi adapters may have limitations)

---

## Step-by-Step Installation

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install System Dependencies

```bash
# Install NetfilterQueue library
sudo apt install -y libnetfilter-queue-dev

# Install Python3 NetfilterQueue
sudo apt install -y python3-netfilterqueue

# Install network tools
sudo apt install -y dsniff arpspoof tcpdump net-tools

# Install development tools (if needed)
sudo apt install -y python3-pip python3-dev build-essential
```

### 3. Install Python Dependencies

**Option A: System-wide (not recommended)**
```bash
sudo pip3 install scapy NetfilterQueue
```

**Option B: Virtual Environment (recommended)**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install scapy NetfilterQueue
```

### 4. Download the Tool

```bash
# Clone repository
git clone https://github.com/melissachall/DNS-Spoof-MITM.git
cd DNS-Spoof-MITM

# Or download ZIP and extract
wget https://github.com/melissachall/DNS-Spoof-MITM/archive/main.zip
unzip main.zip
cd DNS-Spoof-MITM-main
```

### 5. Verify Installation

```bash
# Test imports
python3 -c "from scapy.all import *; print('Scapy OK')"
python3 -c "from netfilterqueue import NetfilterQueue; print('NetfilterQueue OK')"

# Check iptables
sudo iptables --version

# Check arpspoof
arpspoof 2>&1 | head -n 1
```

### 6. Enable IP Forwarding

**Temporary (until reboot):**
```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

**Permanent:**
```bash
# Edit sysctl.conf
sudo nano /etc/sysctl.conf

# Add or uncomment this line:
net.ipv4.ip_forward=1

# Apply changes
sudo sysctl -p
```

### 7. Test Run

```bash
# Make script executable
chmod +x dnsspoof.py

# Test script execution (won't spoof without ARP poisoning)
sudo python3 dnsspoof.py --help
```

**Expected Output:**
```
usage: dnsspoof.py [-h] [--spoof SPOOF] [--debug] [--json JSON]

DNS Spoof MITM (lab robust version)

optional arguments:
  -h, --help     show this help message and exit
  --spoof SPOOF  IP à laquelle rediriger les domaines spoofés
  --debug        Active le mode debug (logs détaillés)
  --json JSON    Fichier JSON de mapping DNS ('domain': 'ip')
```

---

## Troubleshooting Installation

### Issue: NetfilterQueue Import Error

```bash
ImportError: No module named 'netfilterqueue'
```

**Solution:**
```bash
# Install system package first
sudo apt install python3-netfilterqueue libnetfilter-queue-dev

# Then try pip
sudo pip3 install NetfilterQueue

# If still failing, install from source:
git clone https://github.com/oremanj/python-netfilterqueue
cd python-netfilterqueue
sudo python3 setup.py install
```

### Issue: Scapy Permission Error

```bash
PermissionError: [Errno 1] Operation not permitted
```

**Solution:**
```bash
# Always run with sudo for network operations
sudo python3 dnsspoof.py
```

### Issue: iptables Command Not Found

```bash
sudo apt install iptables
```

### Issue: arpspoof Not Found

```bash
sudo apt install dsniff

# If dsniff unavailable:
sudo apt install ettercap-text-only
# Use: sudo ettercap -T -M arp:remote /<victim_ip>/ /<gateway_ip>/
```

### Issue: "Cannot open shared object file"

```bash
error while loading shared libraries: libnetfilter_queue.so.1
```

**Solution:**
```bash
# Update library cache
sudo ldconfig

# If still failing, reinstall
sudo apt remove libnetfilter-queue1 libnetfilter-queue-dev
sudo apt install libnetfilter-queue1 libnetfilter-queue-dev
```

### Issue: Python3 Not Default

```bash
# Create alias (add to ~/.bashrc)
alias python=python3
alias pip=pip3

# Or use update-alternatives
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1
```

---

## Post-Installation Configuration

### 1. Create Custom Domain Mapping (Optional)

```bash
# Copy example
cp domains.json.example domains.json

# Edit with your targets
nano domains.json
```

Example `domains.json`:
```json
{
    "www.example.com.": "192.168.1.10",
    "example.com.": "192.168.1.10"
}
```

### 2. Configure Network Interface

```bash
# Find your network interface
ip addr show

# Common names: eth0, ens33, wlan0

# Set interface in script or use it in arpspoof commands
```

### 3. Test Network Connectivity

```bash
# Ping gateway
ping -c 4 192.168.1.1

# Ping victim (if known)
ping -c 4 192.168.1.20

# Test DNS resolution
nslookup google.com
```

---

## Verification Checklist

Run through this checklist before your first test:

- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] Scapy installed (`python3 -c "import scapy"`)
- [ ] NetfilterQueue installed (`python3 -c "import netfilterqueue"`)
- [ ] iptables installed (`sudo iptables --version`)
- [ ] dsniff/arpspoof installed (`which arpspoof`)
- [ ] IP forwarding enabled (`cat /proc/sys/net/ipv4/ip_forward` returns `1`)
- [ ] Root/sudo access working (`sudo -v`)
- [ ] Network interface identified (`ip addr show`)
- [ ] Script executable (`ls -l dnsspoof.py` shows `x` permission)
- [ ] Help command works (`sudo python3 dnsspoof.py --help`)

---

## Virtual Lab Setup (Recommended)

### VirtualBox Configuration

```bash
# Install VirtualBox on host
# Download from: https://www.virtualbox.org/

# Create VMs:
# 1. Kali Linux (Attacker)
#    - Network: Internal Network "lab_network"
#    - Adapter Type: PCnet-FAST III
#
# 2. Windows 10 (Victim)
#    - Network: Internal Network "lab_network"
#    - Adapter Type: PCnet-FAST III
#
# 3. pfSense/Router (Gateway)
#    - Adapter 1: NAT (Internet)
#    - Adapter 2: Internal Network "lab_network"
```

### Network Configuration in VMs

**Kali Linux:**
```bash
sudo nano /etc/network/interfaces

# Add:
auto eth0
iface eth0 inet static
    address 192.168.1.10
    netmask 255.255.255.0
    gateway 192.168.1.1
    dns-nameservers 8.8.8.8 1.1.1.1

# Restart networking
sudo systemctl restart networking
```

**Windows Victim:**
```
Control Panel → Network → Change Adapter Settings
Right-click Ethernet → Properties → IPv4
Set:
  IP: 192.168.1.20
  Mask: 255.255.255.0
  Gateway: 192.168.1.1
  DNS: 8.8.8.8
```

---

## Security Recommendations

1. **Use Isolated Lab Only**
   - Never connect lab network to production
   - Use Internal/Host-Only networking in VMs
   - Take VM snapshots before testing

2. **Document Everything**
   - Keep logs of all activities
   - Note timestamps
   - Screenshot configurations

3. **Clean Up After Testing**
   - Remove iptables rules
   - Stop ARP spoofing
   - Revert VM snapshots

---

## Next Steps

1. ✅ Review `README.md` for usage instructions
2. ✅ Read attack workflow documentation
3. ✅ Set up virtual lab environment
4. ✅ Test ARP spoofing separately first
5. ✅ Run DNS spoof with `--debug` flag
6. ✅ Review legal/ethical guidelines

---

## Quick Start Command Summary

```bash
# Complete installation in one go (Kali Linux)
sudo apt update
sudo apt install -y libnetfilter-queue-dev python3-netfilterqueue dsniff tcpdump
pip3 install scapy NetfilterQueue
sudo sysctl -w net.ipv4.ip_forward=1
git clone https://github.com/melissachall/DNS-Spoof-MITM.git
cd DNS-Spoof-MITM
chmod +x dnsspoof.py
sudo python3 dnsspoof.py --help
```

---

**Installation Date:** 2025-11-23  
**Last Updated:** 2025-11-23  
**Version:** 1.0
