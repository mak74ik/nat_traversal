# NATranslate (`nat_traversal`)

> **Zero-config P2P UDP hole punching & STUN NAT traversal CLI.**  
> Built and tested autonomously by **Auto Qwen AI**.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/mak74ik/nat_traversal/blob/main/LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## 🌟 Overview

`NATranslate` discovers external public IP addresses and mapped NAT ports via RFC 5389 STUN protocol and executes direct UDP hole punching between machines without requiring a public static IP or port forwarding.

---

## 🚀 Usage

### 1. Discover Public IP and Mapped Port via STUN
```bash
python3 main.py stun
```
Output:
```
[+] STUN Discovery Successful:
    Public IP:        176.124.139.136
    External Port:    61421
    Local Bound Port: 61421
```

### 2. Direct P2P Hole Punching Between Nodes
Node A and Node B exchange their STUN public IP/ports, then punch simultaneously:
```bash
# Node A
python3 main.py punch --local-port 61421 --peer-ip <NODE_B_PUBLIC_IP> --peer-port <NODE_B_PORT>
```

### 3. Listen for Direct P2P UDP Packets
```bash
python3 main.py listen --port 61421
```

---

## 🧪 Testing

Run automated end-to-end unit tests (STUN discovery + local UDP loopback hole punching):
```bash
python3 -m unittest discover -s tests
```

---

## 👥 Credits

Developed autonomously by **Auto Qwen AI**:
- 🤖 **Autonomous Engine**: Auto Qwen AI Pipeline
- 🌐 **Protocol**: RFC 5389 STUN Client + Asynchronous UDP Hole Punching
- 🛡️ **Quality Assurance**: Automated Socket Integration Tests
