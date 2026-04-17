# SDN-Project
# SDN-Based Access Control System

## Overview

This project implements an **SDN-based access control system** using the Ryu controller and Mininet.
The system ensures that **only authorized hosts can communicate**, while unauthorized hosts are blocked dynamically using OpenFlow rules.

---

## Objectives

* Allow communication only between trusted hosts
* Block unauthorized access
* Dynamically install flow rules
* Improve network security using SDN

---

## Architecture

* **Controller:** Ryu
* **Switch:** OpenFlow-enabled switch
* **Emulator:** Mininet
* **Hosts:**

  * h1 → 10.0.0.1 (Authorized)
  * h2 → 10.0.0.2 (Authorized)
  * h3 → 10.0.0.3 (Unauthorized)

---

##  Features

* Whitelist-based access control
* Dynamic flow rule installation
* ARP handling for connectivity
* Blocking unauthorized traffic
* Performance testing (Throughput & Latency)

---

##  Project Structure

```
sdn_project/
│── controller.py      # Ryu controller logic
│── topo.py            # Mininet topology
│── README.md
```

---

##  Setup & Installation

### 1. Install Dependencies

```bash
sudo apt update
sudo apt install mininet python3-pip -y
pip3 install ryu==4.34 eventlet==0.33.3 greenlet==2.0.2 dnspython==2.2.1
```

---

### 2. Run Controller

```bash
python3 -m ryu.cmd.manager controller.py
```

---

### 3. Run Mininet

```bash
sudo mn --custom topo.py --topo mytopo --controller remote
```

---

##  Testing

###  Connectivity Test

```bash
h1 ping h2   # Should work
h3 ping h1   # Should fail
```

---

### Throughput Test

```bash
h2 iperf -s
h1 iperf -c 10.0.0.2
```

---

###  Latency Test

```bash
h1 ping h2
```

---

## 📈 Results

| Test       | Result           |
| ---------- | -----------------|
| h1 → h2    |  Allowed         |
| h3 → h1    |  Blocked         |
| Throughput | High (~900 Mbps) |
| Latency    | Low (~0.1 ms)    |

---

##  Working Principle

1. Packet arrives at switch
2. Switch sends packet to controller
3. Controller checks whitelist
4. Decision:

   * Allowed → Forward
   * Not allowed → Drop
5. Flow rules installed dynamically

---

##  Access Control Logic

* ARP traffic → Always allowed
* Authorized IP → Forward
* Unauthorized IP → Drop

---

##  Performance Evaluation

* Throughput measured using `iperf`
* Latency measured using `ping`
* Efficient due to flow rule caching

---

##  Conclusion

The project successfully demonstrates **secure access control using SDN**.
Only authorized hosts can communicate, and unauthorized traffic is effectively blocked.

---


##  Author

Adarsh Naik
SRN: PES2UG24AM011

---
