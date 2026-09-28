# Production Readiness Checklist

Status: **Complete**

| Requirement | Status |
|---|---|
| Proper CLI interface with `argparse` (not hardcoded values) | Done — `--attempts`, `--threshold`, `--failure-rate`, `--log-file`, `--ip`, `--username`, `--seed`, `--quiet` |
| Input validation (invalid IPs, negative attempt counts, etc.) | Done — `validate_ip`, `validate_positive_int`, `validate_probability`; rejected with a clear message and non-zero exit code |
| Unit tests: normal login | Done — `test_normal_successful_login_is_not_blocked` |
| Unit tests: lockout trigger | Done — `test_lockout_triggers_after_n_failed_attempts` |
| Unit tests: IP block | Done — `test_blocked_ip_is_rejected_on_further_attempts`, `test_other_ips_are_unaffected_by_one_ips_lockout` |
| Unit tests: log output | Done — `test_log_attempt_writes_expected_format`, `test_log_attempt_appends_multiple_lines`, `test_run_simulation_logs_one_line_per_attempt` |
| `README.md`: what it does, how to run, example output, use cases | Done |
| `.gitignore` | Done |
| No hardcoded credentials or debug prints | Verified — the tool simulates fake credentials against no real system; all `print()` calls are intentional CLI output, not leftover debugging |

## Verification performed

- Installed into a clean virtualenv and ran the full pytest suite: 21/21 passed.
- Ran `login_guard.py` directly from the CLI (`--attempts 10 --threshold 3 --seed 1`) and confirmed lockout, block, and log-output behavior matches the printed output.
- Confirmed invalid input (bad IP, negative attempts, non-numeric threshold) is rejected with a clear error and non-zero exit code, both via the CLI and via dedicated `test_main_rejects_*` tests.
- Reviewed `login_guard.py` for hardcoded credentials, real IPs, and debug prints — none found; all output is intentional CLI reporting.

No further action is required for this repo's production-readiness bar unless new attack simulation features are added.
