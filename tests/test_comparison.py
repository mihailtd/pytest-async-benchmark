"""Tests for comparison functionality."""

import asyncio
from io import StringIO

import pytest
from rich.console import Console

from pytest_async_benchmark.comparison import (
    BenchmarkComparator,
    BenchmarkScenario,
    a_vs_b_comparison,
    quick_compare,
)
from pytest_async_benchmark.display import display_comparison_table


class TestBenchmarkComparator:
    """Test the BenchmarkComparator class."""

    @pytest.mark.asyncio
    async def test_basic_comparison(self):
        """Test basic comparison functionality."""
        comparator = BenchmarkComparator()

        async def fast_func():
            await asyncio.sleep(0.001)
            return True

        async def slow_func():
            await asyncio.sleep(0.005)
            return True

        result1 = await comparator.add_scenario(
            "Fast Function", fast_func, rounds=3, iterations=5
        )
        result2 = await comparator.add_scenario(
            "Slow Function", slow_func, rounds=3, iterations=5
        )

        assert len(comparator.results) == 2
        assert result1["name"] == "Fast Function"
        assert result2["name"] == "Slow Function"

        fast_mean = result1["result"]["mean"]
        slow_mean = result2["result"]["mean"]
        assert fast_mean < slow_mean

    @pytest.mark.asyncio
    async def test_scenario_with_description(self):
        """Test scenario with description."""
        comparator = BenchmarkComparator()

        async def test_func():
            return True

        result = await comparator.add_scenario(
            "Test Function",
            test_func,
            rounds=2,
            iterations=3,
            description="A test function for benchmarking",
        )

        assert result["description"] == "A test function for benchmarking"

    def test_fastest_scenario(self):
        """Test finding the fastest scenario."""
        comparator = BenchmarkComparator()

        comparator.results = [
            {"name": "Slow", "result": {"mean": 0.01}},
            {"name": "Fast", "result": {"mean": 0.001}},
            {"name": "Medium", "result": {"mean": 0.005}},
        ]

        fastest = comparator.get_fastest_scenario()
        assert fastest["name"] == "Fast"

    def test_most_stable_scenario(self):
        """Test finding the most stable scenario."""
        comparator = BenchmarkComparator()

        comparator.results = [
            {"name": "Unstable", "result": {"stddev": 0.01}},
            {"name": "Stable", "result": {"stddev": 0.001}},
            {"name": "Medium", "result": {"stddev": 0.005}},
        ]

        stable = comparator.get_most_stable_scenario()
        assert stable["name"] == "Stable"

    def test_export_results(self):
        """Test exporting results."""
        comparator = BenchmarkComparator()

        comparator.results = [
            {
                "name": "Test",
                "description": "Test function",
                "result": {
                    "mean": 0.005,
                    "min": 0.001,
                    "max": 0.01,
                    "median": 0.004,
                    "stddev": 0.002,
                    "rounds": 5,
                    "iterations": 10,
                },
            }
        ]

        exported = comparator.export_results()
        assert len(exported) == 1
        assert exported[0]["name"] == "Test"
        assert exported[0]["mean"] == 0.005
        assert exported[0]["description"] == "Test function"

    def test_clear_results(self):
        """Test clearing results."""
        comparator = BenchmarkComparator()

        comparator.results = [{"name": "test"}]
        assert len(comparator.results) == 1

        comparator.clear_results()
        assert len(comparator.results) == 0


class TestQuickCompare:
    """Test the quick_compare utility function."""

    @pytest.mark.asyncio
    async def test_quick_compare(self):
        """Test quick comparison of multiple scenarios."""

        async def func1():
            await asyncio.sleep(0.001)
            return True

        async def func2():
            await asyncio.sleep(0.002)
            return True

        scenarios = [
            BenchmarkScenario("Function 1", func1, rounds=2, iterations=3),
            BenchmarkScenario("Function 2", func2, rounds=2, iterations=3),
        ]

        console = Console(file=StringIO(), width=80)

        comparator = await quick_compare(
            scenarios, title="Test Comparison", console=console
        )

        assert len(comparator.results) == 2
        assert comparator.results[0]["name"] == "Function 1"
        assert comparator.results[1]["name"] == "Function 2"


class TestAVsBComparison:
    """Test the a_vs_b_comparison utility function."""

    @pytest.mark.asyncio
    async def test_a_vs_b_comparison(self):
        """Test A vs B comparison."""

        async def function_a():
            await asyncio.sleep(0.001)
            return "A"

        async def function_b():
            await asyncio.sleep(0.003)
            return "B"

        console = Console(file=StringIO(), width=80)

        comparator = await a_vs_b_comparison(
            "Function A",
            function_a,
            "Function B",
            function_b,
            rounds=3,
            iterations=5,
            console=console,
        )

        assert len(comparator.results) == 2
        assert comparator.results[0]["name"] == "Function A"
        assert comparator.results[1]["name"] == "Function B"

        a_mean = comparator.results[0]["result"]["mean"]
        b_mean = comparator.results[1]["result"]["mean"]
        assert a_mean < b_mean


class TestDisplayComparison:
    """Test display comparison functions."""

    def test_display_comparison_table(self):
        """Test the display comparison table function."""
        comparisons = [
            {
                "name": "Version 1",
                "result": {
                    "min": 0.001,
                    "max": 0.01,
                    "mean": 0.005,
                    "median": 0.004,
                    "stddev": 0.002,
                    "rounds": 5,
                    "iterations": 10,
                },
            },
            {
                "name": "Version 2",
                "result": {
                    "min": 0.0005,
                    "max": 0.008,
                    "mean": 0.003,
                    "median": 0.002,
                    "stddev": 0.001,
                    "rounds": 5,
                    "iterations": 10,
                },
            },
        ]

        console = Console(file=StringIO(), width=120)

        display_comparison_table(comparisons, title="Test Comparison", console=console)

        output = console.file.getvalue()
        assert "Test Comparison" in output
        assert "Version 1" in output
        assert "Version 2" in output


class TestBenchmarkScenario:
    """Test the BenchmarkScenario dataclass."""

    def test_scenario_creation(self):
        """Test creating a benchmark scenario."""

        async def test_func():
            return True

        scenario = BenchmarkScenario(
            name="Test Scenario",
            func=test_func,
            rounds=10,
            iterations=50,
            description="A test scenario",
        )

        assert scenario.name == "Test Scenario"
        assert scenario.func == test_func
        assert scenario.rounds == 10
        assert scenario.iterations == 50
        assert scenario.description == "A test scenario"

    def test_scenario_defaults(self):
        """Test scenario with default values."""

        async def test_func():
            return True

        scenario = BenchmarkScenario("Test", test_func)

        assert scenario.rounds == 5
        assert scenario.iterations == 10
        assert scenario.description is None
