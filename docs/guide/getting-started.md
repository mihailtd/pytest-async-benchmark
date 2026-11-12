---
title: Getting Started
description: Installation, quick start, and foundational concepts for pytest-async-benchmark.
---

# Getting Started

`pytest-async-benchmark` provides modern, high-precision benchmarking for Python asynchronous code. It is designed specifically for `async def` functions, integrating seamlessly into existing `pytest` and `pytest-asyncio` suites.

## Installation

Choose your installation method based on your package manager:

::: code-group

```bash [pip]
# With pytest-asyncio (recommended for native async/await tests)
pip install "pytest-async-benchmark[asyncio]"

# Standalone (synchronous runner interface)
pip install pytest-async-benchmark
```

```bash [uv]
# With pytest-asyncio
uv add pytest-async-benchmark --optional asyncio

# Standalone
uv add pytest-async-benchmark
```

```bash [poetry]
# With pytest-asyncio
poetry add pytest-async-benchmark -E asyncio

# Standalone
poetry add pytest-async-benchmark
```

:::

### Requirements

- **Python**: `>=3.10` (Python 3.10, 3.11, 3.12, 3.13, 3.14)
- **Pytest**: `>=8.3.5`
- **Rich**: `>=14.0.0`
- **Optional**: `pytest-asyncio>=0.23.0` (for native `await async_benchmark(...)` syntax)

## Your First Async Benchmark

If you already use `@pytest.mark.asyncio`, benchmarking an async function is as simple as injecting the `async_benchmark` fixture:

```python
import asyncio
import pytest


async def fetch_item(item_id: int):
    await asyncio.sleep(0.002)
    return {"id": item_id, "name": f"item_{item_id}"}


@pytest.mark.asyncio
async def test_item_lookup_speed(async_benchmark):
    # Benchmark the coroutine
    result = await async_benchmark(fetch_item, 101)

    # Validate timing metrics
    assert result["p95"] < 0.005
    assert result["mean"] < 0.003
```

Run pytest normally from your terminal:

```bash
pytest tests/test_performance.py -v
```

You'll see a formatted Rich table containing full distribution statistics:

```text
Benchmark Results:
╭────────────────────────┬─────────────┬─────────────┬─────────────┬─────────────┬────────────╮
│ Benchmark              │ Mean        │ Min         │ Max         │ p95         │ Ops/sec    │
├────────────────────────┼─────────────┼─────────────┼─────────────┼─────────────┼────────────┤
│ test_item_lookup_speed │ 2.12 ms     │ 2.05 ms     │ 3.15 ms     │ 2.45 ms     │ 471.7      │
╰────────────────────────┴─────────────┴─────────────┴─────────────┴─────────────┴────────────╯
```

## Result Dictionary Fields

Every benchmark run returns a dictionary with the following keys:

| Field | Type | Description |
|---|---|---|
| `mean` | `float` | Arithmetic mean duration per call in seconds |
| `min` | `float` | Fastest individual call duration in seconds |
| `max` | `float` | Slowest individual call duration in seconds |
| `median` | `float` | Median (50th percentile) call duration |
| `stddev` | `float` | Sample standard deviation |
| `p50` | `float` | 50th percentile latency (median) |
| `p75` | `float` | 75th percentile latency |
| `p90` | `float` | 90th percentile latency |
| `p95` | `float` | 95th percentile latency |
| `p99` | `float` | 99th percentile latency |
| `ops` | `float` | Operations per second (throughput: `1.0 / mean`) |
| `count` | `int` | Total number of measured calls |
| `total_time` | `float` | Sum of all call durations in seconds |
| `rounds` | `int` | Number of measurement rounds completed |
| `iterations` | `int` | Number of iterations per round |
| `samples` | `list[float]` | Chronological list of all individual call durations |
| `warmup_time` | `float` | Time spent in warmup phase (excluded from stats) |

## Calibration & Timing Budget

By default, when `rounds` is not explicitly specified, `pytest-async-benchmark` runs in **auto-calibration mode**:
- It runs a brief warmup call.
- It calculates an execution budget (default: 1.0 second).
- It executes at least 5 rounds and up to 10,000 rounds within the time budget.

You can customize rounds and iterations directly:

```python
# Fixed rounds and iterations:
result = await async_benchmark(fetch_item, 101, rounds=10, iterations=5)

# Or limit total calibration time budget:
result = await async_benchmark(fetch_item, 101, max_time=0.5)
```

Or configure it declaratively via `@pytest.mark.async_benchmark`:

```python
@pytest.mark.asyncio
@pytest.mark.async_benchmark(rounds=20, max_time=2.0)
async def test_calibrated(async_benchmark):
    result = await async_benchmark(fetch_item, 101)
    assert result["rounds"] >= 20
```
