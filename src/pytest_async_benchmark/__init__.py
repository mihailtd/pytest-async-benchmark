"""pytest-async-benchmark: Modern pytest benchmarking for async code. 🚀"""

__version__ = "0.1.0"
__author__ = "Mihai Farcas"
__email__ = "contact@mihai.ltd"

from .plugin import async_benchmark
from .runner import AsyncBenchmarkRunner
from .comparison import (
    BenchmarkComparator,
    BenchmarkScenario,
    quick_compare,
    a_vs_b_comparison,
)
from .display import display_comparison_table, format_time, format_speedup
from .analytics import compare_benchmarks, performance_grade, benchmark_summary

__all__ = [
    "async_benchmark",
    "AsyncBenchmarkRunner",
    "BenchmarkComparator",
    "BenchmarkScenario",
    "quick_compare",
    "a_vs_b_comparison",
    "display_comparison_table",
    "format_time",
    "format_speedup",
    "compare_benchmarks",
    "performance_grade",
    "benchmark_summary",
]
