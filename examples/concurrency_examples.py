"""Concurrency benchmarking with async_benchmark.concurrent().

Each example shows a classic async performance bug that is invisible when you
benchmark one call at a time, and how the concurrent benchmark exposes it.

These measure how your code behaves under concurrency in this process and
event loop. They are not load tests of a deployed service.

Run with:
    uv run pytest examples/concurrency_examples.py -v -s
"""

import asyncio
import time

import pytest


class ConnectionPool:
    """A tiny pool: at most `size` queries run at once, the rest wait."""

    def __init__(self, size: int):
        self._slots = asyncio.Semaphore(size)

    async def query(self) -> dict:
        async with self._slots:
            await asyncio.sleep(0.005)  # 5ms query
            return {"ok": True}


@pytest.mark.asyncio
async def test_pool_starvation(async_benchmark):
    """A pool smaller than your concurrency makes callers queue up.

    One call at a time, both pools take ~5ms. Under 20 concurrent callers,
    the 2-connection pool's tail latency balloons because calls wait for a slot.
    """
    small_pool = ConnectionPool(size=2)
    big_pool = ConnectionPool(size=20)

    starved = await async_benchmark.concurrent(
        small_pool.query, concurrency=20, total=200
    )
    healthy = await async_benchmark.concurrent(
        big_pool.query, concurrency=20, total=200
    )

    assert healthy["p95"] < 0.05
    assert starved["p95"] > healthy["p95"] * 3  # queueing shows up in the tail
    assert healthy["throughput"] > starved["throughput"]


@pytest.mark.asyncio
async def test_accidental_serialization(async_benchmark):
    """A lock held around I/O makes concurrent callers run one at a time."""
    lock = asyncio.Lock()

    async def fetch_with_global_lock():
        async with lock:  # oops: the lock covers the slow I/O
            await asyncio.sleep(0.002)

    async def fetch_without_lock():
        await asyncio.sleep(0.002)

    serialized = await async_benchmark.concurrent(
        fetch_with_global_lock, concurrency=10, total=100
    )
    parallel = await async_benchmark.concurrent(
        fetch_without_lock, concurrency=10, total=100
    )

    assert parallel["throughput"] > serialized["throughput"] * 3


@pytest.mark.asyncio
async def test_blocking_call_stalls_the_event_loop(async_benchmark):
    """A sync call inside async code (time.sleep, sync DB driver, heavy CPU)
    blocks every other task. Event loop lag makes it visible."""

    async def handler_with_blocking_call():
        await asyncio.sleep(0.001)
        time.sleep(0.01)  # e.g. requests.get() or a sync driver call

    result = await async_benchmark.concurrent(
        handler_with_blocking_call, concurrency=10, total=50
    )

    # The loop was stuck for ~10ms at a time: a healthy loop lags < 1-2ms.
    assert result["loop_lag_max"] > 0.005


@pytest.mark.asyncio
async def test_timeouts_and_errors_are_part_of_the_result(async_benchmark):
    """Under load, failures matter as much as latency."""
    pool = ConnectionPool(size=1)

    async def query_with_slow_pool():
        return await pool.query()

    result = await async_benchmark.concurrent(
        query_with_slow_pool, concurrency=10, total=50, timeout=0.02
    )

    # With one connection and 10 callers, many calls can't get a slot in 20ms.
    assert result["timeouts"] > 0
    assert result["completed"] + result["timeouts"] + result["errors"] == 50
