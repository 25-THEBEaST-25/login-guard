"""Unit tests for login_guard.py."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import login_guard  # noqa: E402


# --------------------------------------------------------------------------
# Input validation
# --------------------------------------------------------------------------


def test_validate_ip_accepts_valid_ipv4():
    assert login_guard.validate_ip("192.168.0.10") == "192.168.0.10"


def test_validate_ip_accepts_valid_ipv6():
    assert login_guard.validate_ip("::1") == "::1"


def test_validate_ip_rejects_invalid_address():
    with pytest.raises(ValueError, match="invalid IP address"):
        login_guard.validate_ip("999.999.999.999")


def test_validate_ip_rejects_non_ip_string():
    with pytest.raises(ValueError):
        login_guard.validate_ip("not-an-ip")


def test_validate_positive_int_accepts_positive_value():
    assert login_guard.validate_positive_int("5", "attempts") == 5


def test_validate_positive_int_rejects_negative():
    with pytest.raises(ValueError, match="positive integer"):
        login_guard.validate_positive_int(-3, "attempts")


def test_validate_positive_int_rejects_zero():
    with pytest.raises(ValueError, match="positive integer"):
        login_guard.validate_positive_int(0, "threshold")


def test_validate_positive_int_rejects_non_numeric():
    with pytest.raises(ValueError, match="must be an integer"):
        login_guard.validate_positive_int("abc", "attempts")


def test_validate_probability_rejects_out_of_range():
    with pytest.raises(ValueError, match="between 0 and 1"):
        login_guard.validate_probability(1.5, "failure-rate")


def test_validate_probability_accepts_boundaries():
    assert login_guard.validate_probability(0, "failure-rate") == 0.0
    assert login_guard.validate_probability(1, "failure-rate") == 1.0


# --------------------------------------------------------------------------
# Core lockout logic
# --------------------------------------------------------------------------


def test_normal_successful_login_is_not_blocked():
    failed_attempts = {}
    blocked_ips = set()

    status, newly_blocked = login_guard.record_attempt(
        failed_attempts, blocked_ips, "10.0.0.1", success=True, threshold=5
    )

    assert status == "SUCCESS"
    assert newly_blocked is False
    assert "10.0.0.1" not in blocked_ips
    assert failed_attempts == {}


def test_lockout_triggers_after_n_failed_attempts():
    failed_attempts = {}
    blocked_ips = set()
    ip = "10.0.0.2"
    threshold = 5

    for i in range(1, threshold):
        status, newly_blocked = login_guard.record_attempt(
            failed_attempts, blocked_ips, ip, success=False, threshold=threshold
        )
        assert status == "FAIL"
        assert newly_blocked is False
        assert ip not in blocked_ips
        assert failed_attempts[ip] == i

    # The threshold-th failure should trigger the block.
    status, newly_blocked = login_guard.record_attempt(
        failed_attempts, blocked_ips, ip, success=False, threshold=threshold
    )
    assert status == "FAIL"
    assert newly_blocked is True
    assert ip in blocked_ips


def test_blocked_ip_is_rejected_on_further_attempts():
    failed_attempts = {}
    blocked_ips = {"10.0.0.3"}

    status, newly_blocked = login_guard.record_attempt(
        failed_attempts, blocked_ips, "10.0.0.3", success=True, threshold=5
    )

    assert status == "BLOCKED"
    assert newly_blocked is False
    # A blocked IP's attempts should not affect the failure counter.
    assert "10.0.0.3" not in failed_attempts


def test_other_ips_are_unaffected_by_one_ips_lockout():
    failed_attempts = {}
    blocked_ips = set()

    for _ in range(5):
        login_guard.record_attempt(
            failed_attempts, blocked_ips, "10.0.0.4", success=False, threshold=5
        )

    status, _ = login_guard.record_attempt(
        failed_attempts, blocked_ips, "10.0.0.5", success=True, threshold=5
    )

    assert "10.0.0.4" in blocked_ips
    assert "10.0.0.5" not in blocked_ips
    assert status == "SUCCESS"


# --------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------


def test_log_attempt_writes_expected_format(tmp_path):
    log_file = tmp_path / "attempts.log"

    login_guard.log_attempt("admin", "10.0.0.1", "FAIL", log_file=str(log_file))

    contents = log_file.read_text()
    lines = contents.strip().splitlines()
    assert len(lines) == 1
    line = lines[0]
    assert "user=admin" in line
    assert "ip=10.0.0.1" in line
    assert "status=FAIL" in line
    # Line should start with a timestamp like "YYYY-MM-DD HH:MM:SS"
    timestamp_part = line.split(" | ")[0]
    assert len(timestamp_part) == 19
    assert timestamp_part[4] == "-" and timestamp_part[7] == "-"


def test_log_attempt_appends_multiple_lines(tmp_path):
    log_file = tmp_path / "attempts.log"

    login_guard.log_attempt("admin", "10.0.0.1", "SUCCESS", log_file=str(log_file))
    login_guard.log_attempt("cashier", "10.0.0.2", "FAIL", log_file=str(log_file))

    lines = log_file.read_text().strip().splitlines()
    assert len(lines) == 2
    assert "status=SUCCESS" in lines[0]
    assert "status=FAIL" in lines[1]


def test_run_simulation_logs_one_line_per_attempt(tmp_path):
    log_file = tmp_path / "attempts.log"
    random_module = login_guard.random
    random_module.seed(42)

    failed_attempts, blocked_ips = login_guard.run_simulation(
        attempts=15,
        threshold=5,
        usernames=["admin"],
        ips=["10.0.0.9"],
        failure_rate=1.0,  # force every attempt to fail
        log_file=str(log_file),
        quiet=True,
    )

    lines = log_file.read_text().strip().splitlines()
    assert len(lines) == 15
    # All attempts share the single IP; the first `threshold` are FAIL,
    # the rest are BLOCKED.
    fail_lines = [l for l in lines if "status=FAIL" in l]
    blocked_lines = [l for l in lines if "status=BLOCKED" in l]
    assert len(fail_lines) == 5
    assert len(blocked_lines) == 10
    assert "10.0.0.9" in blocked_ips


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def test_main_rejects_invalid_ip(tmp_path, capsys):
    log_file = tmp_path / "attempts.log"
    exit_code = login_guard.main(
        ["--ip", "999.999.999.999", "--log-file", str(log_file), "--attempts", "1"]
    )
    captured = capsys.readouterr()
    assert exit_code != 0
    assert "invalid IP address" in captured.err


def test_main_rejects_negative_attempts(tmp_path, capsys):
    log_file = tmp_path / "attempts.log"
    exit_code = login_guard.main(
        ["--attempts", "-5", "--log-file", str(log_file)]
    )
    captured = capsys.readouterr()
    assert exit_code != 0
    assert "positive integer" in captured.err


def test_main_rejects_non_numeric_threshold(tmp_path, capsys):
    log_file = tmp_path / "attempts.log"
    exit_code = login_guard.main(
        ["--threshold", "banana", "--log-file", str(log_file)]
    )
    captured = capsys.readouterr()
    assert exit_code != 0
    assert "must be an integer" in captured.err


def test_main_succeeds_with_valid_arguments_and_writes_log(tmp_path, capsys):
    log_file = tmp_path / "attempts.log"
    exit_code = login_guard.main(
        [
            "--attempts",
            "10",
            "--threshold",
            "3",
            "--ip",
            "10.0.0.50",
            "--username",
            "tester",
            "--seed",
            "1",
            "--quiet",
            "--log-file",
            str(log_file),
        ]
    )

    assert exit_code == 0
    assert log_file.exists()
    lines = log_file.read_text().strip().splitlines()
    assert len(lines) == 10
