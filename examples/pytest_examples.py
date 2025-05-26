#!/usr/bin/env python3
"""
Comprehensive example demonstrating pytest-async-benchmark usage.

This example shows how to benchmark various types of async operations:
- Simple async functions
- Functions with parameters
- Async context managers
- Error handling
- Performance assertions
"""

import asyncio
import pytest


async def simple_delay(ms: float = 1.0):
    """Simple async function with configurable delay."""
    await asyncio.sleep(ms / 1000)
    return f"Delayed {ms}ms"


async def cpu_bound_async(n: int = 1000):
    """CPU-bound operation in async function."""
    await asyncio.sleep(0)
    total = sum(i * i for i in range(n))
    return total


async def fetch_data_simulation(items: int = 10, delay_per_item: float = 0.1):
    """Simulate fetching data with network delays."""
    results = []
    for i in range(items):
        await asyncio.sleep(delay_per_item / 1000)
        results.append(f"item_{i}")
    return results


async def async_context_operation():
    """Example using async context manager pattern."""

    class AsyncResource:
        async def __aenter__(self):
            await asyncio.sleep(0.001)
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await asyncio.sleep(0.001)

        async def do_work(self):
            await asyncio.sleep(0.002)
            return "work_done"

    async with AsyncResource() as resource:
        return await resource.do_work()


class TestAsyncBenchmarkExamples:
    """Example test class showing various benchmarking patterns."""

    def test_simple_function_benchmark(self, async_benchmark):
        """Benchmark a simple async function."""
        result = async_benchmark(simple_delay, 2.0, rounds=5)

        assert result["rounds"] == 5
        assert result["iterations"] == 1


        assert result["mean"] >= 0.001
        assert result["mean"] < 0.01


        assert result["stddev"] < result["mean"] * 0.5

    def test_cpu_bound_benchmark(self, async_benchmark):
        """Benchmark CPU-bound async operation."""
        result = async_benchmark(
            cpu_bound_async,
            500,
            rounds=3,
            iterations=2,
        )

        assert result["rounds"] == 3
        assert result["iterations"] == 2
        assert result["min"] > 0

    def test_data_fetching_benchmark(self, async_benchmark):
        """Benchmark simulated data fetching."""
        result = async_benchmark(
            fetch_data_simulation,
            items=5,
            delay_per_item=0.5,
            rounds=3,
        )

        assert result["mean"] > 0.001
        assert result["mean"] < 0.01

    def test_context_manager_benchmark(self, async_benchmark):
        """Benchmark async context manager operations."""
        result = async_benchmark(async_context_operation, rounds=4)

        assert result["mean"] > 0.003
        assert result["rounds"] == 4

    @pytest.mark.async_benchmark
    def test_marked_benchmark(self, async_benchmark):
        """Test with async_benchmark marker for organization."""
        result = async_benchmark(simple_delay, 1.0, rounds=2)
        assert result is not None

    def test_benchmark_with_warmup(self, async_benchmark):
        """Test with custom warmup rounds."""
        result = async_benchmark(
            simple_delay,
            1.5,
            rounds=3,
            warmup_rounds=2,
        )

        assert result["rounds"] == 3
        assert result["mean"] > 0.001

    def test_error_handling(self, async_benchmark):
        """Test that non-async functions raise appropriate errors."""

        def sync_function():
            return "not async"

        with pytest.raises(ValueError, match="Function must be async"):
            async_benchmark(sync_function)

    def test_performance_regression_detection(self, async_benchmark):
        """Example of using benchmarks for performance regression testing."""

        fast_result = async_benchmark(simple_delay, 0.5, rounds=5)

        slow_result = async_benchmark(simple_delay, 3.0, rounds=5)

        assert slow_result["mean"] > fast_result["mean"] * 2

        assert fast_result["mean"] < 0.002
        assert slow_result["mean"] < 0.005

    def test_statistical_analysis(self, async_benchmark):
        """Example showing how to analyze benchmark statistics."""
        result = async_benchmark(simple_delay, 1.0, rounds=10, iterations=3)

        assert len(result["raw_times"]) == 10
        assert result["min"] <= result["median"] <= result["max"]
        assert (
            result["min"] <= result["mean"] <= result["max"]
        )

        cv = result["stddev"] / result["mean"]
        assert cv < 0.3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
