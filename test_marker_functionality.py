#!/usr/bin/env python3
"""
Test file to verify marker parameter extraction functionality.
"""

import asyncio

import pytest


async def simple_task():
    """A simple async task for testing."""
    await asyncio.sleep(0.001)
    return "done"


class TestMarkerFunctionality:
    """Test marker parameter extraction."""

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark(rounds=8, iterations=12)
    async def test_with_marker_parameters(self, async_benchmark):
        """Test using marker parameters."""
        result = await async_benchmark(simple_task)

        assert result["rounds"] == 8
        assert result["iterations"] == 12
        print(
            f"✅ Marker test passed: rounds={result['rounds']}, iterations={result['iterations']}"
        )

    @pytest.mark.asyncio
    async def test_with_function_parameters(self, async_benchmark):
        """Test using function parameters."""
        result = await async_benchmark(simple_task, rounds=5, iterations=7)

        assert result["rounds"] == 5
        assert result["iterations"] == 7
        print(
            f"✅ Function test passed: rounds={result['rounds']}, iterations={result['iterations']}"
        )

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark(rounds=10, iterations=15)
    async def test_function_overrides_marker(self, async_benchmark):
        """Test that function parameters override marker parameters."""
        result = await async_benchmark(simple_task, rounds=3)  # Override rounds only

        assert result["rounds"] == 3  # From function
        assert result["iterations"] == 15  # From marker
        print(
            f"✅ Override test passed: rounds={result['rounds']}, iterations={result['iterations']}"
        )
