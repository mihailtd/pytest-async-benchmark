#!/usr/bin/env python3
"""
Code quality checker script.

Runs linting, formatting, and tests in one command.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"🔄 {description}...")
    result = subprocess.run(cmd, shell=True, cwd=Path.cwd())

    if result.returncode == 0:
        print(f"✅ {description} passed!")
        return True
    else:
        print(f"❌ {description} failed!")
        return False


def main():
    """Run all quality checks."""
    print("🧹 Running code quality checks for pytest-async-benchmark\n")

    checks = [
        ("uv run ruff check . --fix", "Linting (with auto-fix)"),
        ("uv run ruff format .", "Code formatting"),
        ("uv run pytest tests/ -v --tb=short", "Test suite"),
        ("python scripts/release-check.py", "Release readiness"),
    ]

    failed_checks = []

    for cmd, description in checks:
        success = run_command(cmd, description)
        if not success:
            failed_checks.append(description)
        print()  # Add spacing between checks

    if failed_checks:
        print(f"❌ {len(failed_checks)} check(s) failed:")
        for check in failed_checks:
            print(f"   • {check}")
        sys.exit(1)
    else:
        print("🎉 All quality checks passed! Your code is ready.")
        sys.exit(0)


if __name__ == "__main__":
    main()
