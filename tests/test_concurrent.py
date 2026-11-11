"""Tests for concurrent benchmarking and task leak detection."""

import asyncio
import time

import pytest

from pytest_async_benchmark.plugin import TaskLeakError, TaskLeakWarning
from pytest_async_benchmark.runner import AsyncBenchmarkRunner


class InFlightCounter:
    """Async callable that records the maximum number of concurrent calls."""

    def __init__(self, delay: float = 0.002):
        self.delay = delay
        self.current = 0
        self.peak = 0
        self.calls = 0

    async def __call__(self):
        self.current += 1
        self.calls += 1
        self.peak = max(self.peak, self.current)
        try:
            await asyncio.sleep(self.delay)
        finally:
            self.current -= 1


def as_coroutine_function(obj):
    """Wrap a callable object in a real coroutine function."""

    async def call():
        return await obj()

    return call


class TestConcurrent:
    @pytest.mark.asyncio
    async def test_concurrency_and_total_are_honoured(self, async_benchmark):
        counter = InFlightCounter()
        result = await async_benchmark.concurrent(
            as_coroutine_function(counter), concurrency=8, total=80, warmup=0
        )

        assert counter.peak == 8
        assert counter.calls == 80
        assert result["completed"] == 80
        assert len(result["samples"]) == 80
        assert result["errors"] == 0
        assert result["timeouts"] == 0
        assert result["mode"] == "concurrent"
        assert result["throughput"] > 0
        assert result["p50"] <= result["p95"] <= result["p99"] <= result["max"]

    @pytest.mark.asyncio
    async def test_concurrency_is_faster_than_sequential(self, async_benchmark):
        async def io_bound():
            await asyncio.sleep(0.01)

        result = await async_benchmark.concurrent(
            io_bound, concurrency=20, total=40, warmup=0
        )
        # 40 x 10ms sequentially would take 400ms; 20 at a time takes ~20ms
        assert result["wall_time"] < 0.2

    @pytest.mark.asyncio
    async def test_concurrency_capped_to_total(self, async_benchmark):
        counter = InFlightCounter()
        result = await async_benchmark.concurrent(
            as_coroutine_function(counter), concurrency=50, total=5, warmup=0
        )
        assert result["concurrency"] == 5
        assert counter.calls == 5

    @pytest.mark.asyncio
    async def test_warmup_calls_are_not_measured(self, async_benchmark):
        counter = InFlightCounter()
        result = await async_benchmark.concurrent(
            as_coroutine_function(counter), concurrency=4, total=20, warmup=6
        )
        assert counter.calls == 26
        assert result["completed"] == 20

    @pytest.mark.asyncio
    async def test_errors_counted_separately(self, async_benchmark):
        calls = 0

        async def flaky():
            nonlocal calls
            calls += 1
            call_number = calls  # read before awaiting: other workers bump it
            await asyncio.sleep(0)
            if call_number % 4 == 0:
                raise ConnectionError("pool exhausted")

        result = await async_benchmark.concurrent(
            flaky, concurrency=4, total=40, warmup=0
        )
        assert result["errors"] == 10
        assert result["completed"] == 30
        assert result["error_types"] == {"ConnectionError": 10}
        assert "pool exhausted" in result["first_error"]

    @pytest.mark.asyncio
    async def test_timeouts_counted_separately(self, async_benchmark):
        calls = 0

        async def sometimes_slow():
            nonlocal calls
            calls += 1
            await asyncio.sleep(0.2 if calls % 5 == 0 else 0.001)

        result = await async_benchmark.concurrent(
            sometimes_slow, concurrency=5, total=20, timeout=0.05, warmup=0
        )
        assert result["timeouts"] == 4
        assert result["completed"] == 16
        assert result["max"] < 0.05

    @pytest.mark.asyncio
    async def test_all_calls_failing_raises(self, async_benchmark):
        async def broken():
            raise ValueError("nope")

        with pytest.raises(RuntimeError, match="All 10 calls failed") as excinfo:
            await async_benchmark.concurrent(broken, concurrency=2, total=10)
        assert isinstance(excinfo.value.__cause__, ValueError)

    @pytest.mark.asyncio
    async def test_loop_lag_detects_blocking_calls(self, async_benchmark):
        async def awaits_then_blocks():
            await asyncio.sleep(0.001)
            time.sleep(0.03)  # a sync call inside async code

        async def never_yields():
            time.sleep(0.03)  # blocks without ever giving the loop back

        async def well_behaved():
            await asyncio.sleep(0.03)

        healthy = await async_benchmark.concurrent(
            well_behaved, concurrency=4, total=8, warmup=0
        )
        for blocking_func in (awaits_then_blocks, never_yields):
            blocking = await async_benchmark.concurrent(
                blocking_func, concurrency=4, total=8, warmup=0
            )
            assert blocking["loop_lag_max"] >= 0.02, blocking_func.__name__
            assert healthy["loop_lag_max"] < blocking["loop_lag_max"]

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark(concurrency=3, total=9)
    async def test_marker_configures_concurrency(self, async_benchmark):
        counter = InFlightCounter()
        result = await async_benchmark.concurrent(
            as_coroutine_function(counter), warmup=0
        )
        assert result["concurrency"] == 3
        assert result["total"] == 9
        assert counter.peak == 3

    @pytest.mark.asyncio
    async def test_invalid_arguments(self):
        runner = AsyncBenchmarkRunner()

        async def noop():
            pass

        with pytest.raises(ValueError):
            await runner.run_concurrent(noop, concurrency=0)
        with pytest.raises(ValueError):
            await runner.run_concurrent(noop, total=0)
        with pytest.raises(ValueError):
            await runner.run_concurrent(noop, timeout=0)
        with pytest.raises(ValueError):
            await runner.run_concurrent(lambda: None)


