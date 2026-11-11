"""Core benchmarking logic for async functions."""

import asyncio
import inspect
import statistics
import time
from typing import Any, Callable, Optional

from .stats import compute_stats

#: Rounds used when ``rounds`` is not given and calibration is active.
DEFAULT_MIN_ROUNDS = 5
#: Upper bound on calibrated rounds, so very fast functions still finish.
DEFAULT_MAX_ROUNDS = 10_000
#: Measurement time budget (seconds) used to calibrate the number of rounds.
DEFAULT_MAX_TIME = 1.0
#: Interval (seconds) of the event loop lag probe in concurrent mode.
LOOP_LAG_INTERVAL = 0.005


def _describe_task(task: "asyncio.Task[Any]") -> str:
    coro = task.get_coro()
    qualname = getattr(coro, "__qualname__", None) or repr(coro)
    return f"{task.get_name()} ({qualname})"


async def find_leaked_tasks(before: "set[asyncio.Task[Any]]") -> list[str]:
    """Describe tasks that are still pending and were not in ``before``.

    Yields to the event loop a few times first, so tasks that are merely
    finishing up get a chance to complete.
    """
    for _ in range(3):
        await asyncio.sleep(0)
    current = asyncio.current_task()
    leaked = [
        task
        for task in asyncio.all_tasks()
        if task not in before and task is not current and not task.done()
    ]
    return sorted(_describe_task(task) for task in leaked)


