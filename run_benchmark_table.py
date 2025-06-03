import subprocess
import time
import re
import requests  # pip install requests
import webbrowser # Added import
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
    popen_kwargs = dict(cwd=cwd, text=True)
                        # stdout=subprocess.DEVNULL,  # Temporarily allow stdout
                        # stderr=subprocess.STDOUT    # Temporarily allow stderr

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
    console.print(f"Running benchmark for [bold]{framework_arg}[/bold] with {NUM_REQUESTS_EXPECTED} requests...")
    cmd = [PYTHON_EXE, BENCHMARK_SCRIPT_PATH, framework_arg, str(NUM_REQUESTS_EXPECTED)]

    if framework_arg.lower() == "flask":
        final_summary_line = None
        requests_done_count = 0
        progress_line_printed = False
        try:
            # Ensure encoding is specified for Popen for consistent text handling
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True, encoding='utf-8')
            
            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    line = line.strip()
                    if not line: 
                        continue

                    if line.startswith("REQ_STATUS:"):
                        requests_done_count += 1
                        # Using carriage return to update the line in place
                        print(f"\rFlask progress: Handled {requests_done_count}/{NUM_REQUESTS_EXPECTED} requests...", end="", flush=True)
                        progress_line_printed = True
                    elif line.startswith("[DIAG-BRB-FLASK]"):
                        if progress_line_printed:
                            # Clear the progress line before printing diagnostic output
                            print("\r" + " " * 80 + "\r", end="", flush=True) 
                        print(line, flush=True) # Print diagnostic line
                        if progress_line_printed:
                            # Reprint the progress line after diagnostic output
                            print(f"\rFlask progress: Handled {requests_done_count}/{NUM_REQUESTS_EXPECTED} requests...", end="", flush=True)
                    elif "Final Flask benchmark summary:" in line:
                        final_summary_line = line
                        if progress_line_printed:
                             # Clear the progress line before finishing
                            print("\r" + " " * 80 + "\r", end="", flush=True)
                        # The summary line itself will be printed by the main logic if needed, or parsed

                process.stdout.close()
            
            # After the loop, if progress was printed, clear it finally
            # This handles cases where the process ends without a final summary line immediately after progress
            if progress_line_printed and not final_summary_line:
                 print("\r" + " " * 80 + "\r", end="", flush=True)

            stderr_output_list = []
            if process.stderr:
                for line in iter(process.stderr.readline, ''):
                    line = line.strip()
                    if line:
                        stderr_output_list.append(line)
                process.stderr.close()

            process.wait(timeout=600) 

            if process.returncode != 0:
                console.print(f"[red]{framework_arg} benchmark script failed with return code {process.returncode}[/red]")
                if stderr_output_list:
                    console.print("[red]STDERR:[/red]")
                    for err_line in stderr_output_list:
                        console.print(f"[red]{err_line}[/red]")
                return None
            
            if final_summary_line:
                return final_summary_line
            else:
                console.print(f"[red]Could not find the final summary line for {framework_arg} in Popen benchmark output.[/red]")
                if stderr_output_list:
                    console.print("[red]STDERR output during Popen execution was:[/red]")
                    for err_line in stderr_output_list:
                        console.print(f"[red]{err_line}[/red]")
                return None

        except subprocess.TimeoutExpired:
            console.print(f"[red]Benchmark for {framework_arg} (Popen path) timed out.[/red]")
            if process.poll() is None: # Check if process is still running
                process.kill()
                process.wait()
            return None
        except Exception as e:
            console.print(f"[red]An unexpected error occurred while running Popen benchmark for {framework_arg}: {e}[/red]")
            return None
            
    else:  # For FastAPI or any other framework not needing live progress
        try:
            result = subprocess.run(cmd, text=True, capture_output=True, timeout=600, check=False, encoding='utf-8')
            if result.returncode != 0:
                console.print(f"[red]{framework_arg} benchmark failed with subprocess.run.[/red]")
                if result.stderr:
                    console.print(f"STDERR:\n{result.stderr.strip()}")
                return None
            
            if result.stdout and result.stdout.strip():
                lines = result.stdout.strip().splitlines()
                if lines:
                    return lines[-1] # Return the last line, expected to be the summary
                else:
                    console.print(f"[red]No lines in stdout from {framework_arg} benchmark script (subprocess.run path).[/red]")
                    return None
            else:
                console.print(f"[red]No stdout from {framework_arg} benchmark script (subprocess.run path).[/red]")
                if result.stderr and result.stderr.strip():
                     console.print(f"STDERR:\n{result.stderr.strip()}")
                return None
        except subprocess.TimeoutExpired:
            console.print(f"[red]Benchmark for {framework_arg} (subprocess.run path) timed out.[/red]")
            return None
        except Exception as e:
            console.print(f"[red]An unexpected error occurred while running subprocess.run benchmark for {framework_arg}: {e}[/red]")
            return None

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
        "config": "Uvicorn, async (default worker, h11, debug log)",
        "delay": "0.3 s asyncio.sleep",
        "cmd": ["uvicorn", "app_fastapi.FastAPI_with_delay:app", "--host", "0.0.0.0",
                "--port", "8000", "--log-level", "debug", "--http", "h11"],
        "url": FASTAPI_SERVER_URL,
        "bench_arg": "fastapi",
    },
    {
        "name": "Flask",
        "config": "Single-threaded, synchronous",
        "delay": "0.3 s time.sleep",
        "cmd": [PYTHON_EXE, "app_flask/Flask_with_delay.py"],
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
                # Open browser after benchmark completes to avoid interference
                try:
                    console.print(f"[blue]Opening {sc['name']} page at {sc['url']} in browser...[/blue]")
                    webbrowser.open(sc["url"])
                    console.print(f"[blue]Keeping server alive for 2 seconds to view the page...[/blue]")
                    time.sleep(2)  # Keep server alive for 2 seconds
                except Exception as e:
                    console.print(f"[yellow]Could not open browser for {sc['name']}: {e}[/yellow]")
        finally:
            stop_server(srv, sc["name"])
        console.print()

    if results:
        display_table(results)
    console.print("\n[bold]Benchmark run finished.[/bold]") 