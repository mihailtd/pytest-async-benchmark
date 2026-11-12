"""Noise-aware comparison of benchmark runs.

A benchmark is only reported as a regression when it is *both*:

1. slower than the baseline by more than the user's threshold, and
2. statistically significantly slower, according to a one-sided
   Mann-Whitney U test on the per-call samples.

Shared CI runners easily vary 10-20% between runs, so a threshold alone fails
builds at random; the significance test filters out that noise.
"""

import math
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from functools import cache
from typing import Any

#: Fewer samples than this on either side: no significance claim is made.
MIN_SAMPLES = 5
#: Use the exact U distribution when both samples are at most this size and untied.
EXACT_MAX_SIZE = 20

#: Metrics a ``--async-bench-compare-fail`` expression may refer to (lower is better).
COMPARABLE_METRICS = ("min", "max", "mean", "median", "p50", "p75", "p90", "p95", "p99")

_FAIL_EXPR_RE = re.compile(
    r"^(?P<metric>[a-z0-9]+):(?P<value>\d+(?:\.\d+)?)(?P<pct>%)?$"
)


# ---------------------------------------------------------------------------
# Mann-Whitney U test
# ---------------------------------------------------------------------------


def _rank(values: Sequence[float]) -> tuple[list[float], list[int]]:
    """Return average ranks (1-based) and the sizes of tie groups."""
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    ties: list[int] = []
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        average = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = average
        if j > i:
            ties.append(j - i + 1)
        i = j + 1
    return ranks, ties


@cache
def _u_counts(n1: int, n2: int) -> tuple[int, ...]:
    """Number of arrangements yielding each U statistic value 0..n1*n2."""
    if n1 == 0 or n2 == 0:
        return (1,)
    # Recurrence: the largest value belongs to sample 1 (adds n2 to U) or to sample 2.
    with_first = _u_counts(n1 - 1, n2)
    with_second = _u_counts(n1, n2 - 1)
    counts = [0] * (n1 * n2 + 1)
    for u, count in enumerate(with_first):
        counts[u + n2] += count
    for u, count in enumerate(with_second):
        counts[u] += count
    return tuple(counts)


def mann_whitney_u(
    x: Sequence[float], y: Sequence[float], alternative: str = "greater"
) -> tuple[float, float]:
    """One-sided Mann-Whitney U test.

    ``alternative="greater"`` tests whether values in ``x`` tend to be larger
    than values in ``y``; ``"less"`` tests the opposite.

    Returns ``(U, p_value)`` where ``U`` is the statistic for ``x``. Uses the
    exact distribution for small untied samples and the normal approximation
    (with tie and continuity correction) otherwise, like SciPy's ``"auto"``.
    """
    if alternative not in ("greater", "less"):
        raise ValueError("alternative must be 'greater' or 'less'")
    n1, n2 = len(x), len(y)
    if n1 == 0 or n2 == 0:
        raise ValueError("both samples must be non-empty")

    ranks, ties = _rank([*x, *y])
    u1 = sum(ranks[:n1]) - n1 * (n1 + 1) / 2

    if not ties and n1 <= EXACT_MAX_SIZE and n2 <= EXACT_MAX_SIZE:
        counts = _u_counts(n1, n2)
        total = sum(counts)
        u = round(u1)
        if alternative == "greater":
            p = sum(counts[u:]) / total
        else:
            p = sum(counts[: u + 1]) / total
        return u1, min(1.0, p)

    n = n1 + n2
    mean_u = n1 * n2 / 2
    tie_term = sum(t**3 - t for t in ties) / (n * (n - 1))
    variance = n1 * n2 / 12 * ((n + 1) - tie_term)
    if variance <= 0:
        return u1, 1.0  # every value identical: no evidence either way
    sigma = math.sqrt(variance)
    if alternative == "greater":
        z = (u1 - mean_u - 0.5) / sigma
        p = 0.5 * math.erfc(z / math.sqrt(2))
    else:
        z = (u1 - mean_u + 0.5) / sigma
        p = 0.5 * math.erfc(-z / math.sqrt(2))
    return u1, min(1.0, max(0.0, p))


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FailThreshold:
    """A ``--async-bench-compare-fail`` expression such as ``median:10%``."""

    metric: str
    value: float
    percent: bool

    @classmethod
    def parse(cls, expression: str) -> "FailThreshold":
        match = _FAIL_EXPR_RE.match(expression.strip().lower())
        if not match or match["metric"] not in COMPARABLE_METRICS:
            raise ValueError(
                f"Invalid compare-fail expression {expression!r}. Expected "
                "METRIC:PERCENT% or METRIC:SECONDS, e.g. 'median:10%' or "
                f"'p95:0.002'. Metrics: {', '.join(COMPARABLE_METRICS)}"
            )
        return cls(match["metric"], float(match["value"]), bool(match["pct"]))

    def exceeded(self, baseline: float, current: float) -> bool:
        if self.percent:
            if baseline <= 0:
                return False
            return (current - baseline) / baseline * 100 > self.value
        return current - baseline > self.value

    def __str__(self) -> str:
        return f"{self.metric}:{self.value:g}{'%' if self.percent else 's'}"


