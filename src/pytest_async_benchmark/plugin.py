"""Core pytest plugin for async benchmarking."""

import asyncio
import inspect
import io
import warnings
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import pytest
from rich.console import Console
from rich.table import Table

from . import regression, storage
from .display import format_time
from .runner import AsyncBenchmarkRunner

LeakCheck = bool | str | None

_ENTRIES_KEY = pytest.StashKey[list[dict[str, Any]]]()
_SUMMARY_KEY = pytest.StashKey[list[str]]()
_COMPARISON_KEY = pytest.StashKey[list[regression.BenchmarkComparison]]()


class TaskLeakError(AssertionError):
    """Raised when a benchmark leaves asyncio tasks running (``leak_check=True``)."""


class TaskLeakWarning(UserWarning):
    """Emitted when a benchmark leaves asyncio tasks running (``leak_check="warn"``)."""


def _is_pytest_asyncio_available() -> bool:
    """Check if pytest-asyncio is available and active."""
    try:
        import pytest_asyncio  # noqa: F401

        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False
    except ImportError:
        return False


def _normalize_leak_check(value: LeakCheck) -> str:
    """Map a leak_check setting to ``"off"``, ``"warn"`` or ``"fail"``."""
    if value is None or value is False or value == "off":
        return "off"
    if value is True or value == "fail":
        return "fail"
    if value == "warn":
        return "warn"
    raise ValueError(
        f"leak_check must be True, False, 'warn', 'fail' or 'off', got {value!r}"
    )


