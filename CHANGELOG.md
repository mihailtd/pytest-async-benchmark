# Changelog

All notable changes to pytest-async-benchmark will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### 🚀 Major Features
- **Concurrency Benchmarking**: `async_benchmark.concurrent(func, concurrency=..., total=..., timeout=...)` runs calls with N in flight at once and reports throughput, latency percentiles under load, errors, timeouts and event loop lag
- **Regression Detection**: `--async-bench-autosave` saves numbered runs; `--async-bench-compare` compares against a saved run; `--async-bench-compare-fail=median:10%` fails the session only when a slowdown exceeds the threshold *and* is statistically significant (one-sided Mann-Whitney U test, pure Python)
- **JSON Export**: `--async-bench-json=PATH` writes every result, including per-call samples, machine info and git commit info
- **Task Leak Detection**: `leak_check=True` / `"warn"` (or `--async-bench-leak-check`) fails or warns when a benchmark leaves asyncio tasks running

### 🔧 Improvements
- **Per-call timing**: every call is timed individually; statistics are computed from all calls instead of from per-round averages
- **Real percentiles**: results now include `p50`, `p75`, `p90`, `p95`, `p99`, plus `ops`, `count`, `total_time`, `samples` and `mode`
- **Auto calibration**: without `rounds`, measurement runs for a time budget (`max_time`, default 1.0s, at least 5 rounds) instead of a fixed 5 calls; configurable per call, via the marker, or with `--async-bench-max-time`
- Comparison tables now show p95 and p99
- New examples: `examples/concurrency_examples.py`, plus concurrency tests in the FastAPI and FastMCP examples

### ⚠️ Behavior changes
- When `iterations > 1`, `min`, `max`, `median` and `stddev` now describe individual calls rather than round averages (`mean` is unchanged). `raw_times` keeps its previous meaning (one mean per round); per-call durations are in the new `samples` key
- Benchmarks without an explicit `rounds` now run for about 1 second each instead of 5 calls. Pass `rounds=` or `--async-bench-max-time` to change this

### 📝 Documentation
- Removed `grade` and `grade_score` from the documented result keys; they were never returned

## [0.3.0] - 2026-11-10

### 🚀 Major Features
- **Pedantic Mode**: Added `async_benchmark.pedantic()` (and `AsyncBenchmarkRunner.run_pedantic()`) allowing per-iteration setup and teardown while excluding their duration from benchmark measurements (addresses issue #1)
- **Flexible Hook Support**: Setup and teardown functions can be synchronous or asynchronous coroutines
- **Argument Passing**: Return values from `setup` (individual values or unpacked tuples) are passed as arguments to both the target function and `teardown`
- **Dual Interface Pedantic Support**: Works seamlessly with `await async_benchmark.pedantic(...)` or synchronous `async_benchmark.pedantic(...)`

### 🔧 Improvements & Upgrades
- **Dependency Upgrades**: Upgraded dependencies to latest versions (pytest 9.x, rich 15.x, ruff 0.17.x, aiohttp 3.14.x, quart 0.23.x, pre-commit 4.7.x)
- **Modern Python Compatibility**: Fixed `asyncio.iscoroutinefunction` deprecations slated for removal in Python 3.16 by switching to `inspect.iscoroutinefunction` across all modules
- **Pytest-Asyncio v1.x Compatibility**: Added explicit `asyncio_mode = "auto"` and `asyncio_default_fixture_loop_scope = "function"` configuration in `pyproject.toml`
- **CI Matrix**: Extended GitHub Actions CI matrix to test on Python 3.13

## [0.2.0] - 2025-05-28

### 🚀 Major Features
- **Backwards Compatibility**: Automatic interface detection supporting both sync and async usage patterns
- **pytest-asyncio Integration**: Full compatibility with pytest-asyncio plugin when available
- **Dual Interface Support**: Works with `await async_benchmark(...)` (with pytest-asyncio) or `result = async_benchmark(...)` (without)
- **Smart Detection**: Automatically detects pytest-asyncio availability and provides appropriate interface

### ✨ Added
- Automatic pytest-asyncio detection and interface switching
- Legacy sync interface support for backwards compatibility with v0.1.x
- Optional dependency configuration for pytest-asyncio
- Comprehensive backwards compatibility test suite
- `_SyncResultWrapper` class for seamless sync interface
- Enhanced documentation covering both usage patterns

### 🔧 Changed
- **NON-BREAKING**: pytest-asyncio moved from required to optional dependency
- `AsyncBenchmarkFixture.__call__` now returns different types based on environment
- Enhanced fixture to support both sync and async interfaces automatically
- Updated examples to show both usage patterns
- README updated with backwards compatibility documentation

### 🛠️ Fixed
- RuntimeError issues when pytest-asyncio not available
- Event loop management conflicts in different environments
- Compatibility issues with projects not using pytest-asyncio

### 📚 Documentation
- Added pytest-asyncio compatibility section to README
- Updated all code examples to demonstrate async/await usage
- Created dedicated pytest-asyncio showcase example
- Enhanced Quick Start guide with modern async patterns

### 🧪 Testing
- All 40 tests passing with pytest-asyncio integration
- Examples thoroughly tested and validated
- Comprehensive test coverage maintained

---

## [0.1.1] - 2025-05-27

### Initial Features
- Core async benchmarking functionality
- Rich console output with beautiful formatting
- Statistical analysis and comparison tools
- Multiple examples and comprehensive testing

### Core Components
- `AsyncBenchmarkFixture` for pytest integration
- `AsyncBenchmarkRunner` for timing execution
- `BenchmarkComparator` for performance analysis
- Rich-based display formatting

### Examples
- Basic pytest examples
- Quart API comparison
- Comparison analysis tools
- Statistical benchmarking patterns
