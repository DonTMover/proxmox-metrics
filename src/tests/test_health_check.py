from pathlib import Path
import sys

from health_check import check_file, check_command, check_python_modules


def test_check_file_tmp(tmp_path):
    p = tmp_path / "cfg.yaml"
    p.write_text("ok")
    assert check_file(p) is True
    assert check_file(tmp_path / "nope") is False


def test_check_command_known_and_unknown():
    # 'python3' may exist in CI environment; test returns a boolean
    assert isinstance(check_command("python3"), bool)
    assert check_command("no-such-command-xyz") is False


def test_check_python_modules_returns_bool():
    assert isinstance(check_python_modules(), bool)