class _SyncResultWrapper:
    """Wrapper that provides sync interface when pytest-asyncio not available."""

    def __init__(self, coro: Awaitable[Any]):
        self._coro = coro
        self._result: dict[str, Any] = {}
        self._run()

    def _run(self):
        """Run the coroutine in a new event loop."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError("Unexpected: event loop already running")
        except RuntimeError:
            self._result = asyncio.run(self._coro)  # type: ignore

    def __getattr__(self, name):
        """Delegate attribute access to the result."""
        return getattr(self._result, name)

    def __getitem__(self, key):
        """Delegate item access to the result."""
        return self._result[key]

    def __setitem__(self, key, value):
        """Delegate item setting to the result."""
        self._result[key] = value

    def __contains__(self, key):
        """Delegate containment check to the result."""
        return key in self._result

    def __iter__(self):
        """Delegate iteration to the result."""
        return iter(self._result)

    def __len__(self):
        """Delegate length to the result."""
        return len(self._result)

    def __repr__(self):
        return repr(self._result)

    def __str__(self):
        return str(self._result)

    def keys(self):
        """Delegate keys() to the result."""
        return self._result.keys()

    def values(self):
        """Delegate values() to the result."""
        return self._result.values()

    def items(self):
        """Delegate items() to the result."""
        return self._result.items()

    def get(self, key, default=None):
        """Delegate get() to the result."""
        return self._result.get(key, default)


class AsyncBenchmarkFixture:
    """Fixture for benchmarking async functions."""

    def __init__(self, request: pytest.FixtureRequest):
        self.request = request
        self.console = Console()
        self.results: dict[str, Any] = {}
        self._calls = 0

    def _get_marker_params(self):
        """Extract parameters from @pytest.mark.async_benchmark marker."""
        marker = self.request.node.get_closest_marker("async_benchmark")
        if marker:
            return marker.kwargs
        return {}

    def _option(self, name: str) -> Any:
        return _setting(self.request.config, name)

    def _resolve(self, value: Any, key: str, default: Any = None) -> Any:
        """Explicit argument, then marker kwarg, then ``default``."""
        if value is not None:
            return value
        return self._get_marker_params().get(key, default)

    def _make_runner(
        self,
        rounds: int | None,
        iterations: int | None,
        warmup_rounds: int,
        max_time: float | None,
        leak_mode: str,
    ) -> AsyncBenchmarkRunner:
        return AsyncBenchmarkRunner(
            rounds=self._resolve(rounds, "rounds"),
            iterations=self._resolve(iterations, "iterations"),
            warmup_rounds=warmup_rounds,
            max_time=self._resolve(
                max_time, "max_time", self._option("async_bench_max_time")
            ),
            leak_check=leak_mode != "off",
        )

    def _leak_mode(self, leak_check: LeakCheck) -> str:
        return _normalize_leak_check(
            self._resolve(
                leak_check, "leak_check", self._option("async_bench_leak_check")
            )
        )

    def _wrap(self, run: Callable[[], Awaitable[dict[str, Any]]], leak_mode: str):
        """Run the benchmark coroutine, record and display its result."""
        self._calls += 1
        call_index = self._calls

        async def _benchmark():
            result = await run()
            self._record(result, call_index)
            if result.get("mode") == "concurrent":
                self._display_concurrent_results(self.request.node.name, result)
            else:
                self._display_results(self.request.node.name, result)
            self._handle_leaks(result, leak_mode)
            return result

        if _is_pytest_asyncio_available():
            return _benchmark()
        return _SyncResultWrapper(_benchmark())

    def _record(self, result: dict[str, Any], call_index: int) -> None:
        node = self.request.node
        test_name = node.name
        fullname = node.nodeid if call_index == 1 else f"{node.nodeid}#{call_index}"
        self.results[test_name] = result
        entries = self.request.config.stash.setdefault(_ENTRIES_KEY, [])
        entries.append({"name": test_name, "fullname": fullname, "result": result})

    @staticmethod
    def _handle_leaks(result: dict[str, Any], leak_mode: str) -> None:
        leaked = result.get("leaked_tasks")
        if leak_mode == "off" or not leaked:
            return
        message = f"Benchmark left {len(leaked)} asyncio task(s) running: " + ", ".join(
            leaked
        )
        if leak_mode == "fail":
            raise TaskLeakError(message)
        warnings.warn(message, TaskLeakWarning, stacklevel=3)

    def __call__(
        self,
        func: Callable,
        *args,
        rounds: int | None = None,
        iterations: int | None = None,
        warmup_rounds: int = 1,
        max_time: float | None = None,
        leak_check: LeakCheck = None,
        **kwargs,
    ) -> Any:
        """Benchmark an async function.

        Every call is timed individually. If ``rounds`` is not given (here or in
        the marker), rounds are calibrated to fill ``max_time`` seconds
        (default 1.0s, at least 5 rounds).

        Args:
            leak_check: ``True``/``"fail"`` raises :class:`TaskLeakError` if the
                benchmark leaves asyncio tasks running; ``"warn"`` emits a
                :class:`TaskLeakWarning` instead.

        Returns:
            If pytest-asyncio is available and active: An awaitable that yields benchmark results
            If pytest-asyncio is not available: Benchmark results directly (sync interface)
        """
        if not inspect.iscoroutinefunction(func):
            raise ValueError("Function must be async (coroutine function)")

        final_warmup = (
            warmup_rounds
            if warmup_rounds != 1
            else self._get_marker_params().get("warmup_rounds", 1)
        )
        leak_mode = self._leak_mode(leak_check)
        runner = self._make_runner(
            rounds, iterations, final_warmup, max_time, leak_mode
        )
        return self._wrap(lambda: runner.run(func, *args, **kwargs), leak_mode)

    def pedantic(
        self,
        func: Callable,
        *target_args,
        setup: Callable | None = None,
        teardown: Callable | None = None,
        rounds: int | None = None,
        iterations: int | None = None,
        warmup_rounds: int | None = None,
        max_time: float | None = None,
        leak_check: LeakCheck = None,
        args: tuple | None = None,
        kwargs: dict[str, Any] | None = None,
        **extra_kwargs,
    ) -> Any:
        """Benchmark an async function in pedantic mode with setup and teardown.

        Setup and teardown are executed before and after each iteration, but their
        duration is excluded from benchmark timing measurements.

        Args:
            func: The async coroutine function to benchmark.
            *target_args: Positional arguments to pass to func.
            setup: Sync or async callable executed before each iteration. Its return value
                   is passed as extra positional argument(s) to func and teardown.
            teardown: Sync or async callable executed after each iteration, receiving setup's return value.
            rounds: Number of benchmark rounds (defaults to marker setting, else calibrated).
            iterations: Number of iterations per round (defaults to marker setting or 1).
            warmup_rounds: Number of warmup rounds (defaults to marker setting or 0).
            max_time: Time budget in seconds used to calibrate rounds when not given.
            leak_check: Fail (``True``) or warn (``"warn"``) on leaked asyncio tasks.
            args: Optional tuple of positional arguments (alternative to *target_args).
            kwargs: Optional dict of keyword arguments.
            **extra_kwargs: Additional keyword arguments to pass to func.

        Returns:
            If pytest-asyncio is available and active: An awaitable that yields benchmark results.
            If pytest-asyncio is not available: Benchmark results directly (sync interface).
        """
        if not inspect.iscoroutinefunction(func):
            raise ValueError("Function must be async (coroutine function)")

        final_warmup = self._resolve(warmup_rounds, "warmup_rounds", 0)
        leak_mode = self._leak_mode(leak_check)
        runner = self._make_runner(
            rounds, iterations, final_warmup, max_time, leak_mode
        )

        call_args = list(args) if args is not None else list(target_args)
        call_kwargs = dict(kwargs) if kwargs is not None else {}
        call_kwargs.update(extra_kwargs)

        return self._wrap(
            lambda: runner.run_pedantic(
                func, *call_args, setup=setup, teardown=teardown, **call_kwargs
            ),
            leak_mode,
        )

    def concurrent(
        self,
        func: Callable,
        *args,
        concurrency: int | None = None,
        total: int | None = None,
        timeout: float | None = None,
        warmup: int | None = None,
        leak_check: LeakCheck = None,
        **kwargs,
    ) -> Any:
        """Benchmark an async function under concurrency.

        Runs ``total`` calls with ``concurrency`` of them in flight at once and
        reports throughput, the latency distribution under load, errors,
        timeouts and event loop lag.

        This measures how your code behaves under concurrency *in this process
        and event loop*. It is not a load test: when client and server share
        one event loop, throughput reflects that setup, not production capacity.

        Args:
            func: The async coroutine function to call.
            *args: Positional arguments for func.
            concurrency: Calls in flight at once (default: marker setting or 10).
            total: Total number of calls (default: marker setting or 100).
            timeout: Per-call timeout in seconds; timed-out calls are counted
                separately and excluded from latency stats.
            warmup: Warmup calls before measuring (default: one per worker).
            leak_check: Fail (``True``) or warn (``"warn"``) on leaked asyncio tasks.
            **kwargs: Keyword arguments for func.
        """
        if not inspect.iscoroutinefunction(func):
            raise ValueError("Function must be async (coroutine function)")

        leak_mode = self._leak_mode(leak_check)
        runner = AsyncBenchmarkRunner(leak_check=leak_mode != "off")
        final_concurrency = self._resolve(concurrency, "concurrency", 10)
        final_total = self._resolve(total, "total", 100)
        final_timeout = self._resolve(timeout, "timeout")

        return self._wrap(
            lambda: runner.run_concurrent(
                func,
                *args,
                concurrency=final_concurrency,
                total=final_total,
                timeout=final_timeout,
                warmup=warmup,
                **kwargs,
            ),
            leak_mode,
        )

    def _display_results(self, test_name: str, result: dict[str, Any]):
        """Display benchmark results using rich."""
        table = Table(title=f"🚀 Async Benchmark Results: {test_name}")

        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Min", format_time(result["min"]))
        table.add_row("Median", format_time(result["median"]))
        table.add_row("Mean", format_time(result["mean"]))
        table.add_row("p95", format_time(result["p95"]))
        table.add_row("p99", format_time(result["p99"]))
        table.add_row("Max", format_time(result["max"]))
        table.add_row("Std Dev", format_time(result["stddev"]))
        table.add_row("Ops/sec", f"{result['ops']:,.1f}")
        table.add_row("Samples", str(result["count"]))
        rounds_label = str(result["rounds"])
        if result.get("calibrated"):
            rounds_label += " (calibrated)"
        table.add_row("Rounds", rounds_label)
        table.add_row("Iterations", str(result["iterations"]))

        self.console.print("\n")
        self.console.print(table)
        self.console.print("✅ Benchmark completed successfully!\n")

    def _display_concurrent_results(self, test_name: str, result: dict[str, Any]):
        """Display concurrent benchmark results using rich."""
        table = Table(title=f"🚦 Async Concurrency Results: {test_name}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Concurrency", str(result["concurrency"]))
        table.add_row("Completed", f"{result['completed']} / {result['total']}")
        table.add_row("Errors", str(result["errors"]))
        table.add_row("Timeouts", str(result["timeouts"]))
        table.add_row("Throughput", f"{result['throughput']:,.1f} calls/s")
        table.add_row("Wall time", format_time(result["wall_time"]))
        table.add_row("Latency p50", format_time(result["p50"]))
        table.add_row("Latency p95", format_time(result["p95"]))
        table.add_row("Latency p99", format_time(result["p99"]))
        table.add_row("Latency max", format_time(result["max"]))
        table.add_row("Loop lag p99", format_time(result["loop_lag_p99"]))
        table.add_row("Loop lag max", format_time(result["loop_lag_max"]))

        self.console.print("\n")
        self.console.print(table)
        if result["error_types"]:
            errors = ", ".join(f"{k} ×{v}" for k, v in result["error_types"].items())
            self.console.print(f"⚠️  Errors: {errors}")
        self.console.print(
            "[dim]In-process measurement: throughput reflects this event loop, "
            "not production capacity.[/dim]\n"
        )


@pytest.fixture
def async_benchmark(request: pytest.FixtureRequest) -> AsyncBenchmarkFixture:
    """Pytest fixture for async benchmarking."""
    return AsyncBenchmarkFixture(request)


# ---------------------------------------------------------------------------
# Command line options and session hooks
# ---------------------------------------------------------------------------


#: Options that can also be set once in the pytest config file (ini, toml,
#: setup.cfg). A command-line flag takes precedence over the config file.
_INI_SETTINGS = {
    "async_bench_max_time": (
        "Time budget in seconds used to calibrate rounds when none are given "
        "(default: 1.0). 0 runs the minimum of 5 rounds."
    ),
    "async_bench_leak_check": "Default leak check for every benchmark: off, warn or fail.",
}


def _parse_setting(name: str, raw: str) -> Any:
    """Convert and validate a config-file value."""
    raw = raw.strip()
    if name == "async_bench_max_time":
        try:
            value = float(raw)
        except ValueError:
            value = -1.0
        if value < 0:
            raise pytest.UsageError(
                f"{name} must be a non-negative number of seconds, got {raw!r}"
            )
        return value
    if raw.lower() not in ("off", "warn", "fail"):
        raise pytest.UsageError(f"{name} must be off, warn or fail, got {raw!r}")
    return raw.lower()


def _setting(config: pytest.Config, name: str) -> Any:
    """Read an option: command line first, then the config file, else None."""
    value = config.getoption(name, default=None)
    if value is not None or name not in _INI_SETTINGS:
        return value
    raw = config.getini(name)
    return _parse_setting(name, raw) if raw else None


def pytest_addoption(parser: pytest.Parser) -> None:
    for name, help_text in _INI_SETTINGS.items():
        parser.addini(name, help_text, default="")
    group = parser.getgroup("async-benchmark", "async benchmarking")
    group.addoption(
        "--async-bench-max-time",
        type=float,
        default=None,
        metavar="SECONDS",
        help="Time budget used to calibrate rounds when none are given (default: 1.0).",
    )
    group.addoption(
        "--async-bench-leak-check",
        choices=("off", "warn", "fail"),
        default=None,
        help="Default leak check for every benchmark: warn or fail when a "
        "benchmark leaves asyncio tasks running (default: off).",
    )
    group.addoption(
        "--async-bench-json",
        default=None,
        metavar="PATH",
        help="Write all benchmark results to PATH as JSON.",
    )
    group.addoption(
        "--async-bench-autosave",
        action="store_true",
        default=False,
        help="Save results to the storage directory as a numbered run.",
    )
    group.addoption(
        "--async-bench-storage",
        default=".async_benchmarks",
        metavar="DIR",
        help="Directory for saved runs (default: .async_benchmarks).",
    )
    group.addoption(
        "--async-bench-compare",
        nargs="?",
        const="",
        default=None,
        metavar="NUM|PATH",
        help="Compare against a saved run: the latest (no value), a run "
        "number, or a JSON file path.",
    )
    group.addoption(
        "--async-bench-compare-fail",
        action="append",
        default=[],
        metavar="EXPR",
        help="Fail the session on a significant regression beyond EXPR, e.g. "
        "'median:10%%' or 'p95:0.002' (seconds). Can be repeated.",
    )
    group.addoption(
        "--async-bench-compare-alpha",
        type=float,
        default=0.05,
        metavar="ALPHA",
        help="Significance level for the Mann-Whitney U test (default: 0.05).",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest plugin."""
    for name in _INI_SETTINGS:  # fail fast on a bad config-file value
        _setting(config, name)
    config.addinivalue_line(
        "markers",
        "async_benchmark(rounds=None, iterations=None, warmup_rounds=1, "
        "max_time=None, leak_check=None, concurrency=None, total=None, "
        "timeout=None): configure async benchmarks in this test",
    )
    expressions = config.getoption("async_bench_compare_fail", default=[]) or []
    try:
        thresholds = [regression.FailThreshold.parse(expr) for expr in expressions]
    except ValueError as exc:
        raise pytest.UsageError(str(exc)) from None
    if thresholds and config.getoption("async_bench_compare", default=None) is None:
        raise pytest.UsageError(
            "--async-bench-compare-fail requires --async-bench-compare"
        )
    alpha = config.getoption("async_bench_compare_alpha", default=0.05)
    if alpha is not None and not 0 < alpha < 1:
        raise pytest.UsageError("--async-bench-compare-alpha must be between 0 and 1")


