#!/usr/bin/env python3
"""
Release readiness checker for pytest-async-benchmark

This script verifies that the package is ready for release to PyPI by checking:
- Git status and cleanliness
- Version consistency
- Test suite passes
- Package builds successfully
- Required files exist
- GitHub workflows are in place
"""

import re
import subprocess
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


def run_command(cmd: str, cwd: str = None) -> tuple[bool, str, str]:
    """Run a command and return success status, stdout, and stderr."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=cwd or Path.cwd()
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def print_header(text: str) -> None:
    """Print a colored header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")


def print_check(passed: bool, message: str) -> None:
    """Print a check result with colored status."""
    status = f"{Colors.GREEN}✅" if passed else f"{Colors.RED}❌"
    print(f"{status} {message}{Colors.END}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def print_info(message: str) -> None:
    """Print an info message."""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.END}")


def check_git_status() -> list[str]:
    """Check git repository status."""
    issues = []

    print_header("🔍 Git Repository Checks")

    success, stdout, stderr = run_command("git rev-parse --git-dir")
    if not success:
        issues.append("Not in a git repository")
        print_check(False, "Git repository detected")
        return issues

    print_check(True, "Git repository detected")

    success, stdout, stderr = run_command("git status --porcelain")
    if stdout.strip():
        issues.append("Working directory not clean - commit all changes first")
        print_check(False, "Working directory is clean")
        print_info(f"Uncommitted changes found:\n{stdout}")
    else:
        print_check(True, "Working directory is clean")

    success, stdout, stderr = run_command("git branch --show-current")
    current_branch = stdout.strip()
    if current_branch != "main":
        print_warning(
            f"Currently on branch '{current_branch}', consider switching to 'main' for release"
        )
    else:
        print_check(True, "On main branch")

    success, stdout, stderr = run_command("git log --oneline -1")
    if success:
        print_check(True, f"Latest commit: {stdout}")
    else:
        issues.append("No commits found in repository")
        print_check(False, "Repository has commits")

    return issues


def check_version_consistency() -> tuple[list[str], str]:
    """Check version consistency across files."""
    issues = []
    version = None

    print_header("📦 Version Consistency Checks")

    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        issues.append("pyproject.toml not found")
        print_check(False, "pyproject.toml exists")
        return issues, version

    print_check(True, "pyproject.toml exists")

    try:
        with open(pyproject_path) as f:
            content = f.read()
            version_match = re.search(r'version = "([^"]+)"', content)
            if version_match:
                version = version_match.group(1)
                print_check(True, f"Version found in pyproject.toml: {version}")

                if re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$", version):
                    print_check(True, f"Version format is valid: {version}")
                else:
                    issues.append(
                        f"Version format invalid: {version} (should be X.Y.Z or X.Y.Z-suffix)"
                    )
                    print_check(False, "Version format is valid")
            else:
                issues.append("Version not found in pyproject.toml")
                print_check(False, "Version found in pyproject.toml")
    except Exception as e:
        issues.append(f"Could not read pyproject.toml: {e}")
        print_check(False, "Could read pyproject.toml")

    if version:
        success, stdout, stderr = run_command(f"git tag -l v{version}")
        if stdout.strip():
            issues.append(f"Git tag v{version} already exists")
            print_check(False, f"Tag v{version} is available")
        else:
            print_check(True, f"Tag v{version} is available")

    return issues, version


def check_required_files() -> list[str]:
    """Check that all required files exist."""
    issues = []

    print_header("📁 Required Files Check")

    required_files = [
        ("pyproject.toml", "Package configuration"),
        ("README.md", "Package documentation"),
        ("LICENSE", "License file"),
        ("src/pytest_async_benchmark/__init__.py", "Package init file"),
        ("src/pytest_async_benchmark/plugin.py", "Pytest plugin"),
        (".github/workflows/ci.yml", "CI workflow"),
    ]

    for file_path, description in required_files:
        if Path(file_path).exists():
            print_check(True, f"{description}: {file_path}")
        else:
            issues.append(f"Missing required file: {file_path}")
            print_check(False, f"{description}: {file_path}")

    return issues


def check_package_configuration() -> list[str]:
    """Check package configuration in pyproject.toml."""
    issues = []

    print_header("⚙️  Package Configuration Check")

    try:
        with open("pyproject.toml") as f:
            content = f.read()

        checks = [
            ('name = "pytest-async-benchmark"', "Package name"),
            ("description =", "Package description"),
            ("authors =", "Package authors"),
            ("pytest>=", "Pytest dependency"),
            ("rich>=", "Rich dependency"),
            ('[project.entry-points."pytest11"]', "Pytest entry point"),
        ]

        for pattern, description in checks:
            if pattern in content:
                print_check(True, f"{description} configured")
            else:
                issues.append(f"Missing configuration: {description}")
                print_check(False, f"{description} configured")

    except Exception as e:
        issues.append(f"Could not read pyproject.toml: {e}")
        print_check(False, "Could read pyproject.toml")

    return issues


