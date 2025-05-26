"""Demo tests showing pytest-async-benchmark in action."""

import asyncio
import pytest


async def fast_async_operation():
    """A fast async operation for benchmarking."""
    await asyncio.sleep(0.001)
    return "fast result"


async def slow_async_operation():
    """A slower async operation for benchmarking."""
    await asyncio.sleep(0.005)
    return "slow result"


async def async_computation(n: int):
    """Async computation with parameter."""
    await asyncio.sleep(0.001)
    return sum(range(n))


def test_demo_fast_operation(async_benchmark):
    """Benchmark a fast async operation."""
    result = async_benchmark(fast_async_operation, rounds=5, iterations=3)
    assert result["mean"] < 0.01


def test_demo_slow_operation(async_benchmark):
    """Benchmark a slower async operation."""
    result = async_benchmark(slow_async_operation, rounds=3, iterations=2)
    assert result["mean"] > 0.004


def test_demo_computation_with_params(async_benchmark):
    """Benchmark async computation with parameters."""
    result = async_benchmark(async_computation, 100, rounds=4)
    assert result["rounds"] == 4


@pytest.mark.async_benchmark
def test_demo_marked_operation(async_benchmark):
    """Test with async_benchmark marker."""
    result = async_benchmark(fast_async_operation, rounds=2)
    assert result is not None
