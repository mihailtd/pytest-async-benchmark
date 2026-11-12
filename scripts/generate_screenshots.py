#!/usr/bin/env python3
"""Generate high-resolution SVG and PNG terminal screenshots for pytest-async-benchmark."""

import subprocess
from pathlib import Path

from rich.console import Console
from rich.table import Table


def export_terminal(
    console: Console,
    base_name: str,
    out_dir: Path,
    title: str = "pytest-async-benchmark",
):
    """Export Console buffer to both SVG and high-resolution PNG."""
    svg_path = out_dir / f"{base_name}.svg"
    png_path = out_dir / f"{base_name}.png"

    # Export rich SVG with terminal window styling
    console.save_svg(str(svg_path), title=title)

    # Convert to crisp high-DPI PNG via rsvg-convert (2x scale for Retina displays)
    subprocess.run(
        ["rsvg-convert", "-z", "1.5", str(svg_path), "-o", str(png_path)],
        check=True,
    )
    print(f"Generated {svg_path.name} and {png_path.name}")


def generate_benchmark_screenshot(out_dir: Path):
    """Generate screenshot of standard benchmark results."""
    console = Console(record=True, width=76, color_system="truecolor")

    table = Table(
        title="🚀 Async Benchmark Results: test_fetch_user_profile",
        title_style="bold cyan",
        border_style="bright_blue",
        header_style="bold magenta",
    )
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green", justify="right")

    table.add_row("Min", "1.120ms")
    table.add_row("Median", "1.185ms")
    table.add_row("Mean", "1.204ms")
    table.add_row("p95", "1.340ms")
    table.add_row("p99", "1.580ms")
    table.add_row("Max", "1.890ms")
    table.add_row("Std Dev", "82.415μs")
    table.add_row("Ops/sec", "830.6")
    table.add_row("Samples", "831")
    table.add_row("Rounds", "831 [dim](calibrated)[/dim]")
    table.add_row("Iterations", "1")

    console.print()
    console.print(table)
    console.print("[bold green]✅ Benchmark completed successfully![/bold green]\n")

    export_terminal(
        console,
        "benchmark-results",
        out_dir,
        title="test_fetch_user_profile - Benchmark",
    )


def generate_concurrency_screenshot(out_dir: Path):
    """Generate screenshot of concurrent benchmark results."""
    console = Console(record=True, width=76, color_system="truecolor")

    table = Table(
        title="🚦 Async Concurrency Results: test_api_under_load",
        title_style="bold yellow",
        border_style="yellow",
        header_style="bold cyan",
    )
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green", justify="right")

    table.add_row("Concurrency", "25 [dim](tasks in flight)[/dim]")
    table.add_row("Completed", "500 / 500")
    table.add_row("Errors", "0")
    table.add_row("Timeouts", "0")
    table.add_row("Throughput", "[bold green]1,842.5 calls/s[/bold green]")
    table.add_row("Wall time", "271.370ms")
    table.add_row("Latency p50", "12.840ms")
    table.add_row("Latency p95", "16.420ms")
    table.add_row("Latency p99", "19.180ms")
    table.add_row("Latency max", "22.810ms")
    table.add_row("Loop lag p99", "420.150μs")
    table.add_row("Loop lag max", "852.340μs")

    console.print()
    console.print(table)
    console.print(
        "[dim]In-process measurement: throughput reflects this event loop, not production capacity.[/dim]\n"
    )

    export_terminal(
        console,
        "concurrency-results",
        out_dir,
        title="test_api_under_load - Concurrency",
    )


def generate_comparison_screenshot(out_dir: Path):
    """Generate screenshot of A vs B comparison results."""
    console = Console(record=True, width=82, color_system="truecolor")

    table = Table(
        title="🚀 Async Benchmark Comparison",
        title_style="bold cyan",
        border_style="bright_blue",
        header_style="bold magenta",
    )
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Sequential", style="yellow", justify="right")
    table.add_column("Batched Async", style="green", justify="right")
    table.add_column("Difference", style="bold yellow", justify="right")

    table.add_row("Min", "15.420ms", "4.820ms", "-68.7%")
    table.add_row("Max", "24.180ms", "7.350ms", "-69.6%")
    table.add_row(
        "Mean", "16.240ms", "5.120ms", "[bold green]3.17x faster[/bold green]"
    )
    table.add_row("Median", "15.910ms", "4.980ms", "-68.7%")
    table.add_row("p95", "18.350ms", "5.840ms", "-68.2%")
    table.add_row("p99", "21.420ms", "6.710ms", "-68.7%")
    table.add_row("Stddev", "1.450ms", "0.480ms", "-66.9%")
    table.add_row("Rounds", "10", "10", "")
    table.add_row("Iterations", "5", "5", "")

    console.print()
    console.print(table)
    console.print(
        "🏆 [bold green]Batched Async[/bold green] is [bold green]3.17x faster[/bold green] than [yellow]Sequential[/yellow]"
    )
    console.print("[bold green]✅ Comparison completed successfully![/bold green]\n")

    export_terminal(console, "comparison-results", out_dir, title="A vs B Comparison")