def check_tests() -> list[str]:
    """Run the test suite."""
    issues = []

    print_header("🧪 Test Suite Check")

    print_info("Running linting checks...")
    success, stdout, stderr = run_command("uv run ruff check .")
    if success:
        print_check(True, "Ruff linting passed")
    else:
        issues.append("Ruff linting failed")
        print_check(False, "Ruff linting passed")
        if stderr:
            print_info(f"Linting errors:\n{stderr}")

    print_info("Checking code formatting...")
    success, stdout, stderr = run_command("uv run ruff format --check .")
    if success:
        print_check(True, "Code formatting is correct")
    else:
        issues.append("Code formatting check failed")
        print_check(False, "Code formatting is correct")
        if stdout:
            print_info(f"Files need formatting:\n{stdout}")

    print_info("Running main test suite...")
    success, stdout, stderr = run_command("uv run pytest tests/ -v --tb=short")
    if success:
        # Count tests
        test_count = stdout.count(" PASSED")
        print_check(True, f"Main test suite passed ({test_count} tests)")
    else:
        issues.append("Main test suite failed")
        print_check(False, "Main test suite passed")
        if stderr:
            print_info(f"Test errors:\n{stderr}")

    print_info("Testing example files...")
    success, stdout, stderr = run_command(
        "uv run python -m pytest examples/pytest_examples.py -v"
    )
    if success:
        example_count = stdout.count(" PASSED")
        print_check(True, f"Example tests passed ({example_count} tests)")
    else:
        issues.append("Example tests failed")
        print_check(False, "Example tests passed")
        if stderr:
            print_info(f"Example test errors:\n{stderr}")

    print_info("Testing comparison examples...")
    success, stdout, stderr = run_command(
        "uv run python examples/comparison_examples.py"
    )
    if success:
        print_check(True, "Comparison examples run successfully")
    else:
        issues.append("Comparison examples failed")
        print_check(False, "Comparison examples run successfully")
        if stderr:
            print_info(f"Comparison example errors:\n{stderr}")

    return issues


def check_package_build() -> list[str]:
    """Check that the package builds successfully."""
    issues = []

    print_header("🔨 Package Build Check")

    print_info("Building package...")
    success, stdout, stderr = run_command("uv build")
    if success:
        print_check(True, "Package built successfully")

        dist_path = Path("dist")
        if dist_path.exists():
            wheels = list(dist_path.glob("*.whl"))
            tarballs = list(dist_path.glob("*.tar.gz"))

            if wheels:
                print_check(True, f"Wheel built: {wheels[0].name}")
            else:
                issues.append("No wheel file found in dist/")
                print_check(False, "Wheel file created")

            if tarballs:
                print_check(True, f"Source distribution built: {tarballs[0].name}")
            else:
                issues.append("No source distribution found in dist/")
                print_check(False, "Source distribution created")
        else:
            issues.append("dist/ directory not found after build")
            print_check(False, "Build artifacts created")
    else:
        issues.append("Package build failed")
        print_check(False, "Package built successfully")
        if stderr:
            print_info(f"Build errors:\n{stderr}")

    print_info("Testing package installation...")
    success, stdout, stderr = run_command("uv pip install dist/*.whl --force-reinstall")
    if success:
        print_check(True, "Package can be installed")

        success, stdout, stderr = run_command(
            'uv run python -c "import pytest_async_benchmark; print(f\\"✅ Package imports successfully - version {pytest_async_benchmark.__version__}\\")"'
        )
        if success:
            print_check(True, "Package imports successfully")
            print_info(stdout)
        else:
            issues.append("Package import failed")
            print_check(False, "Package imports successfully")
            if stderr:
                print_info(f"Import errors:\n{stderr}")
    else:
        issues.append("Package installation failed")
        print_check(False, "Package can be installed")
        if stderr:
            print_info(f"Installation errors:\n{stderr}")

    return issues


def print_summary(all_issues: list[str], version: str) -> bool:
    """Print the final summary and next steps."""
    print_header("📊 Release Readiness Summary")

    if all_issues:
        print_check(False, f"Found {len(all_issues)} issues that need to be resolved:")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")

        print(f"\n{Colors.BOLD}{Colors.YELLOW}🔧 Next Steps:{Colors.END}")
        print("1. Fix the issues listed above")
        print("2. Commit and push all changes")
        print("3. Run this script again to verify fixes")
        if version:
            print(f"4. When ready: git tag v{version} && git push origin v{version}")

        return False
    else:
        print_check(True, "Package is ready for release!")

        print(f"\n{Colors.BOLD}{Colors.GREEN}🚀 Ready to Release!{Colors.END}")
        if version:
            print(f"\n{Colors.BOLD}To release version {version}:{Colors.END}")
            print(f"   {Colors.CYAN}git tag v{version}{Colors.END}")
            print(f"   {Colors.CYAN}git push origin v{version}{Colors.END}")

        print(f"\n{Colors.BOLD}📦 GitHub Actions will automatically:{Colors.END}")
        print("   • Run tests on multiple Python versions")
        print("   • Build the package")
        print("   • Publish to PyPI using trusted publishing")

        print(f"\n{Colors.BOLD}🎉 After release, users can install with:{Colors.END}")
        print(f"   {Colors.CYAN}pip install pytest-async-benchmark{Colors.END}")
        print(f"   {Colors.CYAN}uv add pytest-async-benchmark{Colors.END}")

        return True


def main():
    """Main entry point."""
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("🔬 pytest-async-benchmark Release Readiness Checker")
    print(f"   Verifying package is ready for PyPI publication{Colors.END}")

    all_issues = []
    version = None

    try:
        all_issues.extend(check_git_status())
        version_issues, detected_version = check_version_consistency()
        all_issues.extend(version_issues)
        version = detected_version

        all_issues.extend(check_required_files())
        all_issues.extend(check_package_configuration())
        all_issues.extend(check_tests())
        all_issues.extend(check_package_build())

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Check interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Unexpected error during checks: {e}{Colors.END}")
        sys.exit(1)

    ready = print_summary(all_issues, version)
    sys.exit(0 if ready else 1)


if __name__ == "__main__":
    main()
