---
title: Migrating from pytest-benchmark
description: Step-by-step guide to migrating from pytest-benchmark to pytest-async-benchmark for asynchronous test suites.
---

# Migrating from pytest-benchmark

If you have an existing test suite using `pytest-benchmark`, this guide explains why and how to migrate your async benchmarks to `pytest-async-benchmark`.

## Why Migrate?

`pytest-benchmark` was designed in 2014 for synchronous Python code. When used with async coroutines:
- **It does not await coroutines by default**: Passing an `async def` function to `benchmark(my_coro)` merely benchmarks the time it takes Python to instantiate the unawaited generator object (~100 nanoseconds), not the execution of the coroutine.
- **Synchronous wrapper loops churn the event loop**: Wrapping coroutines in `asyncio.run()` creates and destroys event loops on every round, causing measurements to be dominated by OS socket teardown and selector setup.
- **Missing modern latency distributions**: Traditional round averages hide tail latency spikes (p95, p99) that characterize real-world async I/O.

## Feature Comparison

| Feature | `pytest-benchmark` | `pytest-async-benchmark` |
|---|---|---|
| **Native `async def` Support** | ❌ Requires custom sync wrappers | ✅ Native `await async_benchmark(...)` |
| **`pytest-asyncio` Loop Integration** | ❌ Loop churn | ✅ Shares active test loop |
| **Real Percentiles (p50, p75, p90, p95, p99)** | ⚠️ Approximated from round averages | ✅ Calculated from individual call samples |
| **Concurrency Load Testing** | ❌ Sequential only | ✅ `async_benchmark.concurrent()` |
| **Task Leak Detection** | ❌ No | ✅ Detects unawaited orphan tasks |
| **Pedantic Setup/Teardown** | Sync hooks only | ✅ Sync and `async def` hooks |
| **Regression Testing** | Fixed % cutoff | ✅ Non-parametric Mann-Whitney U test |
| **Terminal Output** | Plain text tables | ✅ Formatted Rich tables |

## Migration Steps

### 1. Update Dependencies

Replace `pytest-benchmark` with `pytest-async-benchmark`:

::: code-group

```bash [pip]
pip uninstall pytest-benchmark
pip install "pytest-async-benchmark[asyncio]"
```

```bash [uv]
uv remove pytest-benchmark
uv add pytest-async-benchmark --optional asyncio
```

:::

### 2. Update Fixture Injections

Change the injected fixture name from `benchmark` to `async_benchmark`, and `await` the call:

#### Before (`pytest-benchmark` with sync wrapper)

```python
# Old work-around with pytest-benchmark
def test_async_with_sync_runner(benchmark):
    async def work():
        await asyncio.sleep(0.01)

    # Churns event loops on every call!
    def sync_runner():
        return asyncio.run(work())

    result = benchmark(sync_runner)
```

#### After (`pytest-async-benchmark`)

```python
import pytest


@pytest.mark.asyncio
async def test_async_clean(async_benchmark):
    async def work():
        await asyncio.sleep(0.01)

    # Clean, native, accurate
    result = await async_benchmark(work)
    assert result["p95"] < 0.015
```

### 3. Migrating Pedantic Mode

If you used `benchmark.pedantic()` with synchronous functions:

#### Before

```python
def test_pedantic_old(benchmark):
    def setup():
        return (), {"val": 10}

    def target(val):
        return val * 2

    benchmark.pedantic(target, setup=setup, rounds=5)
```

#### After

`pytest-async-benchmark` supports both sync and async functions in pedantic mode, with identical argument-unpacking semantics:

```python
@pytest.mark.asyncio
async def test_pedantic_new(async_benchmark):
    async def async_setup():
        await db.reset()
        return 42

    async def async_target(user_id):
        return await db.fetch(user_id)

    async def async_teardown(user_id):
        await db.cleanup(user_id)

    result = await async_benchmark.pedantic(
        async_target,
        setup=async_setup,
        teardown=async_teardown,
        rounds=10,
    )
    assert result["p95"] < 0.005
```
