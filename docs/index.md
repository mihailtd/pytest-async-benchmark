---
layout: home
title: pytest-async-benchmark
titleTemplate: Modern pytest benchmarking for async Python
description: High-precision pytest benchmarking for async Python coroutines. Real latency distributions, concurrency under load, task leak detection, and regression tracking.

hero:
  name: pytest-async-benchmark
  text: Modern pytest benchmarking for async Python
  tagline: Built specifically for async def coroutines. True latency percentiles (p50-p99), concurrency load testing, task leak detection, and statistically sound regression tests.
  image:
    src: /logo.svg
    alt: pytest-async-benchmark logo
  actions:
    - theme: brand
      text: Get Started
      link: /guide/getting-started
    - theme: alt
      text: Concurrency Benchmarks
      link: /guide/concurrency
    - theme: alt
      text: GitHub
      link: https://github.com/mihailtd/pytest-async-benchmark

features:
  - title: Native Async & Await
    details: Works directly inside pytest-asyncio test coroutines or standard sync test functions. Zero boilerplate, zero loop hackery.
    link: /guide/how-it-works
    linkText: How it works
  - title: Real Latency Distributions
    details: Times every individual call instead of batch averages. Measures min, max, mean, median, stddev, and true p50, p75, p90, p95, p99.
    link: /guide/getting-started#comprehensive-statistics
    linkText: Latency metrics
  - title: Concurrency Under Load
    details: Benchmark with N calls in flight at once. Reports throughput (ops/sec), latency percentiles, timeouts, errors, and event-loop lag.
    link: /guide/concurrency
    linkText: Concurrency benchmarks
  - title: Pedantic Setup & Teardown
    details: Run per-iteration setup and cleanup for database transactions or mocks, completely excluded from measured execution time.
    link: /guide/pedantic-mode
    linkText: Pedantic mode
  - title: Asyncio Task Leak Check
    details: Automatically detects orphan background tasks spawned by unawaited coroutines or leaky client libraries before they corrupt tests.
    link: /guide/leak-detection
    linkText: Leak detection
  - title: Regression Guard in CI
    details: Compare against saved baselines. Fails CI only on statistically verified slowdowns using the non-parametric Mann-Whitney U test.
    link: /guide/regression-detection
    linkText: CI regression guard
---

<div class="home-sections">

<section class="home-section">

<p class="eyebrow">Quick Example</p>

## Benchmark async code with natural pytest syntax

Install `pytest-async-benchmark` and benchmark your coroutines with standard pytest fixtures:

```python
import asyncio
import pytest


async def fetch_user_data(user_id: int):
    await asyncio.sleep(0.005)  # simulated network I/O
    return {"id": user_id, "status": "active"}


@pytest.mark.asyncio
async def test_fetch_latency(async_benchmark):
    # Benchmark the coroutine function with auto-calibrated runs
    result = await async_benchmark(fetch_user_data, 42)

    # Assert on real p95/p99 percentiles or throughput
    assert result["p95"] < 0.010
    assert result["ops"] > 100
```

<div class="home-figure">
  <img src="/screenshots/benchmark-results.png" alt="pytest-async-benchmark terminal output" />
</div>

</section>

<section class="home-section">

<p class="eyebrow">Concurrency Benchmarking</p>

## Measure throughput and event loop lag under real concurrency

Sequential benchmarks tell you how fast code runs in isolation; concurrency benchmarks tell you how it behaves under load.

```python
@pytest.mark.asyncio
async def test_api_concurrency(async_benchmark):
    # Run 100 total requests with 20 requests in flight simultaneously
    stats = await async_benchmark.concurrent(
        fetch_user_data,
        42,
        concurrency=20,
        total=100,
        leak_check=True,
    )

    print(f"Throughput: {stats.ops:.1f} ops/sec")
    print(f"p99 Latency: {stats.p99 * 1000:.2f} ms")
    print(f"Loop Lag: {stats.loop_lag * 1000:.2f} ms")
```

```mermaid
flowchart LR
    A["Test Runner"] --> B["async_benchmark.concurrent(N=20, Total=100)"]
    B --> C["Worker Pool (In-Flight Coroutines)"]
    C --> D["Per-Call Timing Samples"]
    C --> E["Background Task Monitor"]
    D --> F["Percentiles (p50-p99) & Ops/sec"]
    E --> G["Task Leak Detection"]
```

<div class="home-figure">
  <img src="/screenshots/concurrency-results.png" alt="pytest-async-benchmark concurrency results" />
</div>

</section>

<section class="home-section">

<p class="eyebrow">CI Regression Guard</p>

## Catch performance regressions before they land in production

Save historical baselines and prevent silent slowdowns in CI. To eliminate false alarms from noisy cloud runners, `pytest-async-benchmark` applies a one-sided **Mann-Whitney U test** across individual call samples, only failing your pipeline when a regression is both substantive and statistically significant ($p < 0.05$).

```bash
# Compare against baseline and fail if median latency regresses by >10%
pytest --async-bench-compare --async-bench-compare-fail=median:10%
```

<div class="home-figure home-figure-wide">
  <img src="/screenshots/regression-results.png" alt="pytest-async-benchmark CI regression detection" />
</div>

<div class="capabilities" style="margin-top: 24px;">
  <div class="capability">
    <h3>Zero CI Flakiness</h3>
    <p>Replaces fragile fixed cutoffs with non-parametric Mann-Whitney U testing, ignoring transient VM neighbor spikes.</p>
  </div>
  <div class="capability">
    <h3>Automated Baselines</h3>
    <p><code>--async-bench-autosave</code> records numbered runs in <code>.async_benchmarks/</code> with Git commit SHA and host hardware metadata.</p>
  </div>
  <div class="capability">
    <h3>JSON Export</h3>
    <p>Export all raw percentiles and per-call sample arrays via <code>--async-bench-json</code> for dashboard ingestion and PR comments.</p>
  </div>
</div>

</section>

<section class="home-section">

<p class="eyebrow">From the Author</p>

## Deep dives into async architecture and performance

Articles written by Mihai Farcas on building performant Python architectures, AI agents, and type systems:

<WritingCards />

</section>

<section class="home-section">

<p class="eyebrow">Latest Updates</p>

## What's new in pytest-async-benchmark

<ReleaseHighlights />

</section>

</div>
