---
title: API Reference
description: Complete API reference for fixtures, runners, and comparison tools in pytest-async-benchmark.
---

# API Reference

## Fixtures

### `async_benchmark`

The primary pytest fixture used to execute and measure benchmarks.

#### Calling the Fixture directly

```python
result = await async_benchmark(
    func: Callable[..., Awaitable[Any]],
    *args: Any,
    rounds: int | None = None,
    iterations: int = 1,
    warmup: bool = True,
    max_time: float | None = None,
    leak_check: bool | str | None = None,
    **kwargs: Any,
) -> dict[str, Any]
```

**Parameters**:
- **`func`**: An asynchronous function (`async def`) to benchmark.
- **`*args`**: Positional arguments passed to `func`.
- **`rounds`**: Explicit number of rounds. If omitted (`None`), auto-calibration runs until `max_time` is reached (at least 5 rounds).
- **`iterations`**: Number of calls per round (default: `1`).
- **`warmup`**: Whether to run an unmeasured warmup pass before benchmarking (default: `True`).
- **`max_time`**: Total execution budget in seconds for auto-calibration (default: `1.0`).
- **`leak_check`**: Task leak check mode. `True` fails on orphan tasks, `"warn"` issues a warning, `False` or `None` disables it.
- **`**kwargs`**: Keyword arguments forwarded to `func`.

**Returns**:
A dictionary containing distribution statistics:
`mean`, `min`, `max`, `median`, `stddev`, `p50`, `p75`, `p90`, `p95`, `p99`, `ops`, `count`, `total_time`, `rounds`, `iterations`, `samples`, `warmup_time`.

---

### `async_benchmark.pedantic`

Runs target code with isolated per-iteration setup and teardown hooks.

```python
result = await async_benchmark.pedantic(
    target: Callable[..., Awaitable[Any]],
    *args: Any,
    setup: Callable[..., Any] | None = None,
    teardown: Callable[..., Any] | None = None,
    rounds: int | None = None,
    iterations: int = 1,
    warmup: bool = True,
    max_time: float | None = None,
    leak_check: bool | str | None = None,
    **kwargs: Any,
) -> dict[str, Any]
```

**Parameters**:
- **`target`**: The coroutine function to measure.
- **`setup`**: Optional synchronous or asynchronous callable executed before every iteration. Return values (single item or tuple) are forwarded as arguments to `target` and `teardown`. Setup duration is excluded from measurements.
- **`teardown`**: Optional synchronous or asynchronous callable executed after every iteration. Receives arguments from `setup`. Teardown duration is excluded from measurements.

---

### `async_benchmark.concurrent`

Executes coroutines under concurrent load with N tasks in flight.

```python
stats = await async_benchmark.concurrent(
    func: Callable[..., Awaitable[Any]],
    *args: Any,
    concurrency: int | None = None,
    total: int | None = None,
    timeout: float | None = None,
    warmup: bool = True,
    leak_check: bool | str | None = None,
    **kwargs: Any,
) -> ConcurrentBenchmarkResult
```

**Parameters**:
- **`func`**: Asynchronous coroutine to invoke.
- **`concurrency`**: Number of concurrent calls running simultaneously (default: `10` or marker value).
- **`total`**: Total number of calls to complete (default: `100` or marker value).
- **`timeout`**: Per-call deadline in seconds.
- **`warmup`**: Run an unmeasured concurrent warmup batch first (default: `True`).
- **`leak_check`**: Check for orphan background tasks (`True`, `"warn"`, or `False`).

**Returns**: `ConcurrentBenchmarkResult` with:
- `ops`, `total_time`, `concurrency`, `total`, `completed`, `errors`, `timeouts`, `loop_lag`
- `mean`, `min`, `max`, `median`, `p50`, `p75`, `p90`, `p95`, `p99`, `samples`

---

## Markers

### `@pytest.mark.async_benchmark`

Declaratively configures benchmark settings on a test function or class:

```python
@pytest.mark.async_benchmark(
    rounds: int | None = None,
    iterations: int | None = None,
    warmup: bool | None = None,
    max_time: float | None = None,
    concurrency: int | None = None,
    total: int | None = None,
    timeout: float | None = None,
    leak_check: bool | str | None = None,
)
```

Direct arguments passed into `async_benchmark(...)` at call time override values specified in the marker.

---

## Comparison Utilities

### `a_vs_b_comparison`

```python
winner, diff_pct, (res_a, res_b) = await a_vs_b_comparison(
    func_a: Callable[..., Awaitable[Any]],
    func_b: Callable[..., Awaitable[Any]],
    *args: Any,
    rounds: int = 5,
    iterations: int = 1,
    **kwargs: Any,
) -> tuple[str, float, tuple[dict[str, Any], dict[str, Any]]]
```

Compares two coroutines and returns the winner name, the percentage difference in mean execution time, and both raw result dictionaries.

---

### `quick_compare`

```python
results = await quick_compare(
    scenarios: dict[str, Callable[..., Awaitable[Any]]],
    rounds: int = 5,
    iterations: int = 1,
    *args: Any,
    **kwargs: Any,
) -> dict[str, dict[str, Any]]
```

Runs all coroutines provided in the `scenarios` dictionary and returns a mapping from scenario name to benchmark result.

---

### `BenchmarkComparator`

Class for structured multi-scenario benchmark experiments.

```python
from pytest_async_benchmark import BenchmarkComparator

comparator = BenchmarkComparator()
comparator.add_scenario(name: str, func: Callable, description: str = "")
results = await comparator.run_all(rounds=5, iterations=1)
fastest_name, fastest_data = comparator.get_fastest()
stable_name, stable_data = comparator.get_most_stable()
comparator.display_table()
comparator.export_results(filepath: str)
comparator.clear()
```
