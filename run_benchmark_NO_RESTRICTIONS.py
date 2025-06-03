import subprocess
import time
import re
import requests  # pip install requests
import webbrowser
from rich.console import Console
from rich.table import Table
import sys
import os

# --- Configuration ------------------------------------------------------
FLASK_SERVER_URL = "http://127.0.0.1:3000/"
FASTAPI_SERVER_URL = "http://127.0.0.1:8000/"
BENCHMARK_SCRIPT_PATH = "benchmark/run_benchmark.py"  # This script sends requests, delays are in apps
NUM_REQUESTS_EXPECTED = 1000
PYTHON_EXE = sys.executable

# ------------------------------------------------------------------------
console = Console()

# -------------------------- helpers -------------------------------------
def start_server(command_args, health_check_url, server_name, cwd=None):
    """Start server and wait until a 200 health check is returned."""
    console.print(f"[yellow]Starting {server_name} server (No Restrictions Test)...[/yellow]")
    popen_kwargs = dict(cwd=cwd, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
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
    # This function remains largely the same, as benchmark/run_benchmark.py handles the requests.
    # The "no restrictions" aspect is handled by running different app_*.py files.
    console.print(f"Running benchmark for [bold]{framework_arg}[/bold] (No Restrictions Test) with {NUM_REQUESTS_EXPECTED} requests...")
    cmd = [PYTHON_EXE, BENCHMARK_SCRIPT_PATH, framework_arg, str(NUM_REQUESTS_EXPECTED)]
    
    # The stdout/stderr handling can be simplified if live progress isn't strictly needed for this version,
    # or kept if useful. For now, keeping the detailed Flask progress handling.
    if framework_arg.lower() == "flask":
        final_summary_line = None
        requests_done_count = 0
        progress_line_printed = False
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True, encoding='utf-8')
            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    line = line.strip()
                    if not line: continue
                    if line.startswith("REQ_STATUS:"):
                        requests_done_count += 1
                        print(f"\rFlask progress: Handled {requests_done_count}/{NUM_REQUESTS_EXPECTED} requests...", end="", flush=True)
                        progress_line_printed = True
                    elif line.startswith("[DIAG-BRB-FLASK]"):
                        if progress_line_printed: print("\r" + " " * 80 + "\r", end="", flush=True)
                        print(line, flush=True)
                        if progress_line_printed: print(f"\rFlask progress: Handled {requests_done_count}/{NUM_REQUESTS_EXPECTED} requests...", end="", flush=True)
                    elif "Final Flask benchmark summary:" in line:
                        final_summary_line = line
                        if progress_line_printed: print("\r" + " " * 80 + "\r", end="", flush=True)
                process.stdout.close()
            if progress_line_printed and not final_summary_line: print("\r" + " " * 80 + "\r", end="", flush=True)

            stderr_output_list = []
            if process.stderr:
                for line in iter(process.stderr.readline, ''):
                    line = line.strip()
                    if line: stderr_output_list.append(line)
                process.stderr.close()
            process.wait(timeout=600)
            if process.returncode != 0:
                console.print(f"[red]{framework_arg} benchmark script failed (code {process.returncode})[/red]")
                if stderr_output_list: console.print("[red]STDERR:[/red]"); [console.print(f"[red]{err_line}[/red]") for err_line in stderr_output_list]
                return None
            if final_summary_line: return final_summary_line
            else: 
                console.print(f"[red]No summary line for {framework_arg}.[/red]")
                if stderr_output_list: console.print("[red]STDERR:[/red]"); [console.print(f"[red]{err_line}[/red]") for err_line in stderr_output_list]
                return None
        except subprocess.TimeoutExpired:
            console.print(f"[red]Benchmark for {framework_arg} timed out.[/red]")
            if process.poll() is None: process.kill(); process.wait()
            return None
        except Exception as e:
            console.print(f"[red]Error running Popen benchmark for {framework_arg}: {e}[/red]")
            return None
    else: # For FastAPI
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

                    if line.startswith("REQ_STATUS:FASTAPI_TASK_COMPLETED_"):
                        # Extract count from the message, e.g., FASTAPI_TASK_COMPLETED_123
                        try:
                            current_task_num_str = line.split('_')[-1]
                            requests_done_count = int(current_task_num_str)
                        except (IndexError, ValueError):
                            # Fallback if parsing fails, though it shouldn't with the new format
                            requests_done_count += 1 
                        print(f"\rFastAPI progress: Completed {requests_done_count}/{NUM_REQUESTS_EXPECTED} tasks...", end="", flush=True)
                        progress_line_printed = True
                    elif line.startswith("[DIAG-BRB-FASTAPI]"): # Placeholder for potential future diagnostics
                        if progress_line_printed:
                            print("\r" + " " * 80 + "\r", end="", flush=True) 
                        print(line, flush=True)
                        if progress_line_printed:
                            # Reprint the progress line after diagnostic output
                            print(f"\rFastAPI progress: Completed {requests_done_count}/{NUM_REQUESTS_EXPECTED} tasks...", end="", flush=True)
                    elif "FastAPI benchmark:" in line: # Updated to match FastAPI summary line
                        final_summary_line = line
                        if progress_line_printed:
                            print("\r" + " " * 80 + "\r", end="", flush=True)
                    else:
                        # Print any other lines from the subprocess (e.g., error messages)
                        if progress_line_printed:
                            # Clear the progress line before printing the unexpected line
                            print("\r" + " " * 80 + "\r", end="", flush=True)
                        print(line, flush=True) # Print the actual error line
                        if progress_line_printed:
                            # Reprint the progress line after the error line
                            print(f"\rFastAPI progress: Completed {requests_done_count}/{NUM_REQUESTS_EXPECTED} tasks...", end="", flush=True)

                process.stdout.close()
            
            if progress_line_printed and not final_summary_line:
                 print("\r" + " " * 80 + "\r", end="", flush=True)

            stderr_output_list = []
            if process.stderr:
                for line in iter(process.stderr.readline, ''):
                    line = line.strip()
                    if line:
                        stderr_output_list.append(line)
                process.stderr.close()

            process.wait(timeout=600) # Keep existing timeout

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
            if process.poll() is None: 
                process.kill()
                process.wait()
            return None
        except Exception as e:
            console.print(f"[red]An unexpected error occurred while running Popen benchmark for {framework_arg}: {e}[/red]")
            return None

