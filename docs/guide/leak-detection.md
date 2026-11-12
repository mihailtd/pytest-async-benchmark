---
title: Task Leak Detection
description: Catch background asyncio tasks left running after benchmarks before they cause flaky test suites.
---

# Task Leak Detection

A common hazard in asynchronous Python is **task leaking**: code that calls `asyncio.create_task()` or spawns background workers without awaiting them or ensuring clean cancellation upon completion.

These leaked tasks continue executing in the background across subsequent test functions, consuming CPU cycles, holding database connections open, or causing bizarre test failures hours later.

`pytest-async-benchmark` includes built-in task leak detection that tracks the set of active asyncio tasks before and after each benchmark.

## Enabling Leak Detection

You can enable leak detection per benchmark call, via markers, through CLI flags, or in your configuration file.

### 1. In Test Calls

Pass `leak_check=True` to fail the benchmark if new tasks are left running, or `leak_check="warn"` to issue a warning:

```python
import asyncio
import pytest


async def buggy_service():
    # Spawns a background task and forgets to await or cancel it
    asyncio.create_task(asyncio.sleep(10))
    return "done"


@pytest.mark.asyncio
async def test_leaky_operation(async_benchmark):
    # This will raise AssertionError: "Benchmark left 1 asyncio task(s) running"
    await async_benchmark(buggy_service, leak_check=True)
```

With `leak_check="warn"`, pytest logs a warning instead of failing:

```python
@pytest.mark.asyncio
async def test_leaky_warning(async_benchmark):
    await async_benchmark(buggy_service, leak_check="warn")
```

### 2. Via Pytest Markers

Apply `@pytest.mark.async_benchmark(leak_check=True)` to any test function or test class:

```python
@pytest.mark.asyncio
@pytest.mark.async_benchmark(leak_check=True)
async def test_with_marker(async_benchmark):
    await async_benchmark(my_service)
```

### 3. Global Configuration in pyproject.toml

To enforce leak detection across your entire test suite, configure `pyproject.toml`:

```toml
[tool.pytest.ini_options]
async_bench_leak_check = "true"  # or "warn"
```

Or pass the CLI flag during your test run:

```bash
pytest --async-bench-leak-check
```

## Warmup Awareness

Tasks legitimately created during warm-up (e.g. background connection pool health checks or metrics heartbeats initialized on first call) are acknowledged and ignored during subsequent measured rounds.

Only tasks newly spawned and left uncompleted during the benchmark measurement window trigger a leak alert.
