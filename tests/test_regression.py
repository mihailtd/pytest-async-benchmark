"""Tests for noise-aware run comparison (Mann-Whitney U + thresholds)."""

import random

import pytest

from pytest_async_benchmark import regression
from pytest_async_benchmark.regression import (
    FailThreshold,
    compare_benchmark,
    compare_reports,
    mann_whitney_u,
)
from pytest_async_benchmark.stats import compute_stats


def record(samples):
    return {"stats": compute_stats(samples), "samples": list(samples)}


def noisy(center, n, seed, spread=0.1):
    rng = random.Random(seed)
    return [center * (1 + rng.uniform(-spread, spread)) for _ in range(n)]


class TestMannWhitney:
    def test_clearly_greater(self):
        _, p = mann_whitney_u([10, 11, 12, 13, 14], [1, 2, 3, 4, 5], "greater")
        assert p == pytest.approx(1 / 252)  # exact: one arrangement in C(10, 5)

    def test_clearly_less(self):
        _, p = mann_whitney_u([1, 2, 3, 4, 5], [10, 11, 12, 13, 14], "less")
        assert p == pytest.approx(1 / 252)

    def test_wrong_direction_gives_high_p(self):
        _, p = mann_whitney_u([1, 2, 3, 4, 5], [10, 11, 12, 13, 14], "greater")
        assert p == 1.0

    def test_large_samples_use_normal_approximation(self):
        _, p = mann_whitney_u(noisy(1.2, 200, 1), noisy(1.0, 200, 2), "greater")
        assert p < 1e-10

    def test_all_identical_values(self):
        _, p = mann_whitney_u([1.0] * 30, [1.0] * 30, "greater")
        assert p == 1.0

    def test_u_statistic(self):
        u, _ = mann_whitney_u([3, 4], [1, 2, 5], "greater")
        assert u == 4  # 3>1, 3>2, 4>1, 4>2

    def test_invalid_alternative(self):
        with pytest.raises(ValueError):
            mann_whitney_u([1], [2], "two-sided")


class TestFailThreshold:
    def test_parse_percent(self):
        threshold = FailThreshold.parse("median:10%")
        assert threshold == FailThreshold("median", 10.0, True)
        assert threshold.exceeded(1.0, 1.11)
        assert not threshold.exceeded(1.0, 1.09)

    def test_parse_absolute_seconds(self):
        threshold = FailThreshold.parse("p95:0.002")
        assert threshold == FailThreshold("p95", 0.002, False)
        assert threshold.exceeded(0.010, 0.0125)
        assert not threshold.exceeded(0.010, 0.0115)

    @pytest.mark.parametrize("expr", ["median", "median:", "fast:10%", "mean:-5%"])
    def test_rejects_invalid(self, expr):
        with pytest.raises(ValueError, match="compare-fail"):
            FailThreshold.parse(expr)


class TestCompareBenchmark:
    def test_new_benchmark(self):
        result = compare_benchmark("t", record(noisy(1, 20, 1)), None)
        assert result.status == regression.NEW

    def test_insufficient_samples(self):
        result = compare_benchmark("t", record([1.0, 2.0]), record(noisy(1, 20, 1)))
        assert result.status == regression.INSUFFICIENT

    def test_noise_is_not_a_regression(self):
        """Same distribution, different random draws: no significant change."""
        thresholds = [FailThreshold.parse("median:1%")]
        result = compare_benchmark(
            "t", record(noisy(1.0, 50, 1)), record(noisy(1.0, 50, 2)), thresholds
        )
        assert result.status == regression.UNCHANGED

    def test_significant_slowdown_beyond_threshold_is_a_regression(self):
        thresholds = [FailThreshold.parse("median:10%")]
        result = compare_benchmark(
            "t", record(noisy(1.3, 50, 1)), record(noisy(1.0, 50, 2)), thresholds
        )
        assert result.status == regression.REGRESSION
        assert result.failed_thresholds == ["median:10%"]
        assert result.change == pytest.approx(0.3, abs=0.05)

    def test_significant_slowdown_within_threshold_is_only_slower(self):
        thresholds = [FailThreshold.parse("median:50%")]
        result = compare_benchmark(
            "t", record(noisy(1.3, 50, 1)), record(noisy(1.0, 50, 2)), thresholds
        )
        assert result.status == regression.SLOWER

    def test_slowdown_without_thresholds_is_only_slower(self):
        result = compare_benchmark(
            "t", record(noisy(1.3, 50, 1)), record(noisy(1.0, 50, 2))
        )
        assert result.status == regression.SLOWER

    def test_faster(self):
        result = compare_benchmark(
            "t", record(noisy(0.7, 50, 1)), record(noisy(1.0, 50, 2))
        )
        assert result.status == regression.FASTER

    def test_compare_reports_matches_by_fullname(self):
        current = {
            "benchmarks": [
                {"fullname": "a", **record(noisy(1.0, 20, 1))},
                {"fullname": "b", **record(noisy(1.0, 20, 2))},
            ]
        }
        baseline = {"benchmarks": [{"fullname": "a", **record(noisy(1.0, 20, 3))}]}
        results = {c.fullname: c.status for c in compare_reports(current, baseline)}
        assert results["b"] == regression.NEW
        assert results["a"] != regression.NEW
