#!/usr/bin/env python3
"""Login Guard: a brute-force login attack simulator with IP blocking.

Simulates login attempts against a fake system, tracks failed attempts per
source IP, and locks out any IP that exceeds a configurable failure
threshold. Every attempt (success, failure, or blocked) is appended to a
log file with a timestamp.

Intended for security training/demos and for testing lockout logic, not
for use against real systems.
"""

import argparse
import ipaddress
import random
import sys
from datetime import datetime
from typing import Dict, List, Set, Tuple

DEFAULT_LOG_FILE = "login_logs.txt"
DEFAULT_ATTEMPTS = 20
DEFAULT_THRESHOLD = 5
DEFAULT_FAILURE_RATE = 0.7  # probability that a simulated attempt fails
DEFAULT_USERNAMES = ["shop_owner", "admin", "cashier", "manager"]
DEFAULT_IPS = ["192.168.0.10", "192.168.0.15", "192.168.0.21", "192.168.0.30"]


def validate_ip(ip: str) -> str:
    """Validate that `ip` is a syntactically valid IPv4/IPv6 address.

    Returns the (unchanged) ip string on success. Raises ValueError with a
    clear message if the value is not a valid IP address.
    """
    try:
        ipaddress.ip_address(ip)
    except ValueError as exc:
        raise ValueError(f"invalid IP address: {ip!r}") from exc
    return ip


def validate_positive_int(value, name: str) -> int:
    """Validate that `value` is (or can be parsed as) a positive integer."""
    try:
        n = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer, got {value!r}") from exc
    if n <= 0:
        raise ValueError(f"{name} must be a positive integer, got {n}")
    return n


def validate_probability(value, name: str) -> float:
    """Validate that `value` is a float in the inclusive range [0, 1]."""
    try:
        f = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number, got {value!r}") from exc
    if not (0.0 <= f <= 1.0):
        raise ValueError(f"{name} must be between 0 and 1, got {f}")
    return f


def log_attempt(username: str, ip: str, status: str, log_file: str = DEFAULT_LOG_FILE) -> None:
    """Append one login attempt line to the log file.

    `status` should be one of "SUCCESS", "FAIL", or "BLOCKED".
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} | user={username} | ip={ip} | status={status}\n"
    with open(log_file, "a") as f:
        f.write(line)


def record_attempt(
    failed_attempts: Dict[str, int],
    blocked_ips: Set[str],
    ip: str,
    success: bool,
    threshold: int,
) -> Tuple[str, bool]:
    """Apply one login attempt's outcome to the lockout state.

    Mutates `failed_attempts` and `blocked_ips` in place.

    Returns (status, newly_blocked):
      - status is "BLOCKED" if the IP was already blocked before this
        attempt, "SUCCESS" if the login succeeded, or "FAIL" otherwise.
      - newly_blocked is True iff this attempt is the one that pushed the
        IP's failure count to (or past) `threshold` for the first time.
    """
    if ip in blocked_ips:
        return "BLOCKED", False

    if success:
        return "SUCCESS", False

    failed_attempts[ip] = failed_attempts.get(ip, 0) + 1
    newly_blocked = False
    if failed_attempts[ip] >= threshold:
        blocked_ips.add(ip)
        newly_blocked = True
    return "FAIL", newly_blocked


def simulate_attempt(
    usernames: List[str], ips: List[str], failure_rate: float
) -> Tuple[str, str, bool]:
    """Pick a random username/IP pair and a random outcome for one attempt."""
    username = random.choice(usernames)
    ip = random.choice(ips)
    success = random.random() >= failure_rate
    return username, ip, success


def run_simulation(
    attempts: int,
    threshold: int,
    usernames: List[str],
    ips: List[str],
    failure_rate: float,
    log_file: str,
    quiet: bool = False,
) -> Tuple[Dict[str, int], Set[str]]:
    """Run the full simulation loop, logging and printing each attempt.

    Returns the final (failed_attempts, blocked_ips) state.
    """
    failed_attempts: Dict[str, int] = {}
    blocked_ips: Set[str] = set()

    for _ in range(attempts):
        username, ip, success = simulate_attempt(usernames, ips, failure_rate)
        status, newly_blocked = record_attempt(
            failed_attempts, blocked_ips, ip, success, threshold
        )
        log_attempt(username, ip, status, log_file)

        if not quiet:
            if status == "BLOCKED":
                print(f"[BLOCKED] IP {ip} is already blocked!")
            elif status == "FAIL":
                print(f"[FAIL] {ip} has {failed_attempts[ip]} failed attempts")
                if newly_blocked:
                    print(f"ALERT: IP {ip} has been BLOCKED due to brute-force behavior!")
            else:
                print(f"[SUCCESS] Login from IP {ip}")

    return failed_attempts, blocked_ips


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="login_guard",
        description=(
            "Login Guard: simulate brute-force login attempts and demonstrate "
            "per-IP lockout after repeated failures."
        ),
    )
    parser.add_argument(
        "--attempts",
        default=DEFAULT_ATTEMPTS,
        help=f"Number of login attempts to simulate (default: {DEFAULT_ATTEMPTS}).",
    )
    parser.add_argument(
        "--threshold",
        default=DEFAULT_THRESHOLD,
        help=f"Failed attempts from one IP before it is blocked (default: {DEFAULT_THRESHOLD}).",
    )
    parser.add_argument(
        "--failure-rate",
        default=DEFAULT_FAILURE_RATE,
        help=f"Probability (0-1) that a simulated attempt fails (default: {DEFAULT_FAILURE_RATE}).",
    )
    parser.add_argument(
        "--log-file",
        default=DEFAULT_LOG_FILE,
        help=f"Path to the log file attempts are appended to (default: {DEFAULT_LOG_FILE}).",
    )
    parser.add_argument(
        "--ip",
        dest="ips",
        action="append",
        metavar="IP",
        help="Restrict simulated attempts to this IP (repeatable). Default: built-in demo IP pool.",
    )
    parser.add_argument(
        "--username",
        dest="usernames",
        action="append",
        metavar="NAME",
        help="Restrict simulated attempts to this username (repeatable). Default: built-in demo usernames.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed the random number generator for a reproducible run.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-attempt console output (log file is still written).",
    )
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        attempts = validate_positive_int(args.attempts, "attempts")
        threshold = validate_positive_int(args.threshold, "threshold")
        failure_rate = validate_probability(args.failure_rate, "failure-rate")

        ips = args.ips or DEFAULT_IPS
        ips = [validate_ip(ip) for ip in ips]

        usernames = args.usernames or DEFAULT_USERNAMES
        if not usernames:
            raise ValueError("at least one --username must be provided")

        if not args.log_file.strip():
            raise ValueError("--log-file must not be empty")
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.seed is not None:
        random.seed(args.seed)

    print("=== Login Guard (Brute-force Simulator) ===")
    _, blocked_ips = run_simulation(
        attempts=attempts,
        threshold=threshold,
        usernames=usernames,
        ips=ips,
        failure_rate=failure_rate,
        log_file=args.log_file,
        quiet=args.quiet,
    )

    if blocked_ips:
        print(f"\nBlocked IPs this run: {', '.join(sorted(blocked_ips))}")
    else:
        print("\nNo IPs were blocked this run.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
