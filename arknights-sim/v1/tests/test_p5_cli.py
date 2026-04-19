"""P5 acceptance tests: CLI entry point + JSON log output."""
from __future__ import annotations
import json
import os
import subprocess
import sys
import pytest

ARKNIGHTS_DIR = os.path.join(os.path.dirname(__file__), "..")
STAGE_PATH = os.path.join(ARKNIGHTS_DIR, "data", "stages", "main_0-1.yaml")


def run_cli(*extra_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "cli.py", STAGE_PATH, *extra_args],
        cwd=ARKNIGHTS_DIR,
        capture_output=True,
        text=True,
    )


def test_cli_win_exitcode():
    """Default run of main_0-1 exits 0 (win)."""
    proc = run_cli()
    assert proc.returncode == 0, f"Expected exit 0 (win)\n{proc.stdout}\n{proc.stderr}"


def test_cli_text_output_contains_win():
    proc = run_cli()
    assert "WIN" in proc.stdout.upper(), f"Expected WIN in output\n{proc.stdout}"


def test_cli_json_output_structure():
    proc = run_cli("--log", "json")
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["result"] == "win"
    assert data["lives"] == 3
    assert data["stage"] == "main_0-1"
    assert isinstance(data["log"], list)
    assert len(data["log"]) > 0
    assert isinstance(data["operators"], list)
    assert all("name" in op and "alive" in op for op in data["operators"])


def test_cli_json_operators_alive():
    proc = run_cli("--log", "json")
    data = json.loads(proc.stdout)
    for op in data["operators"]:
        assert op["alive"], f"{op['name']} should be alive after win"


def test_cli_custom_ops():
    """--ops flag overrides default operator list."""
    proc = run_cli("--ops", "liskarm,exusiai")
    assert proc.returncode == 0, f"liskarm+exusiai should clear main_0-1\n{proc.stderr}"


def test_cli_unknown_op_exits_2():
    proc = run_cli("--ops", "nonexistent_operator")
    assert proc.returncode == 2, "Unknown operator should exit 2"
    assert "Unknown operator" in proc.stderr


def test_cli_importable():
    """cli.main() can be called directly (not just via subprocess)."""
    from cli import main  # noqa: PLC0415
    stage_abs = os.path.abspath(STAGE_PATH)
    rc = main([stage_abs, "--log", "json"])
    assert rc == 0