def generate_regression_screenshot(out_dir: Path):
    """Generate screenshot of CI baseline regression table."""
    console = Console(record=True, width=86, color_system="truecolor")

    table = Table(
        title="📈 Comparison with baseline: 0001_main_baseline",
        title_style="bold cyan",
        border_style="bright_blue",
        header_style="bold magenta",
    )
    table.add_column("Benchmark", style="cyan", no_wrap=True)
    table.add_column("Baseline", style="dim", justify="right")
    table.add_column("Current", justify="right")
    table.add_column("Delta (Median)", justify="right")
    table.add_column("Significance (p)", justify="right")
    table.add_column("Status", justify="center")

    table.add_row(
        "test_fast_endpoint",
        "1.185ms",
        "1.042ms",
        "[green]-12.1%[/green]",
        "p = 0.001",
        "[bold green]🚀 FASTER[/bold green]",
    )
    table.add_row(
        "test_cache_lookup",
        "0.245ms",
        "0.248ms",
        "[dim]+1.2%[/dim]",
        "p = 0.412",
        "[blue]✓ OK (noise)[/blue]",
    )
    table.add_row(
        "test_batch_serialization",
        "5.120ms",
        "4.890ms",
        "[green]-4.5%[/green]",
        "p = 0.038",
        "[bold green]🚀 FASTER[/bold green]",
    )
    table.add_row(
        "test_heavy_transform",
        "12.450ms",
        "14.820ms",
        "[red]+19.0%[/red]",
        "p = 0.0002",
        "[bold red]⚠️ SLOWER[/bold red]",
    )

    console.print()
    console.print(table)
    console.print(
        "[yellow]Comparison check: 1 regression detected above threshold (median:10%)[/yellow]\n"
    )

    export_terminal(
        console, "regression-results", out_dir, title="Baseline Regression Check"
    )


def generate_hero_composite(out_dir: Path, root_dir: Path):
    """Generate high-impact composite terminal for the README hero."""
    console = Console(record=True, width=86, color_system="truecolor")

    console.print()
    console.print(
        "[bold green]$[/bold green] [bold white]pytest tests/test_performance.py --async-bench-compare[/bold white]"
    )
    console.print(
        "[dim]platform linux -- Python 3.12.3, pytest-8.3.5, async-benchmark-0.4.1[/dim]\n"
    )

    # Bench table
    table1 = Table(
        title="🚀 Async Benchmark Results: test_user_api",
        title_style="bold cyan",
        border_style="bright_blue",
        header_style="bold magenta",
    )
    table1.add_column("Metric", style="cyan")
    table1.add_column("Value", style="green", justify="right")
    table1.add_row("Min", "1.042ms")
    table1.add_row("Median", "1.120ms")
    table1.add_row("Mean", "1.145ms")
    table1.add_row("p95", "1.290ms")
    table1.add_row("p99", "1.450ms")
    table1.add_row("Max", "1.720ms")
    table1.add_row("Ops/sec", "873.4")
    table1.add_row("Samples", "874 [dim](calibrated 1.0s)[/dim]")
    console.print(table1)

    # Concurrency table
    table2 = Table(
        title="🚦 Async Concurrency Results: test_user_api_load",
        title_style="bold yellow",
        border_style="yellow",
        header_style="bold cyan",
    )
    table2.add_column("Metric", style="cyan")
    table2.add_column("Value", style="green", justify="right")
    table2.add_row("Concurrency", "20 in flight")
    table2.add_row("Throughput", "[bold green]1,920.4 calls/s[/bold green]")
    table2.add_row("Latency p95", "14.2ms")
    table2.add_row("Loop lag p99", "310.5μs")
    table2.add_row("Task leaks", "[bold green]0 detected[/bold green]")
    console.print(table2)

    console.print(
        "[bold green]==================== 2 benchmarks passed in 2.14s ====================[/bold green]\n"
    )

    export_terminal(console, "terminal-hero", out_dir, title="pytest-async-benchmark")

    # Also copy as root screenshot.png
    hero_png = out_dir / "terminal-hero.png"
    root_png = root_dir / "screenshot.png"
    root_png.write_bytes(hero_png.read_bytes())
    print(f"Updated root {root_png.name}")


def main():
    root_dir = Path(__file__).resolve().parent.parent
    screenshots_dir = root_dir / "docs" / "public" / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    generate_benchmark_screenshot(screenshots_dir)
    generate_concurrency_screenshot(screenshots_dir)
    generate_comparison_screenshot(screenshots_dir)
    generate_regression_screenshot(screenshots_dir)
    generate_hero_composite(screenshots_dir, root_dir)
    print("All screenshots generated successfully!")


if __name__ == "__main__":
    main()