def parse_benchmark(line):
    m = re.search(r"(\d+)/(\d+) successful requests in ([\d.]+) seconds", line)
    if not m:
        return None
    succ, total, tsec = map(float, m.groups())
    return {"successful": f"{int(succ)}/{int(total)}", "total_time": tsec}

def display_table(rows):
    tbl = Table(title="Benchmark Summary - NO RESTRICTIONS", show_lines=True, header_style="bold magenta")
    tbl.add_column("Framework", style="cyan")
    tbl.add_column("Server Config", style="white")
    tbl.add_column("Artificial Delay", style="green")
    tbl.add_column("#Reqs", justify="right")
    tbl.add_column("Success", justify="right")
    tbl.add_column("Total s", justify="right", style="yellow")
    tbl.add_column("Avg s/req", justify="right", style="blue")
    for r in rows:
        avg_time = r["total_time"] / NUM_REQUESTS_EXPECTED if NUM_REQUESTS_EXPECTED > 0 else 0
        tbl.add_row(r["framework"], r["config"], r["delay"],
                    str(NUM_REQUESTS_EXPECTED), r["successful"],
                    f"{r['total_time']:.2f}", f"{avg_time:.4f}") # Increased precision for avg
    console.print(tbl)

# --------------------------- scenarios ----------------------------------
SCENARIOS = [
    {
        "name": "FastAPI (No Delay)",
        "config": "Uvicorn, async (1 worker, httptools)",
        "delay": "None",
        "cmd": ["uvicorn", "app_fastapi.FastAPI_no_delay:app", "--host", "0.0.0.0",
                "--port", "8000", "--log-level", "warning", 
                "--workers", "1",
                "--http", "httptools"
               ],
        "url": FASTAPI_SERVER_URL,
        "bench_arg": "fastapi",
    },
    {
        "name": "Flask (No Delay, Threaded)",
        "config": "Werkzeug (threaded=True)",
        "delay": "None",
        "cmd": [PYTHON_EXE, "app_flask/Flask_no_delay.py"],
        "url": FLASK_SERVER_URL,
        "bench_arg": "flask",
    }
]

# ----------------------------- main -------------------------------------
if __name__ == "__main__":
    console.print("[bold underline]Automated Web Framework Benchmark (NO RESTRICTIONS)[/bold underline]\n")
    results = []
    root = os.getcwd()

    for i, sc in enumerate(SCENARIOS, 1):
        console.rule(f"[cyan]Scenario {i}/{len(SCENARIOS)} – {sc['name']}[/cyan]")
        srv = start_server(sc["cmd"], sc["url"], sc["name"], cwd=root)
        if not srv:
            console.print(f"[red]Skipping benchmark for {sc['name']} as server failed to start.[/red]")
            continue
        try:
            # No artificial grace period needed as apps have no sleep()
            # if sc["name"].lower().startswith("flask"):
            #     time.sleep(2) 
            line = run_benchmark_script(sc["bench_arg"])
            parsed = parse_benchmark(line) if line else None
            if parsed:
                results.append({"framework": sc["name"], "config": sc["config"],
                                "delay": sc["delay"], **parsed})
                # Optionally, open browser after benchmark. Keeping it for consistency.
                try:
                    console.print(f"[blue]Opening {sc['name']} page at {sc['url']} in browser...[/blue]")
                    webbrowser.open(sc["url"])
                    console.print(f"[blue]Keeping server alive for 3 seconds to view the page...[/blue]")
                    time.sleep(3)  # Reduced delay as pages should load faster
                except Exception as e:
                    console.print(f"[yellow]Could not open browser for {sc['name']}: {e}[/yellow]")
            else:
                console.print(f"[yellow]No parsed benchmark results for {sc['name']}.[/yellow]")
        finally:
            stop_server(srv, sc["name"])
        console.print() # Newline after each scenario

    if results:
        display_table(results)
    else:
        console.print("[yellow]No benchmark results were collected.[/yellow]")
    console.print("\n[bold]No Restrictions Benchmark run finished.[/bold]")