def test_concurrent_sync_interface(async_benchmark):
    """Without a running loop, concurrent() returns results directly."""

    async def io_bound():
        await asyncio.sleep(0.001)

    result = async_benchmark.concurrent(io_bound, concurrency=4, total=12)
    assert result["completed"] == 12


# ---------------------------------------------------------------------------
# Task leak detection
# ---------------------------------------------------------------------------

_leaked: list[asyncio.Task] = []


async def leaks_a_task():
    _leaked.append(asyncio.ensure_future(asyncio.sleep(10)))
    await asyncio.sleep(0)


async def cleans_up():
    task = asyncio.ensure_future(asyncio.sleep(0))
    await task


@pytest.fixture
def cancel_leaked():
    yield
    for task in _leaked:
        task.cancel()
    _leaked.clear()


@pytest.mark.usefixtures("cancel_leaked")
class TestLeakCheck:
    @pytest.mark.asyncio
    async def test_leak_fails(self, async_benchmark):
        with pytest.raises(TaskLeakError, match="asyncio task"):
            await async_benchmark(leaks_a_task, rounds=2, leak_check=True)

    @pytest.mark.asyncio
    async def test_leak_warns(self, async_benchmark):
        with pytest.warns(TaskLeakWarning):
            result = await async_benchmark(leaks_a_task, rounds=2, leak_check="warn")
        assert len(result["leaked_tasks"]) == 2

    @pytest.mark.asyncio
    async def test_no_leak_passes(self, async_benchmark):
        result = await async_benchmark(cleans_up, rounds=3, leak_check=True)
        assert result["leaked_tasks"] == []

    @pytest.mark.asyncio
    async def test_leak_check_off_by_default(self, async_benchmark):
        result = await async_benchmark(leaks_a_task, rounds=2)
        assert "leaked_tasks" not in result

    @pytest.mark.asyncio
    async def test_tasks_started_during_warmup_are_ignored(self, async_benchmark):
        """A lazily started background task (e.g. a pool's keepalive) isn't a leak."""
        state: dict[str, asyncio.Task] = {}

        async def lazy_pool():
            if "keepalive" not in state:
                state["keepalive"] = asyncio.ensure_future(asyncio.sleep(10))
                _leaked.append(state["keepalive"])
            await asyncio.sleep(0)

        result = await async_benchmark(
            lazy_pool, rounds=3, warmup_rounds=1, leak_check=True
        )
        assert result["leaked_tasks"] == []

    @pytest.mark.asyncio
    async def test_concurrent_leak_check(self, async_benchmark):
        with pytest.raises(TaskLeakError):
            await async_benchmark.concurrent(
                leaks_a_task, concurrency=2, total=4, warmup=0, leak_check=True
            )

    @pytest.mark.asyncio
    @pytest.mark.async_benchmark(leak_check="fail")
    async def test_leak_check_from_marker(self, async_benchmark):
        with pytest.raises(TaskLeakError):
            await async_benchmark(leaks_a_task, rounds=1)

    def test_invalid_leak_check_value(self, async_benchmark):
        with pytest.raises(ValueError, match="leak_check"):
            async_benchmark(cleans_up, rounds=1, leak_check="sometimes")
