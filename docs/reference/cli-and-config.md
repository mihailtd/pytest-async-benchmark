---
title: CLI Options & Configuration
description: Complete reference for pytest-async-benchmark command line flags and pytest configuration settings.
---

# CLI Options & Configuration

`pytest-async-benchmark` adds specialized command-line flags and configuration settings to pytest for managing performance runs, baseline comparisons, and task leak detection.

## Command-Line Options

### Baseline & Regression Options

| Flag | Argument | Description |
|---|---|---|
| `--async-bench-autosave` | None | Automatically saves the current test run to `.async_benchmarks/` with an incremental ID (e.g. `0001_...json`). |
| `--async-bench-save` | `NAME` | Saves the run with an explicit custom name under `.async_benchmarks/`. |
| `--async-bench-compare` | `[NAME]` *(optional)* | Compares current results against a baseline. If no name is specified, compares against the most recent saved run. |
| `--async-bench-compare-fail` | `METRIC:PCT` | Fails the pytest session if a regression exceeds the percentage threshold and is statistically significant (e.g. `median:10%` or `mean:15%`). |
| `--async-bench-json` | `PATH` | Exports complete machine-readable benchmark results, git commit information, and per-call timing samples to a JSON file. |

### Calibration & Runtime Options

| Flag | Argument | Description |
|---|---|---|
| `--async-bench-max-time` | `SECONDS` | Override the default auto-calibration time budget per benchmark (default: `1.0`). Passing `0` disables calibration and runs default fixed rounds. |
| `--async-bench-leak-check` | `[MODE]` | Enable task leak checking across all benchmarks. Valid values: `true` (default if flag passed without value), `warn`, or `false`. |
| `--async-bench-sort` | `COLUMN` | Sort terminal output by column: `name`, `mean`, `min`, `max`, `median`, `p95`, `ops`. |

## Configuration File Settings

You can configure persistent defaults in `pyproject.toml` under `[tool.pytest.ini_options]` or in `pytest.ini`.

### In `pyproject.toml`

```toml
[tool.pytest.ini_options]
# Time budget in seconds for auto-calibration
async_bench_max_time = "1.5"

# Global task leak detection ("true", "warn", or "false")
async_bench_leak_check = "true"
```

### In `pytest.ini`

```ini
[pytest]
async_bench_max_time = 1.5
async_bench_leak_check = true
```

## Environment Variables

| Variable | Description |
|---|---|
| `SITE_BASE` | Base path for documentation builds (e.g. `/pytest-async-benchmark/`). |
| `SITE_URL` | Canonical URL for documentation sitemap and OpenGraph tags. |
| `GOOGLE_SITE_VERIFICATION` | Optional Google Search Console HTML verification token. |
