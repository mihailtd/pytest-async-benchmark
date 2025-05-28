#!/usr/bin/env python3
"""
pytest-asyncio Integration Showcase

This example demonstrates the seamless integration between pytest-async-benchmark
and pytest-asyncio, showcasing how the two libraries work together to provide
a superior async testing and benchmarking experience.
"""

import asyncio

import pytest


async def simple_async_task():
    """A simple async task for basic benchmarking."""
    await asyncio.sleep(0.001)
    return "completed"


async def async_database_simulation():
    """Simulate an async database operation."""
    await asyncio.sleep(0.001)
    await asyncio.sleep(0.002)
    await asyncio.sleep(0.001)
    return {"user_id": 123, "name": "test_user", "email": "test@example.com"}


async def async_file_operations():
    """Simulate async file operations."""
    tasks = []
    for _i in range(3):
        task = asyncio.create_task(asyncio.sleep(0.001))
        tasks.append(task)

    await asyncio.gather(*tasks)
    return ["file1_content", "file2_content", "file3_content"]


class TestPytestAsyncioIntegration:
    """
    Test class demonstrating pytest-asyncio integration with pytest-async-benchmark.

    All these tests use the @pytest.mark.asyncio decorator and await the benchmark
    fixture, showcasing the natural async/await syntax support.
    """

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark(rounds=10, iterations=5)
    async def test_basic_async_task_benchmark(self, async_benchmark):
        """Test basic async task benchmarking using marker syntax."""
        result = await async_benchmark(simple_async_task)

        assert "mean" in result
        assert "min" in result
        assert "max" in result
        assert result["rounds"] == 10
        assert result["iterations"] == 5
        assert result["mean"] > 0

    @pytest.mark.asyncio
    async def test_database_simulation_benchmark(self, async_benchmark):
        """Benchmark simulated database operations."""
        result = await async_benchmark(
            async_database_simulation, rounds=5, iterations=3, warmup_rounds=1
        )

        assert result["mean"] < 0.01
        assert result["max"] < 0.02

    @pytest.mark.asyncio
    async def test_concurrent_file_operations_benchmark(self, async_benchmark):
        """Benchmark concurrent async file operations."""
        result = await async_benchmark(async_file_operations, rounds=5)

        assert result["mean"] < 0.005

    @pytest.mark.asyncio
    async def test_mixed_async_operations_comparison(self, async_benchmark):
        """Compare different types of async operations."""

        simple_result = await async_benchmark(simple_async_task, rounds=5)
        db_result = await async_benchmark(async_database_simulation, rounds=5)
        file_result = await async_benchmark(async_file_operations, rounds=5)

        assert simple_result["mean"] <= db_result["mean"]

        assert db_result["mean"] > simple_result["mean"]

        assert simple_result["mean"] < 0.005
        assert db_result["mean"] < 0.01
        assert file_result["mean"] < 0.01

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark
    async def test_with_both_markers(self, async_benchmark):
        """Test using both pytest.mark.asyncio and pytest.mark.async_benchmark."""
        result = await async_benchmark(simple_async_task, rounds=3)

        assert result is not None
        assert result["rounds"] == 3

    @pytest.mark.asyncio
    async def test_performance_regression_detection(self, async_benchmark):
        """Example of using async benchmarks for regression detection."""

        async def optimized_operation():
            await asyncio.sleep(0.001)
            return "optimized"

        async def unoptimized_operation():
            await asyncio.sleep(0.005)
            return "unoptimized"

        optimized_result = await async_benchmark(optimized_operation, rounds=5)
        unoptimized_result = await async_benchmark(unoptimized_operation, rounds=5)

        improvement_factor = unoptimized_result["mean"] / optimized_result["mean"]
        assert improvement_factor > 2.0

        assert optimized_result["mean"] < 0.002
        assert optimized_result["max"] < 0.003

    @pytest.mark.asyncio
    async def test_error_handling_in_async_context(self, async_benchmark):
        """Test error handling works correctly in async context."""

        def not_async_function():
            return "this is not async"

        with pytest.raises(ValueError, match="Function must be async"):
            await async_benchmark(not_async_function)

    @pytest.mark.asyncio
    async def test_async_function_with_parameters(self, async_benchmark):
        """Test benchmarking async functions with various parameter types."""

        async def parameterized_async_function(
            delay_ms: float, multiplier: int = 1, prefix: str = "result"
        ):
            await asyncio.sleep(delay_ms / 1000)
            return f"{prefix}_{multiplier * 42}"

        result = await async_benchmark(
            parameterized_async_function,
            2.0,
            multiplier=3,
            prefix="test",
            rounds=5,
        )

        assert result["rounds"] == 5
        assert result["mean"] >= 0.001


if __name__ == "__main__":
    print("🔥 pytest-asyncio Integration Showcase")
    print("=" * 50)
    print()
    print("To run the pytest benchmarks:")
    print("  pytest examples/pytest_asyncio_showcase.py -v")
    print()
    print("✅ All examples demonstrate pytest-asyncio compatibility!")
