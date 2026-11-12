"""End-to-end tests for JSON output, autosave and --async-bench-compare."""

import json

import pytest

from pytest_async_benchmark import storage

# A test module run inside pytester. The sleep duration comes from an
# environment variable so two runs can differ in speed.
BENCH_MODULE = """
import asyncio
import os

DELAY = float(os.environ.get("BENCH_DELAY", "0.001"))


async def work():
    await asyncio.sleep(DELAY)


def test_bench(async_benchmark):
    async_benchmark(work, rounds=15)


def test_twice(async_benchmark):
    async_benchmark(work, rounds=5)
    async_benchmark(work, rounds=5)
"""


@pytest.fixture(autouse=True)
def pytest_ini(pytester):
    pytester.makeini("[pytest]\nasyncio_default_fixture_loop_scope = function\n")


@pytest.fixture
def bench(pytester):
    pytester.makepyfile(test_bench=BENCH_MODULE)
    return pytester


def saved_runs(pytester):
    return sorted((pytester.path / ".async_benchmarks").glob("*/*.json"))


def test_json_output(bench):
    result = bench.runpytest("--async-bench-json=out/results.json")
    result.assert_outcomes(passed=2)

    report = json.loads((bench.path / "out" / "results.json").read_text())
    assert set(report) >= {"version", "datetime", "machine_info", "benchmarks"}
    assert "node" not in report["machine_info"]  # no hostname

    names = [b["fullname"] for b in report["benchmarks"]]
    assert names == [
        "test_bench.py::test_bench",
        "test_bench.py::test_twice",
        "test_bench.py::test_twice#2",
    ]
    first = report["benchmarks"][0]
    assert len(first["samples"]) == 15
    assert first["samples_truncated"] is False
    assert {"min", "median", "p95", "p99", "ops"} <= set(first["stats"])
    assert "samples" not in first["stats"]
    result.stdout.fnmatch_lines(["*Saved benchmark JSON to*results.json"])


def test_nothing_written_without_options(bench):
    bench.runpytest().assert_outcomes(passed=2)
    assert saved_runs(bench) == []


def test_autosave_numbers_runs(bench):
    bench.runpytest("--async-bench-autosave").assert_outcomes(passed=2)
    bench.runpytest("--async-bench-autosave").assert_outcomes(passed=2)

    runs = saved_runs(bench)
    assert [run.name[:5] for run in runs] == ["0001_", "0002_"]
    assert runs[0].parent.name == storage.machine_id()


def test_custom_storage_dir(bench):
    bench.runpytest(
        "--async-bench-autosave", "--async-bench-storage=perf"
    ).assert_outcomes(passed=2)
    assert list((bench.path / "perf").glob("*/0001_*.json"))


def test_compare_without_saved_runs_warns(bench):
    result = bench.runpytest("--async-bench-compare")
    assert result.ret == 0
    result.stdout.fnmatch_lines(["*Can't compare*No saved benchmark runs*"])


def test_compare_same_speed_passes(bench, monkeypatch):
    monkeypatch.setenv("BENCH_DELAY", "0.002")
    bench.runpytest("--async-bench-autosave").assert_outcomes(passed=2)

    result = bench.runpytest(
        "--async-bench-compare", "--async-bench-compare-fail=median:300%"
    )
    assert result.ret == 0
    result.stdout.fnmatch_lines(["*Comparison with baseline*", "*Compared against*"])


def test_compare_detects_regression(bench, monkeypatch):
    monkeypatch.setenv("BENCH_DELAY", "0.001")
    bench.runpytest("--async-bench-autosave").assert_outcomes(passed=2)

    monkeypatch.setenv("BENCH_DELAY", "0.02")
    result = bench.runpytest(
        "--async-bench-compare", "--async-bench-compare-fail=median:50%"
    )
    result.assert_outcomes(passed=2)  # the tests themselves pass...
    assert result.ret == pytest.ExitCode.TESTS_FAILED  # ...but the session fails
    result.stdout.fnmatch_lines(["*regression (median:50%)*", "*regressed*"])


def test_compare_by_run_number_and_path(bench):
    bench.runpytest("--async-bench-autosave").assert_outcomes(passed=2)
    bench.runpytest("--async-bench-autosave").assert_outcomes(passed=2)
    first = saved_runs(bench)[0]

    by_number = bench.runpytest("--async-bench-compare=1")
    by_number.stdout.fnmatch_lines([f"*Compared against*{first.name}"])

    by_path = bench.runpytest(f"--async-bench-compare={first}")
    by_path.stdout.fnmatch_lines([f"*Compared against*{first.name}"])


def test_compare_does_not_compare_with_itself(bench):
    """With compare + autosave together, the baseline is the previous run."""
    bench.runpytest("--async-bench-autosave").assert_outcomes(passed=2)
    result = bench.runpytest("--async-bench-compare", "--async-bench-autosave")
    result.stdout.fnmatch_lines(["*Compared against*0001_*"])
    assert len(saved_runs(bench)) == 2


def test_compare_fail_requires_compare(bench):
    result = bench.runpytest("--async-bench-compare-fail=median:10%")
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.stderr.fnmatch_lines(["*requires --async-bench-compare*"])


