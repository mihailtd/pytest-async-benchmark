#!/usr/bin/env python3
"""
Advanced comparison examples for pytest-async-benchmark.

This example demonstrates the comparison tools:
- A vs B comparisons
- Multi-scenario benchmarking with BenchmarkComparator
- Quick comparison utilities
- Performance analysis and grading
"""

import asyncio
import time

from pytest_async_benchmark import (
    BenchmarkComparator,
    BenchmarkScenario,
    a_vs_b_comparison,
    quick_compare,
)


async def algorithm_v1(data_size: int = 1000):
    """Original algorithm implementation."""
    await asyncio.sleep(0.002)
    return sum(range(data_size))


async def algorithm_v2(data_size: int = 1000):
    """Optimized algorithm implementation."""
    await asyncio.sleep(0.0015)
    return sum(range(data_size))


async def database_query_slow():
    """Simulate a slow database query."""
    await asyncio.sleep(0.008)
    return [{"id": i, "data": f"record_{i}"} for i in range(50)]


async def database_query_fast():
    """Simulate an optimized database query."""
    await asyncio.sleep(0.003)
    return [{"id": i, "data": f"record_{i}"} for i in range(50)]


async def cpu_intensive_operation():
    """Simulate CPU-intensive work."""
    # Simulate CPU work without blocking the event loop
    start = time.perf_counter()
    total = 0
    while time.perf_counter() - start < 0.004:
        total += 1
    await asyncio.sleep(0)
    return total


async def network_operation_v1():
    """Simulate network operation with multiple round trips."""
    for _ in range(3):
        await asyncio.sleep(0.002)
    return {"status": "success", "version": "v1"}


async def network_operation_v2():
    """Simulate optimized network operation with fewer round trips."""
    for _ in range(1):
        await asyncio.sleep(0.0035)
    return {"status": "success", "version": "v2"}


async def main():
    """Run all comparison examples."""
    print("🔬 Advanced Comparison Examples")
    print("=" * 50)

    print("\n🚀 Example 1: Algorithm Version Comparison")
    print("-" * 45)

    try:
        await a_vs_b_comparison(
            "Algorithm v1",
            algorithm_v1,
            "Algorithm v2 (Optimized)",
            algorithm_v2,
            rounds=8,
            iterations=20,
        )
    except Exception as e:
        print(f"Note: A vs B comparison requires terminal output: {e}")

    print("\n📊 Example 2: Multi-scenario Database Comparison")
    print("-" * 50)

    comparator = BenchmarkComparator()

    await comparator.add_scenario(
        "Slow Query",
        database_query_slow,
        rounds=5,
        iterations=10,
        description="Original unoptimized database query",
    )

    await comparator.add_scenario(
        "Fast Query",
        database_query_fast,
        rounds=5,
        iterations=10,
        description="Optimized query with indexing",
    )

    await comparator.add_scenario(
        "CPU Operation",
        cpu_intensive_operation,
        rounds=3,
        iterations=8,
        description="CPU-intensive processing task",
    )

    try:
        comparator.display_all_results("🔥 Database Performance Analysis")

        print("\n" + "=" * 50)
        comparator.display_pairwise_comparison("Slow Query", "Fast Query")

    except Exception as e:
        print(f"Note: Rich display requires terminal output: {e}")

    results = comparator.export_results()
    print(f"\n📁 Exported {len(results)} benchmark results")

    if results:
        fastest = comparator.get_fastest_scenario()
        most_stable = comparator.get_most_stable_scenario()

        print(f"🏆 Fastest scenario: {fastest['name']}")
        print(f"🎯 Most stable scenario: {most_stable['name']}")

    print("\n⚡ Example 3: Quick Multi-scenario Comparison")
    print("-" * 48)

    try:
        await quick_compare(
            [
                BenchmarkScenario(
                    "Network v1",
                    network_operation_v1,
                    rounds=5,
                    iterations=15,
                    description="Multiple round trip approach",
                ),
                BenchmarkScenario(
                    "Network v2",
                    network_operation_v2,
                    rounds=5,
                    iterations=15,
                    description="Single optimized round trip",
                ),
                BenchmarkScenario(
                    "CPU Task",
                    cpu_intensive_operation,
                    rounds=3,
                    iterations=10,
                    description="CPU-bound processing",
                ),
            ]
        )
    except Exception as e:
        print(f"Note: Quick compare requires terminal output: {e}")

    print("\n🔬 Example 4: Performance Analysis")
    print("-" * 40)

    analysis_comparator = BenchmarkComparator()

    async def small_v1():
        return await algorithm_v1(500)

    async def small_v2():
        return await algorithm_v2(500)

    async def large_v1():
        return await algorithm_v1(2000)

    async def large_v2():
        return await algorithm_v2(2000)

    scenarios = [
        ("Small Dataset v1", small_v1, "500 items, original algorithm"),
        ("Small Dataset v2", small_v2, "500 items, optimized algorithm"),
        ("Large Dataset v1", large_v1, "2000 items, original algorithm"),
        ("Large Dataset v2", large_v2, "2000 items, optimized algorithm"),
    ]

    for name, func, desc in scenarios:
        await analysis_comparator.add_scenario(
            name, func, rounds=5, iterations=12, description=desc
        )

    all_results = analysis_comparator.export_results()
    print("\n📈 Analysis Summary:")
    print(f"   Total scenarios tested: {len(all_results)}")

    for result in all_results:
        print(f"   {result['name']}: {result['mean'] * 1000:.2f}ms avg")

    print("\n✅ All comparison examples completed!")
    print("\n💡 Usage Tips:")
    print("   - Use a_vs_b_comparison() for simple head-to-head comparisons")
    print("   - Use BenchmarkComparator for complex multi-scenario analysis")
    print("   - Use quick_compare() for rapid multi-scenario benchmarking")
    print("   - Export results for further statistical analysis")


if __name__ == "__main__":
    asyncio.run(main())