class AsyncBenchmarkRunner:
    """Runner for async function benchmarks.

    Every call is timed individually. When ``rounds`` is not given, the number
    of rounds is calibrated: the runner keeps measuring until ``max_time``
    seconds have passed (at least ``min_rounds``, at most ``max_rounds``).
    """

    def __init__(
        self,
        rounds: Optional[int] = None,
        iterations: Optional[int] = None,
        warmup_rounds: int = 1,
        max_time: Optional[float] = None,
        min_rounds: Optional[int] = None,
        max_rounds: Optional[int] = None,
        leak_check: bool = False,
    ):
        if rounds is not None and rounds < 1:
            raise ValueError("rounds must be >= 1")
        if iterations is not None and iterations < 1:
            raise ValueError("iterations must be >= 1")
        self.rounds = rounds
        self.iterations = iterations or 1
        self.warmup_rounds = warmup_rounds
        self.max_time = DEFAULT_MAX_TIME if max_time is None else max_time
        self.min_rounds = DEFAULT_MIN_ROUNDS if min_rounds is None else min_rounds
        self.max_rounds = DEFAULT_MAX_ROUNDS if max_rounds is None else max_rounds
        self.leak_check = leak_check

    @property
    def calibrated(self) -> bool:
        """Whether the number of rounds is chosen automatically."""
        return self.rounds is None

    def _keep_going(self, rounds_done: int, started: float) -> bool:
        if self.rounds is not None:
            return rounds_done < self.rounds
        if rounds_done < self.min_rounds:
            return True
        if rounds_done >= self.max_rounds:
            return False
        return time.perf_counter() - started < self.max_time

    @staticmethod
    async def _call_hook(hook: Optional[Callable], *hook_args) -> Any:
        """Call a sync or async hook function."""
        if hook is None:
            return None
        res = hook(*hook_args)
        if inspect.isawaitable(res):
            return await res
        return res

    async def run(
        self,
        func: Callable,
        *args,
        setup: Optional[Callable] = None,
        teardown: Optional[Callable] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Run benchmark for an async function.

        If setup or teardown are provided, delegates to run_pedantic.
        """
        if setup is not None or teardown is not None:
            return await self.run_pedantic(
                func, *args, setup=setup, teardown=teardown, **kwargs
            )

        if not inspect.iscoroutinefunction(func):
            raise ValueError("Function must be async (coroutine function)")

        for _ in range(self.warmup_rounds):
            await func(*args, **kwargs)

        before = asyncio.all_tasks() if self.leak_check else set()

        samples: list[float] = []
        round_means: list[float] = []
        started = time.perf_counter()
        rounds_done = 0

        while self._keep_going(rounds_done, started):
            round_times: list[float] = []
            for _ in range(self.iterations):
                start_time = time.perf_counter()
                await func(*args, **kwargs)
                round_times.append(time.perf_counter() - start_time)
            samples.extend(round_times)
            round_means.append(statistics.fmean(round_times))
            rounds_done += 1

        result = self._calculate_stats(samples, round_means, mode="sequential")
        if self.leak_check:
            result["leaked_tasks"] = await find_leaked_tasks(before)
        return result

    async def _pedantic_call(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict[str, Any],
        setup: Optional[Callable],
        teardown: Optional[Callable],
    ) -> float:
        """Run setup, a timed call, and teardown. Return the call's duration."""
        setup_res = await self._call_hook(setup)
        call_args = list(args)
        teardown_args: list[Any] = []
        if setup_res is not None:
            if isinstance(setup_res, tuple):
                call_args.extend(setup_res)
                teardown_args.extend(setup_res)
            else:
                call_args.append(setup_res)
                teardown_args.append(setup_res)

        start_time = time.perf_counter()
        try:
            await func(*call_args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start_time
            if teardown is not None:
                await self._call_hook(teardown, *teardown_args)
        return elapsed

    async def run_pedantic(
        self,
        func: Callable,
        *args,
        setup: Optional[Callable] = None,
        teardown: Optional[Callable] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Run benchmark for an async function with setup/teardown excluded from timing."""
        if not inspect.iscoroutinefunction(func):
            raise ValueError("Function must be async (coroutine function)")

        for _ in range(self.warmup_rounds):
            await self._pedantic_call(func, args, kwargs, setup, teardown)

        before = asyncio.all_tasks() if self.leak_check else set()

        samples: list[float] = []
        round_means: list[float] = []
        started = time.perf_counter()
        rounds_done = 0

        while self._keep_going(rounds_done, started):
            round_times = [
                await self._pedantic_call(func, args, kwargs, setup, teardown)
                for _ in range(self.iterations)
            ]
            samples.extend(round_times)
            round_means.append(statistics.fmean(round_times))
            rounds_done += 1

        result = self._calculate_stats(samples, round_means, mode="pedantic")
        if self.leak_check:
            result["leaked_tasks"] = await find_leaked_tasks(before)
        return result

    async def run_concurrent(
        self,
        func: Callable,
        *args,
        concurrency: int = 10,
        total: int = 100,
        timeout: Optional[float] = None,
        warmup: Optional[int] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Benchmark ``func`` with ``concurrency`` calls in flight at once.

        A fixed pool of ``concurrency`` workers pulls from a shared counter
        until ``total`` calls have been made (a closed-loop model: N clients
        that each issue their next call as soon as the previous one returns).

        Latency is timed per call, from the moment a worker starts the call.
        Failed and timed-out calls are counted separately and excluded from
        the latency statistics. While the benchmark runs, a probe task measures
        event loop lag: how late a short ``asyncio.sleep`` wakes up. High lag
        means something is blocking the event loop.
        """
        if not inspect.iscoroutinefunction(func):
            raise ValueError("Function must be async (coroutine function)")
        if concurrency < 1:
            raise ValueError("concurrency must be >= 1")
        if total < 1:
            raise ValueError("total must be >= 1")
        if timeout is not None and timeout <= 0:
            raise ValueError("timeout must be > 0")

        workers = min(concurrency, total)
        warmup_calls = workers if warmup is None else warmup

        async def call_once() -> None:
            if timeout is None:
                await func(*args, **kwargs)
            else:
                await asyncio.wait_for(func(*args, **kwargs), timeout)

        # Warmup: same worker pool, errors ignored (they show up in the real run).
        if warmup_calls > 0:
            remaining = [warmup_calls]

            async def warm_worker() -> None:
                while remaining[0] > 0:
                    remaining[0] -= 1
                    try:
                        await call_once()
                    except Exception:
                        pass

            await asyncio.gather(
                *(warm_worker() for _ in range(min(workers, warmup_calls)))
            )

        before = asyncio.all_tasks() if self.leak_check else set()

        samples: list[float] = []
        error_types: dict[str, int] = {}
        counters = {"issued": 0, "errors": 0, "timeouts": 0}
        first_error: list[BaseException] = []

        async def worker() -> None:
            while counters["issued"] < total:
                counters["issued"] += 1
                start_time = time.perf_counter()
                try:
                    await call_once()
                except asyncio.TimeoutError:
                    counters["timeouts"] += 1
                except Exception as exc:
                    counters["errors"] += 1
                    name = type(exc).__name__
                    error_types[name] = error_types.get(name, 0) + 1
                    if not first_error:
                        first_error.append(exc)
                else:
                    samples.append(time.perf_counter() - start_time)

        lags: list[float] = []
        probe_sleep_started: list[float] = []

        async def lag_probe() -> None:
            while True:
                probe_sleep_started[:] = [time.perf_counter()]
                await asyncio.sleep(LOOP_LAG_INTERVAL)
                lags.append(
                    max(
                        0.0,
                        time.perf_counter()
                        - probe_sleep_started[0]
                        - LOOP_LAG_INTERVAL,
                    )
                )
                probe_sleep_started.clear()

        probe = asyncio.ensure_future(lag_probe())
        wall_start = time.perf_counter()
        try:
            await asyncio.gather(*(worker() for _ in range(workers)))
        finally:
            end = time.perf_counter()
            wall_time = end - wall_start
            # If the loop was blocked, the probe may still be waiting to wake up:
            # count how overdue it already is, or the stall would go unrecorded.
            if probe_sleep_started:
                overdue = end - probe_sleep_started[0] - LOOP_LAG_INTERVAL
                if overdue > 0:
                    lags.append(overdue)
            probe.cancel()
            try:
                await probe
            except asyncio.CancelledError:
                pass

        if not samples:
            message = (
                f"All {total} calls failed "
                f"({counters['errors']} errors, {counters['timeouts']} timeouts)"
            )
            raise RuntimeError(message) from (first_error[0] if first_error else None)

        result: dict[str, Any] = compute_stats(samples)
        result.update(
            {
                "mode": "concurrent",
                "concurrency": workers,
                "total": total,
                "completed": len(samples),
                "errors": counters["errors"],
                "timeouts": counters["timeouts"],
                "error_types": error_types,
                "first_error": repr(first_error[0]) if first_error else None,
                "wall_time": wall_time,
                "throughput": len(samples) / wall_time if wall_time > 0 else 0.0,
                "samples": samples,
            }
        )
        if lags:
            ordered_lags = sorted(lags)
            lag_stats = compute_stats(ordered_lags)
            result["loop_lag_mean"] = lag_stats["mean"]
            result["loop_lag_p99"] = lag_stats["p99"]
            result["loop_lag_max"] = lag_stats["max"]
        else:
            result["loop_lag_mean"] = result["loop_lag_p99"] = 0.0
            result["loop_lag_max"] = 0.0
        if self.leak_check:
            result["leaked_tasks"] = await find_leaked_tasks(before)
        return result

    def _calculate_stats(
        self,
        samples: list[float],
        round_means: Optional[list[float]] = None,
        mode: str = "sequential",
    ) -> dict[str, Any]:
        """Calculate statistics from per-call samples.

        ``raw_times`` keeps its pre-0.4 meaning (one mean per round);
        ``samples`` holds every individual call duration.
        """
        if round_means is None:
            round_means = samples
        result = compute_stats(samples)
        result.update(
            {
                "mode": mode,
                "rounds": len(round_means),
                "iterations": self.iterations,
                "calibrated": self.calibrated,
                "raw_times": round_means,
                "samples": samples,
            }
        )
        return result