def test_invalid_compare_fail_expression(bench):
    result = bench.runpytest(
        "--async-bench-compare", "--async-bench-compare-fail=fastest:10%"
    )
    assert result.ret == pytest.ExitCode.USAGE_ERROR


def test_cli_max_time_calibrates(pytester):
    pytester.makepyfile(
        """
        import asyncio

        async def work():
            await asyncio.sleep(0.001)

        def test_calibrated(async_benchmark):
            result = async_benchmark(work)
            assert result["calibrated"]
            assert result["rounds"] == 5
        """
    )
    pytester.runpytest("--async-bench-max-time=0").assert_outcomes(passed=1)


def test_cli_leak_check(pytester):
    pytester.makepyfile(
        """
        import asyncio

        async def leaky():
            asyncio.ensure_future(asyncio.sleep(0.5))

        def test_leaky(async_benchmark):
            async_benchmark(leaky, rounds=1)
        """
    )
    result = pytester.runpytest("--async-bench-leak-check=fail")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*TaskLeakError*"])


class TestStorageHelpers:
    def test_downsample_preserves_range(self):
        samples = [float(i) for i in range(25_000)]
        reduced = storage.downsample(samples, limit=1_000)
        assert len(reduced) == 1_000
        assert reduced[0] == 0.0
        assert reduced[-1] == 24_999.0
        assert reduced == sorted(reduced)

    def test_downsample_small_input_is_sorted_copy(self):
        assert storage.downsample([3.0, 1.0, 2.0]) == [1.0, 2.0, 3.0]

    def test_infinite_values_become_null(self, tmp_path):
        entry = {
            "name": "t",
            "fullname": "t",
            "result": {"mean": 0.0, "ops": float("inf"), "samples": [0.0]},
        }
        report = storage.build_report([entry], "test")
        path = storage.write_report(report, tmp_path / "r.json")
        loaded = storage.load_report(path)
        assert loaded["benchmarks"][0]["stats"]["ops"] is None

    def test_find_baseline_errors(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            storage.find_baseline(tmp_path)
        with pytest.raises(FileNotFoundError):
            storage.find_baseline(tmp_path, "missing.json")


def test_commit_info_comes_from_project_root(bench, monkeypatch, tmp_path_factory):
    """Git info must describe the project under test, not the current directory."""
    bench.run("git", "init", "-q")
    bench.run(
        "git",
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@t",
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "init",
    )
    head = bench.run("git", "rev-parse", "HEAD").outlines[0]

    # Run pytest from a directory that is not the project root (nor a git repo).
    monkeypatch.chdir(tmp_path_factory.mktemp("elsewhere"))
    out = bench.path / "r.json"
    bench.runpytest(
        str(bench.path), f"--rootdir={bench.path}", f"--async-bench-json={out}"
    ).assert_outcomes(passed=2)
    report = json.loads(out.read_text())
    assert report["commit_info"]["id"] == head


CALIBRATION_CHECK = """
import asyncio

async def work():
    await asyncio.sleep(0.001)

def test_calibrated(async_benchmark):
    result = async_benchmark(work)
    assert result["rounds"] == {rounds}
"""


def test_ini_max_time(pytester):
    pytester.makeini(
        "[pytest]\n"
        "asyncio_default_fixture_loop_scope = function\n"
        "async_bench_max_time = 0\n"
    )
    pytester.makepyfile(CALIBRATION_CHECK.format(rounds=5))
    pytester.runpytest().assert_outcomes(passed=1)


def test_cli_max_time_overrides_ini(pytester):
    pytester.makeini(
        "[pytest]\n"
        "asyncio_default_fixture_loop_scope = function\n"
        "async_bench_max_time = 0\n"
    )
    pytester.makepyfile(
        CALIBRATION_CHECK.replace(
            'assert result["rounds"] == {rounds}', 'assert result["rounds"] > 5'
        )
    )
    pytester.runpytest("--async-bench-max-time=0.2").assert_outcomes(passed=1)


def test_pyproject_settings(pytester):
    pytester.makepyprojecttoml(
        """
        [tool.pytest.ini_options]
        asyncio_default_fixture_loop_scope = "function"
        async_bench_max_time = "0"
        async_bench_leak_check = "fail"
        """
    )
    pytester.makepyfile(
        """
        import asyncio

        async def leaky():
            asyncio.ensure_future(asyncio.sleep(0.5))

        def test_leaky(async_benchmark):
            async_benchmark(leaky)
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*TaskLeakError*"])


@pytest.mark.parametrize(
    ("line", "message"),
    [
        ("async_bench_max_time = soon", "*async_bench_max_time must be*"),
        ("async_bench_max_time = -1", "*async_bench_max_time must be*"),
        ("async_bench_leak_check = maybe", "*async_bench_leak_check must be*"),
    ],
)
def test_invalid_ini_settings(pytester, line, message):
    pytester.makeini(
        f"[pytest]\nasyncio_default_fixture_loop_scope = function\n{line}\n"
    )
    pytester.makepyfile("def test_nothing(): pass")
    result = pytester.runpytest()
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.stderr.fnmatch_lines([message])
