#!/usr/bin/env python3
"""
pytest-async-benchmark Marker Syntax Examples

This example demonstrates both ways to configure benchmark parameters:
1. Using @pytest.mark.async_benchmark(rounds=X, iterations=Y) marker
2. Using function parameters in async_benchmark() call
"""

import asyncio

import pytest


async def simple_async_task():
    """A simple async task for benchmarking."""
    await asyncio.sleep(0.001)
    return "completed"


async def database_query():
    """Simulate a database query."""
    await asyncio.sleep(0.002)
    return {"id": 1, "name": "user"}


class TestMarkerSyntax:
    """Test class demonstrating different parameter syntax options."""

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark(rounds=10, iterations=100)
    async def test_with_marker_parameters(self, async_benchmark):
        """Benchmark using marker parameters (preferred for consistent configs)."""
        result = await async_benchmark(simple_async_task)

        assert result["rounds"] == 10
        assert result["iterations"] == 100

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark(rounds=5, iterations=50, warmup_rounds=2)
    async def test_with_marker_and_warmup(self, async_benchmark):
        """Benchmark with marker including warmup rounds."""
        result = await async_benchmark(database_query)

        assert result["rounds"] == 5
        assert result["iterations"] == 50

    @pytest.mark.asyncio
    async def test_with_function_parameters(self, async_benchmark):
        """Benchmark using function parameters (good for dynamic configs)."""
        result = await async_benchmark(
            simple_async_task, rounds=8, iterations=75, warmup_rounds=1
        )

        assert result["rounds"] == 8
        assert result["iterations"] == 75

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark(rounds=5, iterations=25)
    async def test_function_params_override_marker(self, async_benchmark):
        """Function parameters override marker parameters."""
        result = await async_benchmark(
            simple_async_task,
            rounds=12,
            iterations=30,
        )

        assert result["rounds"] == 12
        assert result["iterations"] == 30

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark(rounds=6, iterations=40)
    async def test_partial_override(self, async_benchmark):
        """Partially override marker parameters."""
        result = await async_benchmark(
            simple_async_task,
            rounds=15,
        )

        assert result["rounds"] == 15
        assert result["iterations"] == 40


class TestPerformanceConfigurations:
    """Examples of different performance testing configurations."""

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark(rounds=20, iterations=200)
    async def test_high_precision_benchmark(self, async_benchmark):
        """High precision benchmark for critical performance measurements."""
        result = await async_benchmark(simple_async_task)

        assert result["rounds"] == 20
        assert result["iterations"] == 200

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark(rounds=3, iterations=10)
    async def test_quick_smoke_test(self, async_benchmark):
        """Quick smoke test for basic performance verification."""
        result = await async_benchmark(database_query)

        assert result["rounds"] == 3
        assert result["iterations"] == 10

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark(rounds=10, iterations=100, warmup_rounds=5)
    async def test_with_extensive_warmup(self, async_benchmark):
        """Benchmark with extensive warmup for JIT optimization scenarios."""
        result = await async_benchmark(simple_async_task)

        assert result["rounds"] == 10
        assert result["iterations"] == 100


if __name__ == "__main__":
    print("🎯 pytest-async-benchmark Marker Syntax Examples")
    print("=" * 55)
    print()
    print("Demonstrates two ways to configure benchmarks:")
    print("1. @pytest.mark.async_benchmark(rounds=X, iterations=Y)")
    print("2. await async_benchmark(func, rounds=X, iterations=Y)")
    print()
    print("To run these examples:")
    print("  pytest examples/marker_syntax_examples.py -v")
