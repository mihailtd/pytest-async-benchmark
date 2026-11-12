---
title: Regression Detection & CI Baselines
description: Track performance across commits, compare against historical baselines, and fail CI on statistically verified regressions.
---

# Regression Detection & CI Baselines

Performance testing in CI often suffers from high false-positive rates due to noisy VM neighbors, variable CPU clock speeds, and thermal throttling.

`pytest-async-benchmark` solves this by combining baseline comparison with **rigorous non-parametric statistical testing**. It only fails your CI pipeline when a slowdown is both **substantive** (exceeds your configured threshold) and **statistically significant** (p < 0.05).

## Saving Runs

To record benchmark runs for comparison, use the `--async-bench-autosave` flag:

```bash
pytest --async-bench-autosave
```

This saves run results to `.async_benchmarks/` with numbered filenames (e.g. `0001_initial.json`, `0002_refactor.json`). Each saved file records:
- Complete distribution metrics for every benchmark.
- All individual raw duration samples.
- Host machine metadata (CPU, architecture, Python version, OS).
- Current Git commit SHA, branch name, and dirty-state flag.

## Comparing Against Saved Baselines

To compare the current test run against the most recent saved baseline:

```bash
pytest --async-bench-compare
```

Or compare against a specific saved baseline by number or name:

```bash
pytest --async-bench-compare=0001
```

Pytest prints a side-by-side terminal comparison table highlighting percentage changes:

![Baseline Regression Check Terminal Output](/screenshots/regression-results.png)

## Failing CI on Regressions

To prevent performance regressions from landing on `main`, configure `--async-bench-compare-fail`:

```bash
# Fail if median latency regresses by more than 10%
pytest --async-bench-compare --async-bench-compare-fail=median:10%

# Fail if mean latency regresses by more than 15%
pytest --async-bench-compare --async-bench-compare-fail=mean:15%
```

### The Mann-Whitney U Test (Zero Flakiness)

A simple percentage threshold like `+10%` will periodically fail in CI due to transient host load.

To eliminate flaky CI failures, `pytest-async-benchmark` runs a one-sided **Mann-Whitney U test** across the per-call timing samples of both runs:

1. **Threshold Check**: Is the current median/mean higher than baseline by at least the specified percentage?
2. **Significance Check**: Are the sample distributions statistically distinct at `p < 0.05`?

If latency increased by 11% but the variance across samples is high ($p \ge 0.05$), the runner recognizes that the difference may be random noise and does **not** fail your build. Only when the regression is confirmed with 95% statistical confidence does pytest exit with a non-zero code.

## Exporting Machine-Readable JSON

Export raw benchmark results for dashboard ingestion or PR comments:

```bash
pytest --async-bench-json=benchmark_results.json
```

The exported JSON file contains structured records for every benchmark, including git commit metadata, hardware specs, and per-call samples.