# ---------------------------------------------------------------------------
# Comparing runs
# ---------------------------------------------------------------------------

# Status values of a BenchmarkComparison.
REGRESSION = "regression"
SLOWER = "slower"
FASTER = "faster"
UNCHANGED = "unchanged"
INSUFFICIENT = "insufficient samples"
NEW = "new"


@dataclass
class BenchmarkComparison:
    """How one benchmark compares with its baseline."""

    fullname: str
    status: str
    baseline_median: float | None = None
    current_median: float | None = None
    p_slower: float | None = None
    p_faster: float | None = None
    failed_thresholds: list[str] = field(default_factory=list)

    @property
    def change(self) -> float | None:
        """Relative change of the median (0.1 means 10% slower)."""
        if not self.baseline_median or self.current_median is None:
            return None
        return (self.current_median - self.baseline_median) / self.baseline_median


def compare_benchmark(
    fullname: str,
    current: dict[str, Any],
    baseline: dict[str, Any] | None,
    thresholds: Sequence[FailThreshold] = (),
    alpha: float = 0.05,
) -> BenchmarkComparison:
    """Compare one current benchmark record against its baseline record.

    Both records use the saved JSON shape: ``{"stats": {...}, "samples": [...]}``.
    """
    current_stats = current["stats"]
    if baseline is None:
        return BenchmarkComparison(
            fullname, NEW, current_median=current_stats.get("median")
        )

    baseline_stats = baseline["stats"]
    comparison = BenchmarkComparison(
        fullname,
        UNCHANGED,
        baseline_median=baseline_stats.get("median"),
        current_median=current_stats.get("median"),
    )

    current_samples = current.get("samples") or []
    baseline_samples = baseline.get("samples") or []
    if len(current_samples) < MIN_SAMPLES or len(baseline_samples) < MIN_SAMPLES:
        comparison.status = INSUFFICIENT
        return comparison

    _, comparison.p_slower = mann_whitney_u(
        current_samples, baseline_samples, "greater"
    )
    _, comparison.p_faster = mann_whitney_u(current_samples, baseline_samples, "less")

    significantly_slower = comparison.p_slower < alpha
    if significantly_slower:
        comparison.status = SLOWER
        for threshold in thresholds:
            base_value = baseline_stats.get(threshold.metric)
            cur_value = current_stats.get(threshold.metric)
            if base_value is None or cur_value is None:
                continue
            if threshold.exceeded(base_value, cur_value):
                comparison.failed_thresholds.append(str(threshold))
        if comparison.failed_thresholds:
            comparison.status = REGRESSION
    elif comparison.p_faster < alpha:
        comparison.status = FASTER
    return comparison


def compare_reports(
    current: dict[str, Any],
    baseline: dict[str, Any],
    thresholds: Sequence[FailThreshold] = (),
    alpha: float = 0.05,
) -> list[BenchmarkComparison]:
    """Compare every benchmark in ``current`` with the same one in ``baseline``."""
    baseline_by_name = {
        record["fullname"]: record for record in baseline.get("benchmarks", [])
    }
    return [
        compare_benchmark(
            record["fullname"],
            record,
            baseline_by_name.get(record["fullname"]),
            thresholds,
            alpha,
        )
        for record in current.get("benchmarks", [])
    ]
