import subprocess
import time
import re
import requests  # pip install requests
from rich.console import Console
from rich.table import Table
import sys
import os

# --- Configuration ------------------------------------------------------
FLASK_SERVER_URL = "http://127.0.0.1:3000/"
FASTAPI_SERVER_URL = "http://127.0.0.1:8000/"
BENCHMARK_SCRIPT_PATH = "benchmark/run_benchmark.py"
NUM_REQUESTS_EXPECTED = 100
PYTHON_EXE = sys.executable

# ------------------------------------------------------------------------
console = Console()

# -------------------------- helpers -------------------------------------
def start_server(command_args, health_check_url, server_name, cwd=None):
    """Start server and wait until a 200 health check is returned."""
    console.print(f"[yellow]Starting {server_name} server…[/yellow]")

    # --- STREAM HANDLING: inherit console so the child can always write
    popen_kwargs = dict(cwd=cwd, text=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)

    # run either as  "python -m uvicorn ..."  or plain exe
    if "uvicorn" in command_args[0] and not command_args[0].endswith(".exe"):
        process = subprocess.Popen([PYTHON_EXE, "-m"] + command_args, **popen_kwargs)
    else:
        process = subprocess.Popen(command_args, **popen_kwargs)

    max_wait = 30
    start_t = time.time()
    while time.time() - start_t < max_wait:
        try:
            if requests.get(health_check_url, timeout=3).status_code == 200:
                console.print(f"[green]{server_name} ready.[/green]")
                return process
        except requests.RequestException:
            time.sleep(0.3)
    console.print(f"[red]{server_name} failed to start within {max_wait}s.[/red]")
    process.terminate()
    return None

def stop_server(proc, name):
    if not proc:
        return
    console.print(f"[yellow]Stopping {name}…[/yellow]")
    proc.terminate()
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()
    console.print(f"[green]{name} stopped.[/green]")

def run_benchmark_script(framework_arg):
    console.print(f"Running benchmark for [bold]{framework_arg}[/bold]…")
    cmd = [PYTHON_EXE, BENCHMARK_SCRIPT_PATH, framework_arg]
    result = subprocess.run(cmd, text=True, capture_output=True, timeout=600)
    if result.returncode:
        console.print(f"[red]{framework_arg} benchmark failed.[/red]")
        console.print(result.stderr)
        return None
    last_line = result.stdout.strip().splitlines()[-1]
    return last_line

def parse_benchmark(line):
    m = re.search(r"(\d+)/(\d+) successful requests in ([\d.]+) seconds", line)
    if not m:
        return None
    succ, total, tsec = map(float, m.groups())
    return {"successful": f"{int(succ)}/{int(total)}", "total_time": tsec}

def display_table(rows):
    tbl = Table(title="Benchmark Summary", show_lines=True, header_style="bold magenta")
    tbl.add_column("Framework", style="cyan")
    tbl.add_column("Server", style="white")
    tbl.add_column("Delay", style="green")
    tbl.add_column("#Reqs", justify="right")
    tbl.add_column("Success", justify="right")
    tbl.add_column("Total s", justify="right", style="yellow")
    tbl.add_column("Avg s/req", justify="right", style="blue")
    for r in rows:
        avg = r["total_time"] / NUM_REQUESTS_EXPECTED
        tbl.add_row(r["framework"], r["config"], r["delay"],
                    str(NUM_REQUESTS_EXPECTED), r["successful"],
                    f"{r['total_time']:.2f}", f"{avg:.3f}")
    console.print(tbl)

# --------------------------- scenarios ----------------------------------
SCENARIOS = [
    {
        "name": "FastAPI",
        "config": "Uvicorn, async",
        "delay": "0.3 s asyncio.sleep",
        "cmd": ["uvicorn", "app_fastapi.app:app", "--host", "0.0.0.0",
                "--port", "8000", "--log-level", "warning"],
        "url": FASTAPI_SERVER_URL,
        "bench_arg": "fastapi",
    },
    {
        "name": "Flask",
        "config": "Single-threaded",
        "delay": "0.3 s time.sleep",
        "cmd": [PYTHON_EXE, "app_flask/flask_application.py"],
        "url": FLASK_SERVER_URL,
        "bench_arg": "flask",
    }
]

# ----------------------------- main -------------------------------------
if __name__ == "__main__":
    console.print("[bold underline]Automated Web Framework Benchmark[/bold underline]\n")
    results = []
    root = os.getcwd()

    for i, sc in enumerate(SCENARIOS, 1):
        console.rule(f"[cyan]Scenario {i}/{len(SCENARIOS)} – {sc['name']}[/cyan]")
        srv = start_server(sc["cmd"], sc["url"], sc["name"], cwd=root)
        if not srv:
            continue
        try:
            if sc["name"].lower() == "flask":
                time.sleep(2)  # tiny grace period
            line = run_benchmark_script(sc["bench_arg"])
            parsed = parse_benchmark(line) if line else None
            if parsed:
                results.append({"framework": sc["name"], "config": sc["config"],
                                "delay": sc["delay"], **parsed})
        finally:
            stop_server(srv, sc["name"])
        console.print()

    if results:
        display_table(results)
    console.print("\n[bold]Benchmark run finished.[/bold]") 