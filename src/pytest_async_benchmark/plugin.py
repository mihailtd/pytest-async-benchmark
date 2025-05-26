"""Core pytest plugin for async benchmarking."""

import asyncio
from typing import Any, Callable, Optional

import pytest
from rich.console import Console
from rich.table import Table

from .display import format_time
from .runner import AsyncBenchmarkRunner


class AsyncBenchmarkFixture:
    """Fixture for benchmarking async functions."""

    def __init__(self, request: pytest.FixtureRequest):
        self.request = request
        self.console = Console()
        self.results: dict[str, Any] = {}

    def __call__(
        self,
        func: Callable,
        *args,
        rounds: Optional[int] = None,
        iterations: Optional[int] = None,
        warmup_rounds: int = 1,
        **kwargs,
    ):
        """Benchmark an async function."""
        if not asyncio.iscoroutinefunction(func):
            raise ValueError("Function must be async (coroutine function)")

        runner = AsyncBenchmarkRunner(
            rounds=rounds, iterations=iterations, warmup_rounds=warmup_rounds
        )

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(runner.run(func, *args, **kwargs))

        test_name = self.request.node.name
        self.results[test_name] = result

        self._display_results(test_name, result)

        return result

    def _display_results(self, test_name: str, result: dict[str, Any]):
        """Display benchmark results using rich."""
        table = Table(title=f"🚀 Async Benchmark Results: {test_name}")

        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Min", format_time(result["min"]))
        table.add_row("Max", format_time(result["max"]))
        table.add_row("Mean", format_time(result["mean"]))
        table.add_row("Median", format_time(result["median"]))
        table.add_row("Std Dev", format_time(result["stddev"]))
        table.add_row("Rounds", str(result["rounds"]))
        table.add_row("Iterations", str(result["iterations"]))

        self.console.print("\n")
        self.console.print(table)
        self.console.print("✅ Benchmark completed successfully!\n")


@pytest.fixture
def async_benchmark(request: pytest.FixtureRequest) -> AsyncBenchmarkFixture:
    """Pytest fixture for async benchmarking."""
    return AsyncBenchmarkFixture(request)


def pytest_configure(config):
    """Configure pytest plugin."""
    config.addinivalue_line(
        "markers", "async_benchmark: mark test as an async benchmark"
    )


def pytest_collection_modifyitems(config, items):
    """Modify collected test items."""
    for item in items:
        if "async_benchmark" in item.fixturenames:
            item.add_marker(pytest.mark.async_benchmark)
