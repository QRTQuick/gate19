"""gate19 benchmark — micro-benchmarks."""

from __future__ import annotations

import time
import timeit
from pathlib import Path
import typer
from rich.table import Table
from gate19.cli.app import app
from gate19.utils.console import console, success, info

@app.command("benchmark")
def benchmark_command(
    iterations: int = typer.Option(1000, "--iter", "-n", help="Iterations for benchmarks"),
):
    """Run performance benchmarks. ⏱️"""
    console.print("[bold magenta]⏱️ Gate19 Benchmarks[/]\n")

    results = []

    # Benchmark 1: import time
    def bench_import():
        import importlib
        start = time.perf_counter()
        for _ in range(100):
            importlib.import_module("gate19.utils.console")
        return (time.perf_counter() - start) / 100

    t_import = bench_import()
    results.append(("Import gate19.utils.console", f"{t_import*1000:.3f} ms", "per import"))

    # Benchmark 2: resolver
    def bench_resolver():
        from gate19.resolver.resolver import Resolver
        r = Resolver()
        start = time.perf_counter()
        r.resolve(["requests>=2.0", "rich>=13.0"], parallel=False)
        return time.perf_counter() - start

    try:
        t_resolver = bench_resolver()
        results.append(("Resolver (2 packages, no cache)", f"{t_resolver:.3f} s", "resolve"))
    except Exception as e:
        results.append(("Resolver", f"error: {e}", ""))

    # Benchmark 3: file scaffolding
    def bench_fs():
        from gate19.utils.fs import ensure_dir, write_file
        import tempfile, shutil
        tmp = Path(tempfile.mkdtemp())
        start = time.perf_counter()
        for i in range(100):
            write_file(tmp / f"file_{i}.txt", "hello world")
        elapsed = time.perf_counter() - start
        shutil.rmtree(tmp, ignore_errors=True)
        return elapsed / 100

    t_fs = bench_fs()
    results.append(("Write file", f"{t_fs*1000:.3f} ms", "per write"))

    # Benchmark 4: toml parsing
    def bench_toml():
        from gate19.utils.pyproject import load_pyproject
        import tempfile
        tmp = Path(tempfile.mktemp(suffix=".toml"))
        tmp.write_text('[project]\nname="bench"\nversion="0.1.0"\ndependencies=["requests", "rich"]\n')
        start = time.perf_counter()
        for _ in range(iterations):
            load_pyproject(tmp)
        elapsed = time.perf_counter() - start
        tmp.unlink(missing_ok=True)
        return elapsed / iterations

    t_toml = bench_toml()
    results.append(("Parse pyproject.toml", f"{t_toml*1000:.3f} ms", "per parse"))

    table = Table(title=f"Benchmarks (n={iterations} where applicable)", show_header=True, header_style="bold magenta")
    table.add_column("Benchmark", style="cyan")
    table.add_column("Time", style="green")
    table.add_column("Unit", style="dim")
    for name, t, unit in results:
        table.add_row(name, t, unit)

    console.print(table)
    success(f"\nBenchmarks completed — avg times shown ✓")
    console.print("[dim]Tip: Run with --iter 5000 for more stable numbers[/]")
