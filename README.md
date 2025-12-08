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

---

## 🧠 How It Works (Internals Explained)

1. The script generates **random IP addresses and usernames** to simulate attackers.
2. Every login attempt is checked against a **failed-attempt counter**.
3. If an IP fails more than **5 times**, it is:
   - Instantly **blocked**
   - Written to `blocked_ips.txt`
4. Every login attempt (success or failure) is logged with:
   - Timestamp
   - Username
   - IP Address
   - Status (SUCCESS / FAILED / BLOCKED)
5. Real-time alerts are printed in the terminal for quick monitoring.

This mimics how real-world systems detect and respond to brute-force attacks.

---

## ⚠️ Disclaimer

This project is built **strictly for educational and ethical cybersecurity learning purposes**.  
Do NOT use this tool for illegal or unauthorized activity.

---

## 👨‍💻 Author

Built with 💚 by Aryan  
Daily Cybersecurity Practice Project
