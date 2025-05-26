"""Test configuration for pytest-async-benchmark."""

import pytest


@pytest.fixture
def sample_async_func():
    """Sample async function for testing."""

    async def slow_async_operation():
        import asyncio

        await asyncio.sleep(0.01)
        return "result"

    return slow_async_operation