def _version() -> str:
    from . import __version__

    return __version__


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Save, export and compare collected benchmark results."""
    config = session.config
    entries = config.stash.get(_ENTRIES_KEY, [])
    summary = config.stash.setdefault(_SUMMARY_KEY, [])
    if not entries:
        return

    json_path = config.getoption("async_bench_json", default=None)
    autosave = config.getoption("async_bench_autosave", default=False)
    compare = config.getoption("async_bench_compare", default=None)
    if not (json_path or autosave or compare is not None):
        return

    report = storage.build_report(entries, _version(), Path(config.rootpath))
    storage_dir = Path(config.rootpath) / config.getoption("async_bench_storage")

    # Compare before saving, so "latest saved run" is never this run.
    if compare is not None:
        try:
            baseline_path = storage.find_baseline(storage_dir, compare)
            baseline = storage.load_report(baseline_path)
        except (OSError, ValueError) as exc:
            summary.append(f"⚠️  Can't compare: {exc}")
        else:
            thresholds = [
                regression.FailThreshold.parse(expr)
                for expr in config.getoption("async_bench_compare_fail")
            ]
            comparisons = regression.compare_reports(
                report,
                baseline,
                thresholds,
                alpha=config.getoption("async_bench_compare_alpha"),
            )
            config.stash[_COMPARISON_KEY] = comparisons
            summary.append(f"Compared against {baseline_path}")
            regressions = [c for c in comparisons if c.status == regression.REGRESSION]
            if regressions and session.exitstatus == pytest.ExitCode.OK:
                session.exitstatus = pytest.ExitCode.TESTS_FAILED

    if json_path:
        written = storage.write_report(report, json_path)
        summary.append(f"Saved benchmark JSON to {written}")
    if autosave:
        written = storage.write_report(
            report, storage.autosave_path(storage_dir, report)
        )
        summary.append(f"Saved benchmark run to {written}")


def _format_change(change: float | None) -> str:
    if change is None:
        return "-"
    return f"{change * 100:+.1f}%"


def _format_p(value: float | None) -> str:
    return "-" if value is None else f"{value:.3g}"


_STATUS_STYLE = {
    regression.REGRESSION: "bold red",
    regression.SLOWER: "yellow",
    regression.FASTER: "green",
    regression.UNCHANGED: "",
    regression.INSUFFICIENT: "dim",
    regression.NEW: "cyan",
}


def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:
    """Print the comparison table and where results were saved."""
    comparisons = config.stash.get(_COMPARISON_KEY, None)
    summary = config.stash.get(_SUMMARY_KEY, [])
    if not comparisons and not summary:
        return

    terminalreporter.section("async benchmark")
    buffer = io.StringIO()
    console = Console(
        file=buffer,
        force_terminal=terminalreporter.hasmarkup,
        width=terminalreporter._tw.fullwidth,
    )

    if comparisons:
        table = Table(title="Comparison with baseline (median latency)")
        table.add_column("Benchmark", style="cyan", overflow="fold")
        table.add_column("Baseline", justify="right", no_wrap=True)
        table.add_column("Current", justify="right", no_wrap=True)
        table.add_column("Change", justify="right", no_wrap=True)
        table.add_column("p (slower)", justify="right", no_wrap=True)
        table.add_column("Status", no_wrap=True)
        for comp in comparisons:
            status = comp.status
            if comp.failed_thresholds:
                status += f" ({', '.join(comp.failed_thresholds)})"
            table.add_row(
                comp.fullname,
                format_time(comp.baseline_median)
                if comp.baseline_median is not None
                else "-",
                format_time(comp.current_median)
                if comp.current_median is not None
                else "-",
                _format_change(comp.change),
                _format_p(comp.p_slower),
                f"[{_STATUS_STYLE[comp.status]}]{status}[/]"
                if _STATUS_STYLE[comp.status]
                else status,
            )
        console.print(table)
        regressions = [c for c in comparisons if c.status == regression.REGRESSION]
        if regressions:
            console.print(
                f"[bold red]❌ {len(regressions)} benchmark(s) regressed "
                "beyond --async-bench-compare-fail thresholds[/]"
            )
        terminalreporter.write(buffer.getvalue())

    for line in summary:
        terminalreporter.write_line(line)
