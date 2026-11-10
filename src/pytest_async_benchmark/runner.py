"""Core benchmarking logic for async functions."""

import inspect
import statistics
import time
from typing import Any, Callable, Optional


class AsyncBenchmarkRunner:
    """Runner for async function benchmarks."""

    def __init__(
        self,
        rounds: Optional[int] = None,
        iterations: Optional[int] = None,
        warmup_rounds: int = 1,
    ):
        self.rounds = rounds or 5
        self.iterations = iterations or 1
        self.warmup_rounds = warmup_rounds

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

        times: list[float] = []

        for _ in range(self.rounds):
            round_times: list[float] = []

            for _ in range(self.iterations):
                start_time = time.perf_counter()
                await func(*args, **kwargs)
                end_time = time.perf_counter()
                round_times.append(end_time - start_time)

            times.append(statistics.mean(round_times))

        return self._calculate_stats(times)

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

        # Warmup rounds
        for _ in range(self.warmup_rounds):
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
            try:
                await func(*call_args, **kwargs)
            finally:
                if teardown is not None:
                    await self._call_hook(teardown, *teardown_args)

        times: list[float] = []

        # Measurement rounds
        for _ in range(self.rounds):
            round_times: list[float] = []

            for _ in range(self.iterations):
                setup_res = await self._call_hook(setup)
                call_args = list(args)
                teardown_args = []
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
                    end_time = time.perf_counter()
                    round_times.append(end_time - start_time)
                    if teardown is not None:
                        await self._call_hook(teardown, *teardown_args)

            times.append(statistics.mean(round_times))

        return self._calculate_stats(times)

    def _calculate_stats(self, times: list[float]) -> dict[str, Any]:
        """Calculate statistics from timing data."""
        return {
            "min": min(times),
            "max": max(times),
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "stddev": statistics.stdev(times) if len(times) > 1 else 0.0,
            "rounds": self.rounds,
            "iterations": self.iterations,
            "raw_times": times,
        }
