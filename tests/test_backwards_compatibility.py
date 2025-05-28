"""Test backwards compatibility for both sync and async interfaces."""

import asyncio

import pytest


async def sample_async_function():
    """Sample async function for testing."""
    await asyncio.sleep(0.01)
    return "completed"


def test_sync_interface_basic(async_benchmark):
    """Test that sync interface works without await."""
    result = async_benchmark(sample_async_function)

    assert "mean" in result
    assert "min" in result
    assert "max" in result
    assert result["rounds"] > 0
    assert result["iterations"] > 0


def test_sync_interface_with_parameters(async_benchmark):
    """Test sync interface with custom parameters."""
    result = async_benchmark(sample_async_function, rounds=2, iterations=3)

    assert result["rounds"] == 2
    assert result["iterations"] == 3
    assert result["mean"] > 0


@pytest.mark.async_benchmark(rounds=3, iterations=2)
def test_sync_interface_with_marker(async_benchmark):
    """Test sync interface with marker parameters."""
    result = async_benchmark(sample_async_function)

    assert result["rounds"] == 3
    assert result["iterations"] == 2


def test_sync_interface_parameter_precedence(async_benchmark):
    """Test that function parameters override marker parameters."""

    @pytest.mark.async_benchmark(rounds=5, iterations=4)
    def test_function():
        result = async_benchmark(sample_async_function, rounds=2, iterations=3)
        assert result["rounds"] == 2
        assert result["iterations"] == 3

    result = async_benchmark(sample_async_function, rounds=2, iterations=3)
    assert result["rounds"] == 2
    assert result["iterations"] == 3


def test_non_async_function_raises_error(async_benchmark):
    """Test that non-async functions raise ValueError."""

    def sync_function():
        return "sync"

    with pytest.raises(ValueError, match="Function must be async"):
        async_benchmark(sync_function)


def test_result_has_required_fields(async_benchmark):
    """Test that result contains all required benchmark fields."""
    result = async_benchmark(sample_async_function)

    required_fields = ["min", "max", "mean", "median", "stddev", "rounds", "iterations"]
    for field in required_fields:
        assert field in result, f"Missing required field: {field}"

    for time_field in ["min", "max", "mean", "median", "stddev"]:
        assert isinstance(result[time_field], (int, float)), (
            f"{time_field} should be numeric"
        )
        assert result[time_field] >= 0, f"{time_field} should be non-negative"

    assert isinstance(result["rounds"], int)
    assert isinstance(result["iterations"], int)
    assert result["rounds"] > 0
    assert result["iterations"] > 0
