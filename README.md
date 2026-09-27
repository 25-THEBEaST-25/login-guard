# Login Guard — Brute-Force Login Simulator

Login Guard is a small Python command-line tool that simulates brute-force
login attempts against a fake system. It tracks failed login attempts per
source IP, automatically blocks any IP once it crosses a configurable
failure threshold, and writes a timestamped log of every attempt
(success, failure, or blocked).

It does not connect to any real service or accept real credentials — it is
a self-contained simulator for demonstrating and testing lockout logic.

---

## Features

- Simulates login attempts with configurable usernames, IPs, attempt
  count, and failure rate
- Tracks failed attempts per source IP
- Blocks an IP after a configurable number of failures (default: 5)
- Ignores further attempts from an already-blocked IP
- Logs every attempt (`SUCCESS` / `FAIL` / `BLOCKED`) with a timestamp
- Proper CLI with input validation (invalid IPs, non-numeric or negative
  counts, etc. are rejected with a clear error and non-zero exit code)
- Reproducible runs via `--seed`, for demos and testing

---

## Requirements

- Python 3.8+
- [pytest](https://pypi.org/project/pytest/) (only needed to run the test
  suite): `pip install pytest`

---

## Usage

```bash
python login_guard.py [options]
```

### Options

| Flag             | Description                                                        | Default                   |
|------------------|---------------------------------------------------------------------|----------------------------|
| `--attempts`     | Number of login attempts to simulate                               | `20`                       |
| `--threshold`    | Failed attempts from one IP before it is blocked                    | `5`                        |
| `--failure-rate` | Probability (0–1) that a simulated attempt fails                    | `0.7`                      |
| `--log-file`     | Path to the log file attempts are appended to                       | `login_logs.txt`           |
| `--ip`           | Restrict simulation to this IP (repeatable)                         | built-in demo IP pool      |
| `--username`     | Restrict simulation to this username (repeatable)                   | built-in demo usernames    |
| `--seed`         | Seed the RNG for a reproducible run                                 | random                     |
| `--quiet`        | Suppress per-attempt console output (log file is still written)     | off                        |

Run `python login_guard.py --help` for the full list.

### Examples

Run the default simulation (20 attempts, block after 5 failures):

```bash
python login_guard.py
```

Force a lockout demo against a single IP with a high failure rate and a
fixed seed, so the run is reproducible:

```bash
python login_guard.py --ip 10.0.0.5 --attempts 10 --threshold 3 --failure-rate 1.0 --seed 42
```

Use a custom log file location:

```bash
python login_guard.py --log-file /tmp/demo_logins.txt
```

Invalid input is rejected instead of silently running:

```bash
$ python login_guard.py --attempts -5
Error: attempts must be a positive integer, got -5
$ echo $?
1

$ python login_guard.py --ip 999.999.999.999
Error: invalid IP address: '999.999.999.999'
$ echo $?
1
```

### Example output

```
=== Login Guard (Brute-force Simulator) ===
[FAIL] 10.0.0.5 has 1 failed attempts
[FAIL] 10.0.0.5 has 2 failed attempts
[FAIL] 10.0.0.5 has 3 failed attempts
ALERT: IP 10.0.0.5 has been BLOCKED due to brute-force behavior!
[BLOCKED] IP 10.0.0.5 is already blocked!
[BLOCKED] IP 10.0.0.5 is already blocked!

Blocked IPs this run: 10.0.0.5
```

Each attempt is also appended to the log file, e.g.:

```
2026-09-27 12:00:01 | user=admin | ip=10.0.0.5 | status=FAIL
2026-09-27 12:00:01 | user=admin | ip=10.0.0.5 | status=FAIL
2026-09-27 12:00:01 | user=admin | ip=10.0.0.5 | status=FAIL
2026-09-27 12:00:01 | user=admin | ip=10.0.0.5 | status=BLOCKED
```

---

## How it works

1. Each simulated attempt picks a random username/IP pair (or uses the
   ones you supply) and a random success/failure outcome based on
   `--failure-rate`.
2. `record_attempt()` updates a per-IP failure counter. Once an IP's
   counter reaches `--threshold`, the IP is added to the blocked set.
3. Any further attempt from a blocked IP is short-circuited and logged as
   `BLOCKED`, without affecting the failure counter.
4. Every attempt is appended to the log file with a timestamp, username,
   IP, and status, regardless of outcome.

The core logic (`record_attempt`, `log_attempt`, `run_simulation`) is
factored out of `main()` so it can be unit tested directly, without
spawning a subprocess or relying on real randomness (see `tests/`).

---

## Running the tests

```bash
pip install pytest
pytest
```

The suite covers input validation, a normal successful login, a lockout
triggering after N failed attempts, a blocked IP being rejected on further
attempts, log file output format/content, and CLI error handling.

---

## Use cases

- **Security training/demos**: show, live, how brute-force detection and
  IP lockout work without touching a real authentication system.
- **Testing lockout logic**: use `--seed` and `--failure-rate 1.0` to
  produce deterministic runs and assert on the resulting log file or
  blocked-IP set, as a reference for building lockout logic elsewhere.
- **Log format experimentation**: point multiple runs at different
  `--log-file` paths to compare how downstream tooling (e.g. a SIEM
  parser) handles the output.

---

## Disclaimer

This project is for educational and ethical cybersecurity learning
purposes only — it simulates attempts against fake, in-memory data and
never targets a real system. Do not adapt it for use against systems you
do not own or have explicit authorization to test.
