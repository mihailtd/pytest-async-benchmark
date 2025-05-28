"""
Backwards Compatibility Examples

This file demonstrates pytest-async-benchmark's backwards compatibility,
showing both the modern async interface (with pytest-asyncio) and the
legacy sync interface (without pytest-asyncio).
"""

import asyncio

import pytest


async def fast_operation():
    """A fast async operation for testing."""
    await asyncio.sleep(0.001)  # 1ms
    return "fast_result"


async def slow_operation():
    """A slower async operation for testing."""
    await asyncio.sleep(0.01)  # 10ms
    return "slow_result"


# =============================================================================
# MODERN ASYNC INTERFACE (with pytest-asyncio)
# =============================================================================


@pytest.mark.asyncio
async def test_modern_async_basic(async_benchmark):
    """Modern async interface - basic usage."""
    result = await async_benchmark(fast_operation)
    assert "mean" in result


@pytest.mark.asyncio
async def test_modern_async_with_params(async_benchmark):
    """Modern async interface - with custom parameters."""
    result = await async_benchmark(fast_operation, rounds=3, iterations=5)
    assert result["rounds"] == 3
    assert result["iterations"] == 5


@pytest.mark.asyncio
@pytest.mark.async_benchmark(rounds=4, iterations=3)
async def test_modern_async_with_marker(async_benchmark):
    """Modern async interface - with marker configuration."""
    result = await async_benchmark(fast_operation)
    assert result["rounds"] == 4
    assert result["iterations"] == 3


@pytest.mark.asyncio
@pytest.mark.async_benchmark(rounds=2, iterations=2)
async def test_modern_async_parameter_override(async_benchmark):
    """Modern async interface - function params override marker."""
    result = await async_benchmark(fast_operation, rounds=5)
    assert result["rounds"] == 5
    assert result["iterations"] == 2


# =============================================================================
# LEGACY SYNC INTERFACE (backwards compatible)
# =============================================================================


def test_legacy_sync_basic(async_benchmark):
    """Legacy sync interface - basic usage (no await needed)."""
    result = async_benchmark(fast_operation)
    assert "mean" in result


def test_legacy_sync_with_params(async_benchmark):
    """Legacy sync interface - with custom parameters."""
    result = async_benchmark(fast_operation, rounds=3, iterations=5)
    assert result["rounds"] == 3
    assert result["iterations"] == 5


@pytest.mark.async_benchmark(rounds=4, iterations=3)
def test_legacy_sync_with_marker(async_benchmark):
    """Legacy sync interface - with marker configuration."""
    result = async_benchmark(fast_operation)
    assert result["rounds"] == 4
    assert result["iterations"] == 3


@pytest.mark.async_benchmark(rounds=2, iterations=2)
def test_legacy_sync_parameter_override(async_benchmark):
    """Legacy sync interface - function params override marker."""
    result = async_benchmark(fast_operation, rounds=5)
    assert result["rounds"] == 5
    assert result["iterations"] == 2


# =============================================================================
# COMPARISON EXAMPLES
# =============================================================================


def test_sync_comparison_example(async_benchmark):
    """Example showing how to compare different async functions (sync style)."""
    fast_result = async_benchmark(fast_operation, rounds=3, iterations=5)
    slow_result = async_benchmark(slow_operation, rounds=3, iterations=5)

    assert fast_result["mean"] < slow_result["mean"]
    print(f"Fast operation: {fast_result['mean']:.4f}s")
    print(f"Slow operation: {slow_result['mean']:.4f}s")
    print(f"Speedup: {slow_result['mean'] / fast_result['mean']:.2f}x")


@pytest.mark.asyncio
async def test_async_comparison_example(async_benchmark):
    """Example showing how to compare different async functions (async style)."""
    fast_result = await async_benchmark(fast_operation, rounds=3, iterations=5)
    slow_result = await async_benchmark(slow_operation, rounds=3, iterations=5)

    assert fast_result["mean"] < slow_result["mean"]
    print(f"Fast operation: {fast_result['mean']:.4f}s")
    print(f"Slow operation: {slow_result['mean']:.4f}s")
    print(f"Speedup: {slow_result['mean'] / fast_result['mean']:.2f}x")


# =============================================================================
# ERROR HANDLING EXAMPLES
# =============================================================================


def test_sync_error_handling(async_benchmark):
    """Test error handling in sync interface."""

    def sync_function():
        return "not async"

    with pytest.raises(ValueError, match="Function must be async"):
        async_benchmark(sync_function)


@pytest.mark.asyncio
async def test_async_error_handling(async_benchmark):
    """Test error handling in async interface."""

    def sync_function():
        return "not async"

    with pytest.raises(ValueError, match="Function must be async"):
        await async_benchmark(sync_function)


# =============================================================================
# MIXED USAGE DEMONSTRATION
# =============================================================================


class TestMixedUsage:
    """Demonstrate mixed usage patterns in the same test class."""

    def test_sync_in_class(self, async_benchmark):
        """Sync interface usage in test class."""
        result = async_benchmark(fast_operation, rounds=2)
        assert result["rounds"] == 2

    @pytest.mark.asyncio
    async def test_async_in_class(self, async_benchmark):
        """Async interface usage in test class."""
        result = await async_benchmark(fast_operation, rounds=2)
        assert result["rounds"] == 2


if __name__ == "__main__":
    print("Running backwards compatibility demonstrations...")
    print("Note: Run with pytest to see the actual benchmark results")
