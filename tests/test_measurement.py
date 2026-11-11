"""Tests for per-call timing, percentiles and round calibration."""

import asyncio

import pytest

from pytest_async_benchmark.runner import AsyncBenchmarkRunner
from pytest_async_benchmark.stats import PERCENTILES, compute_stats, percentile


async def tiny_sleep():
    await asyncio.sleep(0.001)


class TestPercentile:
    def test_known_values(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        assert percentile(values, 0) == 1.0
        assert percentile(values, 50) == 3.0
        assert percentile(values, 100) == 5.0
        assert percentile(values, 25) == 2.0
        assert percentile(values, 90) == pytest.approx(4.6)

    def test_single_value(self):
        assert percentile([7.0], 99) == 7.0

    def test_rejects_bad_input(self):
        with pytest.raises(ValueError):
            percentile([], 50)
        with pytest.raises(ValueError):
            percentile([1.0], 101)


class TestComputeStats:
    def test_keys_and_ordering(self):
        stats = compute_stats([0.005, 0.001, 0.003, 0.002, 0.004])
        for pct in PERCENTILES:
            assert f"p{pct}" in stats
        assert stats["min"] == 0.001
        assert stats["max"] == 0.005
        assert stats["median"] == stats["p50"] == 0.003
        assert stats["min"] <= stats["p50"] <= stats["p95"] <= stats["p99"]
        assert stats["p99"] <= stats["max"]
        assert stats["count"] == 5
        assert stats["ops"] == pytest.approx(1 / 0.003)
        assert stats["total_time"] == pytest.approx(0.015)

    def test_single_sample_has_zero_stddev(self):
        assert compute_stats([0.5])["stddev"] == 0.0


class TestPerCallSamples:
    @pytest.mark.asyncio
    async def test_every_call_is_a_sample(self, async_benchmark):
        result = await async_benchmark(tiny_sleep, rounds=4, iterations=3)

        assert len(result["samples"]) == 12
        assert result["count"] == 12
        # raw_times keeps its pre-0.4 meaning: one mean per round
        assert len(result["raw_times"]) == 4
        assert result["rounds"] == 4
        assert result["iterations"] == 3
        assert result["calibrated"] is False

    @pytest.mark.asyncio
    async def test_stats_come_from_samples(self, async_benchmark):
        result = await async_benchmark(tiny_sleep, rounds=10)

        assert result["min"] == min(result["samples"])
        assert result["max"] == max(result["samples"])
        assert result["p50"] <= result["p95"] <= result["p99"] <= result["max"]

    @pytest.mark.asyncio
    async def test_pedantic_reports_percentiles(self, async_benchmark):
        result = await async_benchmark.pedantic(
            tiny_sleep, setup=lambda: None, rounds=3, iterations=2
        )
        assert result["mode"] == "pedantic"
        assert len(result["samples"]) == 6
        assert "p99" in result


class TestCalibration:
    @pytest.mark.asyncio
    async def test_rounds_fill_time_budget(self):
        runner = AsyncBenchmarkRunner(max_time=0.1)
        result = await runner.run(tiny_sleep)

        assert result["calibrated"] is True
        assert result["rounds"] > 5  # ~1ms per call fits many rounds in 100ms
        assert result["total_time"] < 0.5

    @pytest.mark.asyncio
    async def test_minimum_rounds_respected(self):
        runner = AsyncBenchmarkRunner(max_time=0)
        result = await runner.run(tiny_sleep)
        assert result["rounds"] == 5

    @pytest.mark.asyncio
    async def test_maximum_rounds_respected(self):
        async def noop():
            pass

        runner = AsyncBenchmarkRunner(max_time=10, max_rounds=50)
        result = await runner.run(noop)
        assert result["rounds"] == 50

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark(max_time=0)
    async def test_max_time_from_marker(self, async_benchmark):
        result = await async_benchmark(tiny_sleep)
        assert result["calibrated"] is True
        assert result["rounds"] == 5

    @pytest.mark.asyncio
    async def test_invalid_rounds(self):
        with pytest.raises(ValueError):
            AsyncBenchmarkRunner(rounds=0)
