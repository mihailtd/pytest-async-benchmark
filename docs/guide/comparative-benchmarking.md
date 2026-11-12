---
title: Comparative Benchmarking
description: Compare competing implementations side-by-side with A vs B tests and multi-scenario comparison tables.
---

# Comparative Benchmarking

When optimizing asynchronous systems, you often need to evaluate competing implementations: comparing two serialization formats, evaluating different caching libraries, or tuning batch sizes.

`pytest-async-benchmark` provides high-level comparison utilities:
- **`a_vs_b_comparison`**: Quick side-by-side comparison of two implementations.
- **`quick_compare`**: Dictionary-based comparison of multiple implementations.
- **`BenchmarkComparator`**: Full multi-scenario analysis with rankings and Rich tables.

## A vs B Comparisons

Compare two coroutines with a single function call:

```python
import asyncio
import pytest
from pytest_async_benchmark import a_vs_b_comparison


async def approach_a():
    await asyncio.sleep(0.005)


async def approach_b():
    await asyncio.sleep(0.002)


@pytest.mark.asyncio
async def test_implementation_bakeoff():
    winner, diff_pct, (res_a, res_b) = await a_vs_b_comparison(
        approach_a,
        approach_b,
        rounds=10,
        iterations=5,
    )

    print(f"Winner: {winner}")
    print(f"Performance Difference: {diff_pct:.1f}%")

    assert winner == "approach_b"
    assert diff_pct > 50.0  # Approach B is over 50% faster
```

![A vs B Comparison Terminal Output](/screenshots/comparison-results.png)

## Quick Compare (Dictionary of Scenarios)

To compare three or more implementations simultaneously:

```python
import asyncio
import pytest
from pytest_async_benchmark import quick_compare


async def parse_sync():
    await asyncio.sleep(0.008)


async def parse_threads():
    await asyncio.sleep(0.004)


async def parse_native():
    await asyncio.sleep(0.001)


@pytest.mark.asyncio
async def test_parser_options():
    results = await quick_compare(
        {
            "Sync Parser": parse_sync,
            "Threaded Parser": parse_threads,
            "Native Async": parse_native,
        },
        rounds=10,
    )

    fastest = min(results.items(), key=lambda x: x[1]["mean"])
    assert fastest[0] == "Native Async"
```

## Advanced Multi-Scenario Analysis (`BenchmarkComparator`)

For complex comparative experiments, use `BenchmarkComparator`:

```python
import asyncio
import pytest
from pytest_async_benchmark import BenchmarkComparator


@pytest.mark.asyncio
async def test_detailed_suite():
    comparator = BenchmarkComparator()

    comparator.add_scenario(
        "Standard JSON",
        parse_sync,
        description="Standard library json module",
    )
    comparator.add_scenario(
        "Orjson",
        parse_native,
        description="Fast Rust-based orjson",
    )

    results = await comparator.run_all(rounds=15)

    # Determine fastest implementation
    fastest_name, fastest_data = comparator.get_fastest()
    assert fastest_name == "Orjson"

    # Determine most stable (lowest relative standard deviation)
    stable_name, stable_data = comparator.get_most_stable()

    # Pretty-print comparison table
    comparator.display_table()
```
