"""Statistics calculation for async benchmarks."""

import math
import statistics
from collections.abc import Sequence
from typing import Any

#: Percentiles reported for every benchmark (as ``p50``, ``p75``, ...).
PERCENTILES = (50, 75, 90, 95, 99)


def percentile(sorted_values: Sequence[float], pct: float) -> float:
    """Return the ``pct``-th percentile of already-sorted values.

    Uses linear interpolation between closest ranks, which matches NumPy's
    default (``method="linear"``) and ``statistics.quantiles(method="inclusive")``.
    """
    if not sorted_values:
        raise ValueError("percentile() requires at least one value")
    if not 0 <= pct <= 100:
        raise ValueError("pct must be between 0 and 100")
    if len(sorted_values) == 1:
        return float(sorted_values[0])

    position = (len(sorted_values) - 1) * pct / 100
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(sorted_values[lower])
    fraction = position - lower
    return (
        sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * fraction
    )


def compute_stats(samples: Sequence[float]) -> dict[str, Any]:
    """Compute latency statistics from per-call samples (in seconds)."""
    if not samples:
        raise ValueError("compute_stats() requires at least one sample")

    ordered = sorted(samples)
    mean = statistics.fmean(ordered)
    stats: dict[str, Any] = {
        "min": ordered[0],
        "max": ordered[-1],
        "mean": mean,
        "median": percentile(ordered, 50),
        "stddev": statistics.stdev(ordered) if len(ordered) > 1 else 0.0,
    }
    for pct in PERCENTILES:
        stats[f"p{pct}"] = percentile(ordered, pct)
    stats["ops"] = 1.0 / mean if mean > 0 else float("inf")
    stats["count"] = len(ordered)
    stats["total_time"] = math.fsum(ordered)
    return stats


class StatsContainer:
    """Container for benchmark statistics calculation."""

    def __init__(self):
        self.measurements: list[float] = []

    def add_measurement(self, duration: float):
        """Add a timing measurement."""
        self.measurements.append(duration)

    def calculate_stats(self) -> dict[str, Any]:
        """Calculate comprehensive statistics."""
        if not self.measurements:
            return {}

        stats = compute_stats(self.measurements)
        stats["raw_times"] = self.measurements.copy()
        return stats

    def reset(self):
        """Reset all measurements."""
        self.measurements.clear()
