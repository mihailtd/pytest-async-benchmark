---
title: Concurrency Benchmarking
description: Measure throughput, tail latency percentiles, error rates, and event loop lag under load with async_benchmark.concurrent.
---

# Concurrency Benchmarking

Sequential benchmarks measure raw execution speed in isolation. However, asynchronous applications (FastAPI endpoints, message queues, MCP tool servers) primarily operate under **concurrent load**.

Under concurrency, coroutines contend for CPU slices, connection pools, and event-loop time. `async_benchmark.concurrent()` tests how your code performs when multiple operations are in flight simultaneously.

## Basic Usage

Call `async_benchmark.concurrent()` with:
- `concurrency`: Maximum number of coroutines running concurrently.
- `total`: Total number of invocations to complete.
- `timeout` *(optional)*: Maximum per-call timeout in seconds.
- `leak_check` *(optional)*: Check for unawaited orphan tasks.

```python
import asyncio
import pytest


async def handle_request(client_id: int):
    # Simulate database query and serialization
    await asyncio.sleep(0.005)
    return {"status": "ok", "client": client_id}


@pytest.mark.asyncio
async def test_under_load(async_benchmark):
    # 20 requests in flight simultaneously, 200 total requests
    stats = await async_benchmark.concurrent(
        handle_request,
        client_id=1,
        concurrency=20,
        total=200,
    )

    print(f"Throughput: {stats.ops:.1f} ops/sec")
    print(f"Median: {stats.median * 1000:.2f} ms")
    print(f"95th percentile: {stats.p95 * 1000:.2f} ms")
    print(f"99th percentile: {stats.p99 * 1000:.2f} ms")
    print(f"Loop Lag: {stats.loop_lag * 1000:.2f} ms")

    assert stats.errors == 0
    assert stats.timeouts == 0
    assert stats.p95 < 0.015  # Under 15ms under load
```

## Result Fields: `ConcurrentBenchmarkResult`

The returned result object provides comprehensive load performance data:

| Attribute | Type | Description |
|---|---|---|
| `ops` | `float` | Throughput in operations per second (`completed / total_time`) |
| `total_time` | `float` | Total elapsed wall-clock duration in seconds |
| `concurrency` | `int` | Maximum concurrent calls in flight |
| `total` | `int` | Target number of total calls |
| `completed` | `int` | Successfully finished calls |
| `errors` | `int` | Number of calls that raised exceptions |
| `timeouts` | `int` | Number of calls that timed out |
| `loop_lag` | `float` | Maximum event-loop scheduler delay in seconds |
| `mean` | `float` | Mean duration per call |
| `min` | `float` | Minimum call duration |
| `max` | `float` | Maximum call duration |
| `median` | `float` | Median (50th percentile) duration |
| `p50` | `float` | 50th percentile latency |
| `p75` | `float` | 75th percentile latency |
| `p90` | `float` | 90th percentile latency |
| `p95` | `float` | 95th percentile latency |
| `p99` | `float` | 99th percentile latency |
| `samples` | `list[float]` | Individual latency durations for all completed calls |

## Error and Timeout Handling

When benchmarking flaky network services or connection pools under heavy load, calls may fail or time out. `pytest-async-benchmark` tracks these explicitly without crashing the benchmark run:

```python
@pytest.mark.asyncio
async def test_resilience(async_benchmark):
    stats = await async_benchmark.concurrent(
        flaky_network_call,
        concurrency=50,
        total=500,
        timeout=0.05,  # 50ms deadline
    )

    # Assert that errors remain within SLA limits:
    error_rate = (stats.errors + stats.timeouts) / stats.total
    assert error_rate < 0.02  # Less than 2% failure rate
```

If **all** calls fail, the runner raises a `RuntimeError` with details of the underlying exception.

## Measuring Event Loop Lag

Asynchronous Python runs on a single OS thread via cooperative multitasking. If a handler performs synchronous blocking operations (e.g. `time.sleep()`, heavy hashing, regexes without yielding), it starves all other coroutines on the loop.

During concurrency runs, `pytest-async-benchmark` runs a background timer measuring how far the loop drifts from its target schedule.

```python
assert stats.loop_lag < 0.005  # Loop lag should stay under 5ms
```

A high `loop_lag` warns you that CPU-bound code is choking your event loop and should be offloaded to `asyncio.to_thread()` or `ProcessPoolExecutor`.
