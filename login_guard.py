import random
from datetime import datetime

LOG_FILE = "login_logs.txt"

def log_attempt(username: str, ip: str, success: bool) -> None:
    """Write one login attempt line to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if success else "FAIL"
    line = f"{timestamp} | user={username} | ip={ip} | status={status}\n"
    with open(LOG_FILE, "a") as f:
        f.write(line)

def simulate_single_attempt():
    """Generate one random login attempt."""
    usernames = ["shop_owner", "admin", "cashier", "manager"]
    ips = ["192.168.0.10", "192.168.0.15", "192.168.0.21", "192.168.0.30"]

    username = random.choice(usernames)
    ip = random.choice(ips)

    # 70% chance of failure, 30% success
    success = random.random() < 0.3

    log_attempt(username, ip, success)
    print(f"Logged attempt -> user={username}, ip={ip}, success={success}")

    # 👇 NEW: return the values so main() can use them
    return username, ip, success

def main():
    print("=== Login Guard (Brute-force Simulator) ===")

    failed_attempts = {}   # Track failed logins per IP
    blocked_ips = set()    # Store blocked IPs

    for i in range(20):    # Simulate 20 login attempts
        username, ip, success = simulate_single_attempt()

        # If IP already blocked → Ignore further attempts
        if ip in blocked_ips:
            print(f"[BLOCKED] IP {ip} is already blocked!\n")
            continue

        if not success:
            failed_attempts[ip] = failed_attempts.get(ip, 0) + 1
            print(f"[FAIL] {ip} has {failed_attempts[ip]} failed attempts")

            # Block after 5 failures
            if failed_attempts[ip] >= 5:
                blocked_ips.add(ip)
                print(f"🚨 ALERT: IP {ip} has been BLOCKED due to brute-force behavior!\n")

        else:
            print(f"[SUCCESS] Login from IP {ip}\n")


if __name__ == "__main__":
    main()
