"""Saving and loading benchmark results as JSON.

The layout mirrors pytest-benchmark's conventions so it feels familiar:

    <storage>/<machine-id>/<NNNN>_<commit>_<YYYYmmdd_HHMMSS>[_uncommitted-changes].json
"""

import datetime
import json
import math
import os
import platform
import re
import subprocess
from pathlib import Path
from typing import Any

#: Samples kept per benchmark in saved files. Larger sets are downsampled
#: evenly over the sorted values, which preserves the distribution's shape.
MAX_STORED_SAMPLES = 10_000

#: Keys of a result dict that are bulky raw data rather than summary stats.
_RAW_KEYS = {"samples", "raw_times"}

_SAVE_NAME_RE = re.compile(r"^(\d{4})_")


def machine_id() -> str:
    """Return an identifier for this platform/interpreter, e.g. ``Linux-CPython-3.13-64bit``."""
    impl = platform.python_implementation()
    major, minor = platform.python_version_tuple()[:2]
    bits = platform.architecture()[0]
    return f"{platform.system()}-{impl}-{major}.{minor}-{bits}"


def machine_info() -> dict[str, Any]:
    """Describe the machine. Deliberately excludes the hostname."""
    return {
        "machine": platform.machine(),
        "system": platform.system(),
        "release": platform.release(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
    }


def _git(*args: str, cwd: Path | None = None) -> str | None:
    try:
        out = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
            cwd=cwd,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip()


def commit_info(cwd: Path | None = None) -> dict[str, Any]:
    """Return the git commit, branch and dirty state of the repo at ``cwd``.

    Returns an empty dict outside a git repository.
    """
    commit = _git("rev-parse", "HEAD", cwd=cwd)
    if not commit:
        return {}
    status = _git("status", "--porcelain", "--untracked-files=no", cwd=cwd)
    return {
        "id": commit,
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd),
        "dirty": bool(status),
    }


def _json_safe(value: Any) -> Any:
    """Make floats JSON-safe (inf/nan become None)."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def downsample(samples: list[float], limit: int = MAX_STORED_SAMPLES) -> list[float]:
    """Return at most ``limit`` evenly spaced values from the sorted samples."""
    ordered = sorted(samples)
    if len(ordered) <= limit:
        return ordered
    step = (len(ordered) - 1) / (limit - 1)
    return [ordered[round(i * step)] for i in range(limit)]


def benchmark_record(entry: dict[str, Any]) -> dict[str, Any]:
    """Convert a collected benchmark entry into its JSON representation."""
    result = entry["result"]
    samples = list(result.get("samples") or [])
    stored = downsample(samples)
    stats = {key: value for key, value in result.items() if key not in _RAW_KEYS}
    return _json_safe(
        {
            "name": entry["name"],
            "fullname": entry["fullname"],
            "mode": result.get("mode", "sequential"),
            "stats": stats,
            "samples": stored,
            "samples_truncated": len(stored) < len(samples),
        }
    )


def build_report(
    entries: list[dict[str, Any]], version: str, root: Path | None = None
) -> dict[str, Any]:
    """Build the full JSON report for a session (git info is read from ``root``)."""
    return {
        "version": version,
        "datetime": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "machine_info": machine_info(),
        "commit_info": commit_info(root),
        "benchmarks": [benchmark_record(entry) for entry in entries],
    }


def write_report(report: dict[str, Any], path: str | Path) -> Path:
    """Write a report to ``path`` (creating parent directories)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return path


def load_report(path: str | Path) -> dict[str, Any]:
    """Load a report previously written by :func:`write_report`."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _run_number(path: Path) -> int | None:
    match = _SAVE_NAME_RE.match(path.name)
    return int(match.group(1)) if match else None


def _saved_runs(directory: Path) -> list[Path]:
    """Numbered saved runs in ``directory``, oldest first."""
    if not directory.is_dir():
        return []
    return sorted(
        path for path in directory.glob("*.json") if _run_number(path) is not None
    )


def autosave_path(storage: str | Path, report: dict[str, Any]) -> Path:
    """Return the next numbered file path for an autosaved report."""
    directory = Path(storage) / machine_id()
    last = max((_run_number(path) or 0 for path in _saved_runs(directory)), default=0)
    commit = report.get("commit_info") or {}
    commit_id = (commit.get("id") or "nogit")[:8]
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = "_uncommitted-changes" if commit.get("dirty") else ""
    return directory / f"{last + 1:04d}_{commit_id}_{stamp}{suffix}.json"


def find_baseline(storage: str | Path, selector: str = "") -> Path:
    """Locate a saved report to compare against.

    ``selector`` may be empty (latest saved run for this machine), a run number
    such as ``"3"`` or ``"0003"``, or a path to a JSON file.
    """
    if selector:
        candidate = Path(selector)
        if candidate.suffix == ".json" or candidate.exists():
            if not candidate.is_file():
                raise FileNotFoundError(f"Baseline file not found: {candidate}")
            return candidate

    directory = Path(storage) / machine_id()
    runs = _saved_runs(directory)
    if not runs:
        raise FileNotFoundError(
            f"No saved benchmark runs in {directory}. "
            "Save one first with --async-bench-autosave."
        )
    if not selector:
        return runs[-1]
    if not selector.isdigit():
        raise ValueError(
            f"Invalid --async-bench-compare value {selector!r}: "
            "expected a run number or a path to a .json file"
        )
    prefix = f"{int(selector):04d}_"
    for run in runs:
        if run.name.startswith(prefix):
            return run
    raise FileNotFoundError(f"No saved run numbered {selector} in {directory}")
