# 🔐 Login Guard — Brute-Force Attack Simulator

Login Guard is a Python-based cybersecurity simulation tool that demonstrates how brute-force login attacks happen and how systems can detect, log, and block malicious IPs in real time.

This project is built as part of daily hands-on cybersecurity practice.

---

## 🚀 Features

- ✅ Simulates real-world brute-force login attempts
- ✅ Random usernames & IP addresses
- ✅ Tracks failed attempts per IP
- ✅ Automatically blocks IPs after 5 failed attempts
- ✅ Logs all login attempts with timestamps
- ✅ Saves blocked IPs to a file
- ✅ Displays real-time alerts in the terminal

---

## 🛠️ Technologies Used

- Python 3
- Random module
- Date & Time logging
- File handling
- Dictionaries & Sets

---

## 📂 Project Files

- `login_guard.py` → Main brute-force detection script  
- `login_logs.txt` → Stores all login attempts  
- `blocked_ips.txt` → Stores blocked IP addresses  
- `README.md` → Project documentation  

---

## ▶️ How to Run

Make sure Python is installed, then run:

```bash
python login_guard.py
