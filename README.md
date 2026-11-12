# pytest-async-benchmark 🚀

Modern pytest benchmarking for async code with beautiful terminal output and advanced comparison tools.

[![PyPI version](https://img.shields.io/pypi/v/pytest-async-benchmark.svg)](https://pypi.org/project/pytest-async-benchmark/)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-async-benchmark.svg)](https://pypi.org/project/pytest-async-benchmark/)
[![Documentation](https://img.shields.io/badge/docs-GitHub_Pages-blue.svg)](https://mihailtd.github.io/pytest-async-benchmark/)
[![Blog](https://img.shields.io/badge/blog-mihai.ltd-blue.svg)](https://mihai.ltd/blog/why-i-built-pytest-async-benchmark/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 📖 **Full Documentation**: Visit [https://mihailtd.github.io/pytest-async-benchmark/](https://mihailtd.github.io/pytest-async-benchmark/) for complete guides, concurrency tutorials, and framework examples.
>
> ✍️ **Deep Dive**: Read [Why I Built pytest-async-benchmark: Real Latency Distributions for Async Python](https://mihai.ltd/blog/why-i-built-pytest-async-benchmark/) on [mihai.ltd](https://mihai.ltd).

## ✨ Features

- 🎯 **Async-First**: Designed specifically for benchmarking `async def` functions
- 🔌 **Pytest Integration**: Seamless integration as a pytest plugin with full **pytest-asyncio** support
- 🎨 **Rich Output**: Beautiful terminal reporting powered by Rich!
- 📊 **Comprehensive Stats**: Every call is timed individually: min, max, mean, median, std dev, p50/p75/p90/p95/p99, ops/sec
- 🚦 **Concurrency Benchmarking**: `async_benchmark.concurrent()` reports throughput, latency under load, errors, timeouts and event loop lag
- 📈 **Regression Detection**: Save runs, compare against a baseline, and fail CI only on statistically significant slowdowns
- 🧹 **Task Leak Detection**: Optionally fail or warn when a benchmark leaves asyncio tasks running
- 💾 **JSON Export**: `--async-bench-json` writes every result, including per-call samples
- ⚖️ **A vs B Comparisons**: Compare different implementations side-by-side
- 📈 **Multi-Scenario Analysis**: Benchmark multiple scenarios with detailed comparison tables
- 🎯 **Performance Grading**: Automatic performance scoring and analysis
- ⚡ **Auto Calibration**: Without `rounds`, measurement runs for a time budget (1s by default) instead of a fixed 5 calls
- 🔄 **Quick Compare**: One-line comparison utilities
- 🏆 **Winner Detection**: Automatic identification of best-performing implementation
- 🚀 **Easy to Use**: Simple fixture-based API with native `async`/`await` support
- 🔧 **pytest-asyncio Compatible**: Works perfectly with pytest-asyncio's event loop management
- 🌐 **Framework Friendly**: Works with any async code, including **FastAPI**, **FastMCP**, Quart, aiohttp and more (see [Real-World Examples](#-real-world-examples))

## 📦 Installation

### For Existing pytest-asyncio Users 🚀
**Already testing async APIs (FastAPI, Quart, aiohttp)?** You're all set with the basic installation:

```bash
pip install pytest-async-benchmark
# or
uv add pytest-async-benchmark
```

You'll get the full async/await experience immediately since you already have pytest-asyncio!

### For New Users
Choose your installation based on your needs:

```bash
# Full installation with async/await support (recommended)
pip install pytest-async-benchmark[asyncio]
uv add pytest-async-benchmark --optional asyncio

# Basic installation (simple interface)
pip install pytest-async-benchmark
uv add pytest-async-benchmark
```

### Quick Check ✅
Already using `@pytest.mark.asyncio` in your tests? Then the basic installation is all you need:

```python
# If you already have tests like this:
@pytest.mark.asyncio
async def test_my_api():
    # Your existing async test code
    pass


# Then just add pytest-async-benchmark and use:
@pytest.mark.asyncio
async def test_my_api_performance(async_benchmark):
    result = await async_benchmark(my_async_function)
    assert result["mean"] < 0.01
```

## 🚀 Quick Start

pytest-async-benchmark automatically adapts to your environment, providing **two convenient interfaces**:

### Async Interface (with pytest-asyncio)
When pytest-asyncio is installed, use the natural async/await syntax:

```python
import asyncio
import pytest


async def slow_async_operation():
    await asyncio.sleep(0.01)  # 10ms
    return "result"


@pytest.mark.asyncio
@pytest.mark.async_benchmark(rounds=5, iterations=10)
async def test_async_performance(async_benchmark):
    # Use await with pytest-asyncio for best experience
    result = await async_benchmark(slow_async_operation)

    # Your assertions here
    assert result["mean"] < 0.02
```

### Simple Interface (without pytest-asyncio)
For simpler setups, the sync interface works automatically:

```python
import asyncio
import pytest


async def slow_async_operation():
    await asyncio.sleep(0.01)
    return "result"


@pytest.mark.async_benchmark(rounds=5, iterations=10)
def test_sync_performance(async_benchmark):
    # No await needed - sync interface
    result = async_benchmark(slow_async_operation)

    # Your assertions here
    assert result["mean"] < 0.02  # Should complete in under 20ms
```

### Flexible Configuration Syntax

pytest-async-benchmark supports **two syntax options** for configuring benchmarks:

#### Option 1: Marker Syntax (Recommended)
```python
@pytest.mark.async_benchmark(rounds=5, iterations=10)
async def test_with_marker(async_benchmark):
    result = await async_benchmark(slow_async_operation)
    assert result["rounds"] == 5  # From marker
```

#### Option 2: Function Parameter Syntax
```python
async def test_with_parameters(async_benchmark):
    result = await async_benchmark(slow_async_operation, rounds=5, iterations=10)
    assert result["rounds"] == 5  # From function parameters
```

## 🔧 Interface Detection & Flexibility

pytest-async-benchmark **automatically detects** your environment and provides the best interface:

### With pytest-asyncio (Recommended)
When pytest-asyncio is installed, use natural async/await syntax:

```python
# Set in your pyproject.toml for automatic async test detection
[tool.pytest.ini_options]
asyncio_mode = "auto"


# Then use await syntax
@pytest.mark.asyncio
async def test_my_benchmark(async_benchmark):
    result = await async_benchmark(my_async_function)
    # Your assertions here
```

**Benefits of pytest-asyncio integration:**
- ✅ Native `async`/`await` syntax support
- ✅ Automatic event loop management
- ✅ No `RuntimeError: cannot be called from a running event loop`
- ✅ Better compatibility with async frameworks like FastAPI, Quart, aiohttp
- ✅ Cleaner test code with standard async patterns

### Without pytest-asyncio (Simple Setup)
When pytest-asyncio is not available, the simple interface works automatically:

```python
# No pytest-asyncio required
def test_my_benchmark(async_benchmark):
    result = async_benchmark(my_async_function)  # No await needed
    # Your assertions here
```

**Benefits of simple interface:**
- ✅ No additional dependencies required
- ✅ Simpler setup for basic use cases
- ✅ Perfect for getting started quickly
- ✅ Automatic event loop management internally

## 🎯 Core Usage Examples

### Interface Flexibility

#### Async Interface (with pytest-asyncio)
```python
@pytest.mark.asyncio
@pytest.mark.async_benchmark(rounds=10, iterations=100, warmup_rounds=2)
async def test_with_marker(async_benchmark):
    """Use marker for consistent, visible configuration."""
    result = await async_benchmark(my_async_function)
    assert result["rounds"] == 10  # Configuration is explicit and visible
```

#### Simple Interface (without pytest-asyncio)
```python
@pytest.mark.async_benchmark(rounds=10, iterations=100, warmup_rounds=2)
def test_with_marker_sync(async_benchmark):
    """Use marker for consistent, visible configuration - simple style."""
    result = async_benchmark(my_async_function)  # No await needed
    assert result["rounds"] == 10  # Configuration is explicit and visible
```

### Two Configuration Syntaxes

#### Marker Syntax (Declarative)
```python
# With pytest-asyncio
@pytest.mark.asyncio
@pytest.mark.async_benchmark(rounds=10, iterations=100, warmup_rounds=2)
async def test_with_marker_async(async_benchmark):
    result = await async_benchmark(my_async_function)
    assert result["rounds"] == 10


# Without pytest-asyncio
@pytest.mark.async_benchmark(rounds=10, iterations=100, warmup_rounds=2)
def test_with_marker_sync(async_benchmark):
    result = async_benchmark(my_async_function)
    assert result["rounds"] == 10
```

#### Function Parameter Syntax (Dynamic)
```python
# With pytest-asyncio
@pytest.mark.asyncio
async def test_with_parameters_async(async_benchmark):
    result = await async_benchmark(
        my_async_function, rounds=10, iterations=100, warmup_rounds=2
    )
    assert result["rounds"] == 10


# Without pytest-asyncio
def test_with_parameters_simple(async_benchmark):
    result = async_benchmark(
        my_async_function, rounds=10, iterations=100, warmup_rounds=2
    )
    assert result["rounds"] == 10
```

#### Combined Syntax (Override)
Both interfaces support parameter precedence where function parameters override marker settings:

```python
@pytest.mark.async_benchmark(rounds=5, iterations=50)  # Default config
async def test_with_override(
    async_benchmark,
):  # Works with or without @pytest.mark.asyncio
    """Function parameters override marker settings."""
    result = await async_benchmark(  # Use 'await' only with pytest-asyncio
        my_async_function,
        rounds=20,  # This overrides marker's rounds=5
        # iterations=50 comes from marker
    )
    assert result["rounds"] == 20  # Function parameter wins
    assert result["iterations"] == 50  # From marker
```

### Basic Benchmarking

```python
@pytest.mark.asyncio
async def test_my_async_function(async_benchmark):
    async def my_function():
        # Your async code here
        await some_async_operation()
        return result

    # Benchmark with default settings (5 rounds, 1 iteration each)
    stats = await async_benchmark(my_function)

    # Access comprehensive timing statistics
    print(f"Mean execution time: {stats['mean']:.3f}s")
    print(f"Standard deviation: {stats['stddev']:.3f}s")
    print(f"95th percentile: {stats['p95']:.3f}s")
```

### Advanced Configuration

### 🔬 Pedantic Mode (Setup & Teardown Excluded from Timing)

When benchmarking async operations that require per-iteration setup (e.g. creating fresh databases, initializing connection pools, or preparing test fixtures) and teardown, setup/cleanup overhead pollutes the timing results.

`async_benchmark.pedantic()` runs setup before and teardown after each iteration, but strictly measures **only the target operation**:

```python
@pytest.mark.asyncio
async def test_database_indexing(async_benchmark):
    async def setup():
        db = await create_fresh_database()
        return db

    async def teardown(db):
        await db.close()

    async def index_records(db):
        await db.execute("CREATE INDEX idx_user ON users(email)")

    result = await async_benchmark.pedantic(
        index_records,
        setup=setup,
        teardown=teardown,
        rounds=10,
        iterations=1,
    )
    assert result["mean"] < 0.05
```

**Key Features:**
- ⚡ **Zero Setup/Teardown Overhead**: Setup and teardown times are excluded from benchmark measurements.
- 🔄 **Sync or Async Hooks**: Both `setup` and `teardown` can be synchronous functions or `async def` coroutines.
- 📦 **Argument Passing**: Return value from `setup` is passed as argument(s) to the target function and `teardown`. Unpacks tuples automatically if returned.
- 🛡️ **Safe Cleanup**: Teardown runs in a `finally` block even if the target encounters an error.
- 🌓 **Dual Interface**: Supports `await async_benchmark.pedantic(...)` or synchronous `async_benchmark.pedantic(...)`.

## 🎯 Two Configuration Syntaxes

pytest-async-benchmark offers **two flexible ways** to configure your benchmarks:

### 🏷️ Marker Syntax (Recommended)

Use pytest markers for **declarative, visible configuration**:

```python
@pytest.mark.asyncio
@pytest.mark.async_benchmark(rounds=10, iterations=100, warmup_rounds=2)
async def test_high_precision_benchmark(async_benchmark):
    """High precision benchmark with marker configuration."""
    result = await async_benchmark(my_async_function)

    # Configuration is visible and consistent
    assert result["rounds"] == 10
    assert result["iterations"] == 100
```

**Benefits:**
- ✅ **Visible configuration** - Parameters are clear at test level
- ✅ **IDE support** - Better tooling and autocomplete
- ✅ **Test discovery** - Easy to find all benchmark tests
- ✅ **Consistent configs** - Same settings across related tests

### ⚙️ Function Parameter Syntax

Use function parameters for **dynamic, flexible configuration**:

```python
@pytest.mark.asyncio
async def test_dynamic_benchmark(async_benchmark):
    """Dynamic benchmark with runtime configuration."""
    # Configuration can be computed or conditional
    rounds = 20 if is_production else 5

    result = await async_benchmark(
        my_async_function, rounds=rounds, iterations=50, warmup_rounds=1
    )
```

**Benefits:**
- ✅ **Dynamic configuration** - Runtime parameter calculation
- ✅ **Conditional logic** - Different configs based on environment
- ✅ **Per-call customization** - Each benchmark call can differ

### 🔄 Combined Syntax (Best of Both)

**Function parameters override marker parameters**:

```python
@pytest.mark.asyncio
@pytest.mark.async_benchmark(rounds=5, iterations=50, warmup_rounds=1)
async def test_with_overrides(async_benchmark):
    """Use marker defaults with selective overrides."""

    # Quick test with marker defaults
    quick_result = await async_benchmark(fast_function)

    # Precision test with overridden rounds
    precise_result = await async_benchmark(
        slow_function,
        rounds=20,  # Overrides marker's rounds=5
        # iterations=50 and warmup_rounds=1 come from marker
    )

    assert quick_result["rounds"] == 5  # From marker
    assert precise_result["rounds"] == 20  # From function override
```

### Traditional Configuration

```python
@pytest.mark.asyncio
async def test_with_custom_settings(async_benchmark):
    result = await async_benchmark(
        my_async_function,
        rounds=10,  # Number of rounds to run
        iterations=5,  # Iterations per round
        warmup_rounds=2,  # Warmup rounds before measurement
    )
```

### With Function Arguments

```python
@pytest.mark.asyncio
async def test_with_args(async_benchmark):
    async def process_data(data, multiplier=1):
        # Process the data
        await asyncio.sleep(0.01)
        return len(data) * multiplier

    result = await async_benchmark(
        process_data,
        "test_data",  # positional arg
        multiplier=2,  # keyword arg
        rounds=3,
    )
```

## ⚖️ A vs B Comparison Features

### Quick Comparison

```python
from pytest_async_benchmark import quick_compare


async def algorithm_v1():
    await asyncio.sleep(0.002)  # 2ms
    return "v1_result"


async def algorithm_v2():
    await asyncio.sleep(0.0015)  # 1.5ms - optimized
    return "v2_result"


# Quick one-liner comparison
def test_algorithm_comparison():
    winner, results = quick_compare(algorithm_v1, algorithm_v2, rounds=5)
    assert winner == "algorithm_v2"  # v2 should be faster
```

### Detailed A vs B Analysis

```python
from pytest_async_benchmark import a_vs_b_comparison


def test_detailed_comparison():
    # Compare with beautiful terminal output
    a_vs_b_comparison(
        "Original Algorithm",
        algorithm_v1,
        "Optimized Algorithm",
        algorithm_v2,
        rounds=8,
        iterations=20,
    )
```

### Multi-Scenario Benchmarking

```python
from pytest_async_benchmark import BenchmarkComparator


def test_multi_scenario():
    comparator = BenchmarkComparator()

    # Add multiple scenarios
    comparator.add_scenario(
        "Database Query v1",
        db_query_v1,
        rounds=5,
        iterations=10,
        description="Original database implementation",
    )

    comparator.add_scenario(
        "Database Query v2",
        db_query_v2,
        rounds=5,
        iterations=10,
        description="Optimized with connection pooling",
    )

    # Run comparison and get results
    results = comparator.run_comparison()

    # Beautiful comparison table automatically displayed
    # Access programmatic results
    fastest = results.get_fastest_scenario()
    assert fastest.name == "Database Query v2"
```

## 🚦 Concurrency Benchmarking

Async code is about concurrency, so measuring one call at a time misses a whole class of problems. `async_benchmark.concurrent()` runs `total` calls with `concurrency` of them in flight at once:

```python
@pytest.mark.asyncio
async def test_fetch_under_load(async_benchmark, client):
    async def fetch_item():
        response = await client.get("/items/1")
        response.raise_for_status()

    result = await async_benchmark.concurrent(
        fetch_item,
        concurrency=50,  # calls in flight at once
        total=1000,  # calls in total
        timeout=1.0,  # optional per-call timeout
    )

    assert result["errors"] == 0
    assert result["p99"] < 0.1  # latency under load
    assert result["loop_lag_max"] < 0.05  # nothing blocks the event loop
    print(f"{result['throughput']:.0f} calls/s")
```

**What it reports:**

| Key | Meaning |
|---|---|
| `throughput` | Completed calls per second of wall time |
| `p50` … `p99`, `min`, `max`, `mean` | Latency of successful calls, timed per call from when a worker starts it |
| `errors`, `error_types`, `first_error` | Calls that raised (counted, not timed). `error_types` maps exception names to counts |
| `timeouts` | Calls that exceeded `timeout` (counted, not timed) |
| `completed`, `total`, `concurrency`, `wall_time` | What actually ran |
| `loop_lag_mean`, `loop_lag_p99`, `loop_lag_max` | How late a short `asyncio.sleep` woke up during the run. High lag means something blocked the event loop |

**How it works:** a fixed pool of `concurrency` workers pulls from a shared counter until `total` calls are done. It's a closed-loop model: like N clients that each send their next request as soon as the previous one returns. A few warmup calls (one per worker by default, configurable with `warmup=`) run first and aren't measured. If every call fails, it raises instead of reporting empty statistics.

**What it's good for:** catching problems that only appear under concurrency, such as a connection pool smaller than your concurrency, a lock held across I/O that serializes callers, or a blocking call (`time.sleep`, a sync database driver, heavy CPU work) stalling the event loop. See [`examples/concurrency_examples.py`](examples/concurrency_examples.py) for each of these.

> ⚠️ **This is not a load test.** Everything runs in one process and one event loop. When you benchmark a FastAPI app through `httpx.ASGITransport`, the client and the app share that loop and that CPU core, so `throughput` describes that setup, not what your deployed service can handle. To measure production capacity, use a load-testing tool such as [Locust](https://locust.io/) or [k6](https://k6.io/) against a real deployment. Use `concurrent()` to compare implementations and catch regressions in how your code behaves under concurrency.

Concurrency settings can also come from the marker: `@pytest.mark.async_benchmark(concurrency=20, total=500, timeout=1.0)`.

## 🧹 Task Leak Detection

A common async bug is starting a background task (`asyncio.create_task`, `ensure_future`) and never awaiting or cancelling it. Turn on `leak_check` to catch it:

```python
@pytest.mark.asyncio
async def test_no_dangling_tasks(async_benchmark):
    result = await async_benchmark(my_handler, leak_check=True)
    # raises TaskLeakError if my_handler left asyncio tasks running
```

- `leak_check=True` (or `"fail"`) raises `TaskLeakError`, a subclass of `AssertionError`, naming the leaked tasks.
- `leak_check="warn"` emits a `TaskLeakWarning` instead.
- It works with `async_benchmark(...)`, `.pedantic(...)` and `.concurrent(...)`, via the marker (`@pytest.mark.async_benchmark(leak_check="warn")`), or for every benchmark with `--async-bench-leak-check=warn|fail`.

The task snapshot is taken **after warmup**, so a background task that a library starts once on first use (such as a connection pool's keepalive) isn't reported as a leak.

## 📈 Saving Results & Catching Regressions in CI

The command-line options follow [pytest-benchmark](https://pytest-benchmark.readthedocs.io/)'s conventions, with an `--async-bench-` prefix.

```bash
# Export every result (including per-call samples) as JSON
pytest --async-bench-json=benchmarks.json

# Save this run as a baseline: .async_benchmarks/<machine-id>/0001_<commit>_<time>.json
pytest --async-bench-autosave

# Compare against the latest saved run, and fail on a significant slowdown of >10% in the median
pytest --async-bench-compare --async-bench-compare-fail=median:10%
```

**Why not just a percentage threshold?** Shared CI runners easily vary 10-20% between runs, so a plain "fail if more than 15% slower" rule fails builds at random. A benchmark only counts as a regression when it is **both**:

1. slower than the baseline by more than your `--async-bench-compare-fail` threshold, **and**
2. significantly slower according to a one-sided [Mann-Whitney U test](https://en.wikipedia.org/wiki/Mann%E2%80%93Whitney_U_test) on the per-call samples (p < 0.05 by default).

Benchmarks with fewer than 5 samples on either side are reported as `insufficient samples` and never fail the build. The test runs in pure Python, so there's no SciPy dependency.

The comparison table is printed at the end of the session:

```
                                 Comparison with baseline (median latency)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Benchmark                          ┃ Baseline ┃ Current ┃ Change ┃ p (slower) ┃ Status                  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ tests/test_api.py::test_get_user   │  1.055ms │ 2.059ms │ +95.2% │   1.51e-11 │ regression (median:10%) │
│ tests/test_api.py::test_list_users │  2.057ms │ 2.058ms │  +0.0% │      0.163 │ unchanged               │
└────────────────────────────────────┴──────────┴─────────┴────────┴────────────┴─────────────────────────┘
❌ 1 benchmark(s) regressed beyond --async-bench-compare-fail thresholds
```

Statuses: `regression` (fails the session), `slower` (significant, but within your thresholds), `faster`, `unchanged`, `insufficient samples`, and `new` (not in the baseline).

| Option | Description |
|---|---|
| `--async-bench-json=PATH` | Write all results to `PATH` as JSON |
| `--async-bench-autosave` | Save results as the next numbered run in the storage directory |
| `--async-bench-storage=DIR` | Storage directory (default `.async_benchmarks`) |
| `--async-bench-compare[=NUM\|PATH]` | Compare with the latest saved run, run number `NUM`, or a JSON file |
| `--async-bench-compare-fail=EXPR` | Fail on a significant regression beyond `EXPR`: `metric:N%` or `metric:SECONDS`. Metrics: `min`, `max`, `mean`, `median`, `p50`-`p99`. Repeatable |
| `--async-bench-compare-alpha=A` | Significance level for the Mann-Whitney U test (default `0.05`) |
| `--async-bench-max-time=SECONDS` | Time budget for calibrating rounds when none are given (default `1.0`) |
| `--async-bench-leak-check=warn\|fail` | Turn on task leak detection for every benchmark |

`max_time` and the leak check can also be set once in your pytest configuration. A command-line flag overrides it:

```toml
# pyproject.toml
[tool.pytest.ini_options]
async_bench_max_time = "0.5"     # "0" = the minimum of 5 rounds, like v0.3.0
async_bench_leak_check = "warn"  # off | warn | fail
```

**A typical CI setup** compares against a baseline saved from your main branch:

```bash
# On main: produce the baseline (cache or upload .async_benchmarks/ as a CI artifact)
pytest tests/benchmarks --async-bench-autosave

# On pull requests: restore .async_benchmarks/, then compare
pytest tests/benchmarks --async-bench-compare --async-bench-compare-fail=median:15%
```

Baselines are stored per machine ID (OS, Python implementation and version), because timings from different machines aren't comparable. For the most reliable results, compare runs from the same runner type. Each saved run includes git commit info. The saved files keep up to 10,000 samples per benchmark, evenly downsampled from larger runs. No hostname is recorded.

## 📊 Comprehensive Statistics

Each benchmark times **every call individually** and returns:

```python
{
    "min": 0.001234,  # Fastest call
    "max": 0.005678,  # Slowest call
    "mean": 0.002456,  # Mean call duration
    "median": 0.002123,  # Median call duration (same as p50)
    "stddev": 0.000234,  # Standard deviation
    "p50": 0.002123,  # Percentiles (linear interpolation, like NumPy)
    "p75": 0.002801,
    "p90": 0.003456,
    "p95": 0.004123,
    "p99": 0.004789,
    "ops": 407.2,  # Calls per second (1 / mean)
    "count": 120,  # Number of timed calls
    "total_time": 0.294,  # Sum of all call durations
    "rounds": 120,  # Rounds executed
    "iterations": 1,  # Calls per round
    "calibrated": True,  # Rounds were chosen automatically
    "mode": "sequential",  # "sequential", "pedantic" or "concurrent"
    "samples": [...],  # Every call's duration, in seconds
    "raw_times": [...],  # Mean duration of each round
}
```

All times are in seconds. With `leak_check` enabled, results also include `leaked_tasks`.

**Calibration:** when `rounds` isn't given (as an argument or in the marker), the benchmark keeps measuring until it has spent `max_time` seconds (default 1.0s), with at least 5 rounds and at most 10,000. Pass `rounds=` for a fixed count, or `max_time=` (or `--async-bench-max-time`, or `async_bench_max_time` in your pytest config) to change the budget.

## 🎨 Beautiful Terminal Output

### Basic Benchmark Output

```
   🚀 Async Benchmark Results:
        test_my_function
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Metric     ┃ Value            ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ Min        │ 10.048ms         │
│ Median     │ 10.066ms         │
│ Mean       │ 10.072ms         │
│ p95        │ 10.084ms         │
│ p99        │ 10.143ms         │
│ Max        │ 10.513ms         │
│ Std Dev    │ 45.789μs         │
│ Ops/sec    │ 99.3             │
│ Samples    │ 100              │
│ Rounds     │ 100 (calibrated) │
│ Iterations │ 1                │
└────────────┴──────────────────┘
✅ Benchmark completed successfully!
```

### A vs B Comparison Output

```
⚖️  A vs B Comparison Results
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Scenario                ┃ Algorithm A ┃ Algorithm B ┃ Winner    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Mean Time              │ 2.456ms     │ 1.789ms     │ B 🏆      │
│ Median Time            │ 2.234ms     │ 1.678ms     │ B 🏆      │
│ 95th Percentile        │ 3.456ms     │ 2.345ms     │ B 🏆      │
│ Standard Deviation     │ 0.567ms     │ 0.234ms     │ B 🏆      │
│ Performance Grade      │ B (76.2)    │ A (89.1)    │ B 🏆      │
│ Improvement            │ -           │ 27.2%       │ -         │
└─────────────────────────┴─────────────┴─────────────┴───────────┘
🏆 Winner: Algorithm B (27.2% faster)
```

## 🏗️ Project Structure

```
pytest-async-benchmark/
├── src/
│   └── pytest_async_benchmark/
│       ├── __init__.py          # Main exports and API
│       ├── plugin.py            # Pytest plugin and fixtures
│       ├── runner.py            # Core benchmarking engine
│       ├── display.py           # Rich terminal output formatting
│       ├── stats.py             # Statistics and percentiles
│       ├── storage.py           # JSON export, autosave and baselines
│       ├── regression.py        # Noise-aware comparison (Mann-Whitney U)
│       ├── utils.py             # Utility functions
│       ├── analytics.py         # Performance analysis tools
│       └── comparison.py        # A vs B comparison functionality
├── examples/
│   ├── pytest_examples.py      # Comprehensive pytest usage examples
│   ├── concurrency_examples.py  # Pool starvation, locks, blocking calls
│   ├── fastapi_examples.py      # FastAPI endpoint benchmarking
│   ├── fastmcp_examples.py      # FastMCP tool/resource benchmarking
│   ├── quart_api_comparison.py  # Real-world API endpoint comparison
│   └── comparison_examples.py   # Advanced comparison features demo
├── tests/
│   ├── test_async_bench.py      # Core functionality tests
│   ├── test_comparison.py       # Comparison feature tests
│   ├── test_demo.py             # Demo test cases
│   └── conftest.py              # Test configuration
├── pyproject.toml               # Package configuration
└── README.md                    # This file
```

## 📚 Example Files Guide

### 🔧 [`examples/pytest_examples.py`](examples/pytest_examples.py)
Comprehensive pytest usage examples including:
- Basic benchmarking with the `async_benchmark` fixture
- Advanced configuration options
- Performance assertions and testing patterns
- Using markers for benchmark organization

### 🚦 [`examples/concurrency_examples.py`](examples/concurrency_examples.py)
Bugs that only appear under concurrency, and how `concurrent()` exposes them:
- Connection pool starvation (tail latency balloons)
- A lock held across I/O that serializes callers
- A blocking call that stalls the event loop (loop lag)
- Timeouts and errors as part of the result

### ⚡ [`examples/fastapi_examples.py`](examples/fastapi_examples.py)
FastAPI endpoint benchmarking:
- In-process calls via `httpx.ASGITransport` (no server, no network)
- Latency budgets with both fixture and marker syntax
- A vs B comparison of two endpoint implementations

### 🤖 [`examples/fastmcp_examples.py`](examples/fastmcp_examples.py)
FastMCP server benchmarking:
- MCP tool and resource round-trip latency
- In-memory client transport (no subprocess, no stdio)
- A vs B comparison of two tool implementations

### 🌐 [`examples/quart_api_comparison.py`](examples/quart_api_comparison.py)
Real-world API endpoint comparison demo featuring:
- Quart web framework setup
- API v1 vs v2 endpoint benchmarking
- Live server testing with actual HTTP requests
- Performance regression detection

### ⚖️ [`examples/comparison_examples.py`](examples/comparison_examples.py)
Advanced comparison features showcase:
- Multi-scenario benchmark comparisons
- A vs B testing with detailed analysis
- Performance grading and scoring
- Statistical comparison utilities

## 🌐 Real-World Examples

### FastAPI Endpoint Benchmarking

Call your app in-process through `httpx.ASGITransport`. There is no server to start and no network involved. See [`examples/fastapi_examples.py`](examples/fastapi_examples.py) for the complete example.

```python
import asyncio

import httpx
import pytest
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/data")
async def get_data():
    await asyncio.sleep(0.005)  # simulate a database query
    return {"data": "example"}


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_fastapi_endpoint_performance(async_benchmark, client):
    async def make_request():
        response = await client.get("/api/data")
        assert response.status_code == 200
        return response.json()

    result = await async_benchmark(make_request, rounds=10)
    assert result["mean"] < 0.1  # should respond within 100ms
```

> 💡 Create the client **outside** the benchmarked function (as above, via a fixture). Otherwise every measured call also pays for client and connection setup.

### FastMCP Tool Benchmarking

Pass your `FastMCP` server object straight to `fastmcp.Client` and it connects in memory, with no subprocess or stdio. You measure your tool code plus the MCP protocol layer, which is what an agent calling your server experiences. See [`examples/fastmcp_examples.py`](examples/fastmcp_examples.py) for the complete example.

```python
import pytest
from fastmcp import Client, FastMCP

mcp = FastMCP("demo")


@mcp.tool
def add(a: int, b: int) -> int:
    return a + b


@pytest.fixture
async def mcp_client():
    async with Client(mcp) as client:  # in-memory transport
        yield client


@pytest.mark.asyncio
async def test_tool_call_latency(async_benchmark, mcp_client):
    async def call_add():
        result = await mcp_client.call_tool("add", {"a": 2, "b": 3})
        assert result.data == 5

    result = await async_benchmark(call_add, rounds=20, iterations=5)
    assert result["mean"] < 0.05
```

### Quart API Endpoint Comparison

See the complete example in [`examples/quart_api_comparison.py`](examples/quart_api_comparison.py):

```python
import aiohttp
import pytest

from pytest_async_benchmark import a_vs_b_comparison


@pytest.mark.asyncio
async def test_api_v1_vs_v2():
    async with aiohttp.ClientSession("http://localhost:5000") as session:

        async def fetch_v1():
            async with session.get("/api/v1/data") as resp:
                return await resp.json()

        async def fetch_v2():
            async with session.get("/api/v2/data") as resp:
                return await resp.json()

        # Compare API versions (a_vs_b_comparison is async: await it)
        await a_vs_b_comparison(
            "API v1", fetch_v1, "API v2 (Optimized)", fetch_v2, rounds=10, iterations=5
        )
```

### Database Query Benchmarking

```python
@pytest.mark.asyncio
async def test_database_query_performance(async_benchmark):
    async def fetch_user_data(user_id):
        async with database.connection() as conn:
            return await conn.fetch_one("SELECT * FROM users WHERE id = ?", user_id)

    result = await async_benchmark(fetch_user_data, 123, rounds=5)
    assert result["mean"] < 0.05  # Should complete within 50ms
    assert result["p95"] < 0.1  # 95% of queries under 100ms
```

## 🎯 Using Markers

```python
@pytest.mark.async_benchmark
@pytest.mark.asyncio
async def test_performance(async_benchmark):
    # Your benchmark test
    result = await async_benchmark(my_async_function)
    assert result is not None
```

## 📋 API Reference

### `async_benchmark(func, *args, rounds=None, iterations=None, warmup_rounds=1, max_time=None, leak_check=None, **kwargs)`

**Parameters:**
- `func`: The async function to benchmark
- `*args`: Positional arguments to pass to the function
- `rounds`: Number of measurement rounds (default: calibrated, see [Comprehensive Statistics](#-comprehensive-statistics))
- `iterations`: Number of calls per round (default: 1)
- `warmup_rounds`: Number of warmup rounds before measurement (default: 1)
- `max_time`: Time budget in seconds for calibrating rounds (default: 1.0)
- `leak_check`: `True`/`"fail"` or `"warn"` to detect leaked asyncio tasks (default: off)
- `**kwargs`: Keyword arguments to pass to the function

**Returns:** a dictionary of statistics (see [Comprehensive Statistics](#-comprehensive-statistics)).

### `async_benchmark.pedantic(func, *args, setup=None, teardown=None, rounds=None, iterations=None, warmup_rounds=None, max_time=None, leak_check=None, **kwargs)`

Like `async_benchmark(...)`, but runs `setup` and `teardown` around every call without timing them. See [Pedantic Mode](#-pedantic-mode-setup--teardown-excluded-from-timing).

### `async_benchmark.concurrent(func, *args, concurrency=10, total=100, timeout=None, warmup=None, leak_check=None, **kwargs)`

Runs `total` calls with `concurrency` in flight at once. See [Concurrency Benchmarking](#-concurrency-benchmarking).

### Marker

`@pytest.mark.async_benchmark(...)` accepts `rounds`, `iterations`, `warmup_rounds`, `max_time`, `leak_check`, `concurrency`, `total` and `timeout`. Arguments passed directly to the call take precedence.

### Comparison Functions

- `quick_compare(func_a, func_b, **kwargs)`: Quick comparison returning winner and results
- `a_vs_b_comparison(name_a, func_a, name_b, func_b, **kwargs)`: Detailed comparison with terminal output
- `BenchmarkComparator`: Class for multi-scenario benchmarking and analysis

## 📋 Requirements

- Python ≥ 3.10
- pytest ≥ 8.3.5
- pytest-asyncio ≥ 0.23.0 for `await`-style tests (optional: `pip install "pytest-async-benchmark[asyncio]"`)

Note: Rich (for beautiful terminal output) is automatically installed as a dependency.

## 🚀 Development

```bash
# Clone the repository
git clone https://github.com/yourusername/pytest-async-benchmark.git
cd pytest-async-benchmark

# Install dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Run examples
uv run pytest examples/pytest_examples.py -v

# Concurrency examples (pool starvation, locks, blocking calls)
uv run pytest examples/concurrency_examples.py -v -s

# FastAPI and FastMCP examples
uv run pytest examples/fastapi_examples.py examples/fastmcp_examples.py -v

# Test real-world Quart API comparison
uv run python examples/quart_api_comparison.py

# See advanced comparison features
uv run python examples/comparison_examples.py
```

### 🛠️ Code Quality and Formatting

This project uses [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting:

```bash
# Check code for linting issues
uv run ruff check .

# Fix auto-fixable linting issues
uv run ruff check . --fix

# Check code formatting
uv run ruff format --check .

# Format code automatically
uv run ruff format .

# Run both linting and formatting in one go
uv run ruff check . --fix && uv run ruff format .

# Run all quality checks at once (linting, formatting, and tests)
uv run python scripts/quality-check.py
```

### 📋 Release Readiness Check

Before creating a release, verify everything is ready:

```bash
# Run comprehensive release check
uv run python scripts/release-check.py

# This checks:
# ✅ Git repository status
# ✅ Version consistency
# ✅ Code formatting and linting
# ✅ Test suite passes
# ✅ Package builds successfully
# ✅ All required files exist
```

### 🚀 Quick Quality Check

Run all quality checks at once:

```bash
# Run linting, formatting, tests, and release checks
python scripts/quality-check.py

# This will:
# 🔧 Fix linting issues automatically
# 🎨 Format code with Ruff
# 🧪 Run the full test suite
# 📋 Check release readiness
```

## 🚀 Automated Releases

This project uses GitHub Actions for automated testing and publishing to PyPI:

- **Continuous Integration**: Tests run on every push for Python 3.10-3.14
- **Test Publishing**: Automatic uploads to TestPyPI for testing releases
- **Production Releases**: Secure publishing to PyPI using trusted publishing
- **Release Validation**: Comprehensive checks ensure package quality

### Creating a Release

1. Update version in `pyproject.toml` and `src/pytest_async_benchmark/__init__.py`
2. Run `uv run python scripts/release-check.py` to verify readiness
3. Create a git tag: `git tag v1.0.0 && git push origin v1.0.0`
4. Create a GitHub release to trigger automated PyPI publishing

See [RELEASE_GUIDE.md](RELEASE_GUIDE.md) for detailed release instructions.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

*Built with ❤️ for the async Python community*
