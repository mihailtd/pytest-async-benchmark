"""Tests for pytest-async-benchmark."""

import asyncio

import pytest


async def sample_async_function():
    """Sample async function for benchmarking."""
    await asyncio.sleep(0.001)
    return 42


@pytest.mark.asyncio
async def test_async_benchmark_basic(async_benchmark):
    """Test basic async benchmarking functionality."""
    result = await async_benchmark(sample_async_function, rounds=3, iterations=2)

    assert "min" in result
    assert "max" in result
    assert "mean" in result
    assert "median" in result
    assert "stddev" in result
    assert result["rounds"] == 3
    assert result["iterations"] == 2
    assert result["min"] > 0
    assert result["max"] >= result["min"]


@pytest.mark.asyncio
async def test_async_benchmark_with_params(async_benchmark):
    """Test async benchmarking with function parameters."""

    async def async_add(a, b):
        await asyncio.sleep(0.001)
        return a + b

    result = await async_benchmark(async_add, 5, 10, rounds=2)

    assert result["rounds"] == 2
    assert result["min"] > 0


@pytest.mark.asyncio
async def test_async_benchmark_raises_on_sync_function(async_benchmark):
    """Test that sync functions raise an error."""

    def sync_function():
        return "sync"

    with pytest.raises(ValueError, match="Function must be async"):
        await async_benchmark(sync_function)


@pytest.mark.async_benchmark
@pytest.mark.asyncio
async def test_marked_benchmark(async_benchmark):
    """Test with async_benchmark marker."""

    async def marked_function():
        await asyncio.sleep(0.001)
        return "marked"

    result = await async_benchmark(marked_function, rounds=2)
    assert result is not None
