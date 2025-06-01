import subprocess
import sys
import os
import re
import pytest

# Path to the benchmark script
BENCHMARK_SCRIPT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "benchmark", "run_benchmark.py"
)

def run_benchmark_script(framework_name: str) -> float:
    \"\"\"
    Runs the benchmark script for the given framework and returns the reported time.
    Raises RuntimeError if the script fails or output cannot be parsed.
    \"\"\"
    if not os.path.exists(BENCHMARK_SCRIPT_PATH):
        raise FileNotFoundError(f"Benchmark script not found at {BENCHMARK_SCRIPT_PATH}")

    command = [sys.executable, BENCHMARK_SCRIPT_PATH, framework_name]
    
    try:
        # Ensure the script is run from the project root for consistent module resolution if any
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=300, # 5 minutes timeout, adjust as needed
            cwd=project_root 
        )
        output = process.stdout
        # print(f"--- Benchmark output for {framework_name} ---\\n{output}\\n-----------------------------------------") # For debugging

        # Regex to find "X.XX seconds." and capture X.XX
        # Example line: "Flask benchmark: 100/100 successful requests in 15.32 seconds."
        match = re.search(r"(\\d+\\.\\d{2}) seconds\\.", output)
        if match:
            return float(match.group(1))
        else:
            raise ValueError(
                f"Could not parse execution time from benchmark output for {framework_name}.\\nOutput:\\n{output}"
            )
    except FileNotFoundError: # Should be caught by the initial check, but as a safeguard for command itself
        raise RuntimeError(f"Python executable not found at {sys.executable} or script path incorrect.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Benchmark script for {framework_name} failed with exit code {e.returncode}.\\n"
            f"Stdout:\\n{e.stdout}\\n"
            f"Stderr:\\n{e.stderr}"
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            f"Benchmark script for {framework_name} timed out after {e.timeout} seconds.\\n"
            f"Stdout:\\n{e.stdout}\\n"
            f"Stderr:\\n{e.stderr}"
        )
    except ValueError as e: # Re-raise specific parsing error
        raise e
    except Exception as e: # Catch any other unexpected errors
        raise RuntimeError(f"An unexpected error occurred while running benchmark for {framework_name}: {e}")


# --- Test Cases ---

# Note: These tests will run the actual servers and benchmark script.
# Ensure the Flask and FastAPI applications (app_flask/flask_application.py and app_fastapi/app.py)
# are correctly implemented to listen on FLASK_URL and FASTAPI_URL specified in run_benchmark.py
# (http://127.0.0.1:3000/ and http://127.0.0.1:8000/ respectively).
# The tests also depend on the external Flask and FastAPI servers being started by the benchmark script's logic
# (implicitly, as the benchmark script itself doesn't start servers; it assumes they are running).
# This is a deviation from the unit tests which start servers.
# The benchmark script ITSELF is what's being tested here, not the servers ability to start.
# The benchmark script expects servers to be ALREADY running at the specified URLs.

# THIS IS A PROBLEM: The benchmark script `run_benchmark.py` does NOT start the servers.
# The tests in test_flask_route.py and test_fastapi_route.py DO start the servers.
# The TDD for Phase 5 benchmark harness does not explicitly state the benchmark script should start servers,
# but the integration tests for the benchmark WILL require servers to be running.

# For these integration tests to work as intended by the TDD (testing the benchmark script),
# we will need to:
# 1. Start the Flask server.
# 2. Run the Flask benchmark script and get its time.
# 3. Stop the Flask server.
# 4. Start the FastAPI server.
# 5. Run the FastAPI benchmark script and get its time.
# 6. Stop the FastAPI server.
# This makes the test_benchmark.py more complex as it needs to manage server processes
# similar to how test_flask_route.py and test_fastapi_route.py do.

# Let's adjust `run_benchmark_script` to accept server management functions or integrate them.
# For now, I will write the tests assuming the servers are MANUALLY started before running pytest for these.
# This is a point to clarify or improve based on TDD Phase 5 goals.
# The TDD says: "Assert that Flask total time > 3 seconds" etc.
# This implies the benchmark script is run against live servers.


# Global variables to store benchmark times to avoid re-running for each assertion if not necessary
# However, for true isolation and to ensure each test measures fresh, it's better to run the benchmark for each.
# Let's run it each time for now. A setup_module could optimize later if too slow.

FLASK_BENCH_TIME = -1.0
FASTAPI_BENCH_TIME = -1.0

# Pytest markers for skipping if servers aren't intended to be up, or for explicit server setup.
# For now, these tests will FAIL if servers are not running at the expected ports.

@pytest.mark.benchmark_integration  # Custom marker
def test_flask_benchmark_timing():
    \"\"\"Tests the Flask benchmark timing.\"\"\"
    global FLASK_BENCH_TIME
    # This requires the Flask server to be running on http://127.0.0.1:3000/
    # AND the FastAPI server on http://127.0.0.1:8000/ (though not directly used by this specific call)
    # because the benchmark script itself doesn't conditionally import/run parts.
    # Actually, run_benchmark.py only needs the specific server it's targeting.
    
    print("\\nRunning Flask benchmark for timing test...")
    flask_time = run_benchmark_script("flask")
    FLASK_BENCH_TIME = flask_time # Store for potential use in other tests
    print(f"Flask benchmark reported: {flask_time:.2f}s")
    
    # TDD: Assert that Flask total time > 3 seconds (actual time depends on concurrency)
    # Given 100 requests and a 3s delay each, serially it's 300s.
    # With ThreadPoolExecutor, it's much less but still significant.
    # A single request is 3s. For 100 requests, even with threads, it must be > 3s.
    # It should be substantially more if NUM_REQUESTS / num_cores > a few cycles of 3s.
    # For 100 requests, if 8 cores, roughly 100/8 * 3 = 12.5 * 3 = ~37.5s (very rough).
    # The TDD example shows "Flask (100 req): 18.4 s".
    assert flask_time > 3.0, "Flask benchmark time should be greater than the artificial 3s delay."
    # A more realistic lower bound for 100 requests might be NUM_REQUESTS * 3 / MAX_POSSIBLE_CONCURRENCY_FACTOR
    # For now, TDD's "> 3s" is the primary guide, but we expect it to be higher.


@pytest.mark.benchmark_integration
def test_fastapi_benchmark_timing():
    \"\"\"Tests the FastAPI benchmark timing.\"\"\"
    global FASTAPI_BENCH_TIME
    # This requires the FastAPI server to be running on http://127.0.0.1:8000/
    print("\\nRunning FastAPI benchmark for timing test...")
    fastapi_time = run_benchmark_script("fastapi")
    FASTAPI_BENCH_TIME = fastapi_time
    print(f"FastAPI benchmark reported: {fastapi_time:.2f}s")

    # TDD: Assert that FastAPI total time ≈ 3–4 seconds (more truly concurrent)
    assert 2.9 < fastapi_time < 5.0, "FastAPI benchmark time should be close to 3-4s (e.g., 2.9s to 5s for tolerance)."
    # The TDD example shows "FastAPI(100 req): 3.7 s"

@pytest.mark.benchmark_integration
def test_fastapi_is_faster_than_flask():
    \"\"\"Tests that FastAPI benchmark is faster than Flask benchmark.\"\"\"
    # Re-run benchmarks to ensure fresh comparison unless already run and stored
    # For reliability, let's re-run, though it adds to test time.
    print("\\nRe-running Flask benchmark for comparison...")
    flask_comparison_time = run_benchmark_script("flask")
    print(f"Flask benchmark for comparison reported: {flask_comparison_time:.2f}s")
    
    print("\\nRe-running FastAPI benchmark for comparison...")
    fastapi_comparison_time = run_benchmark_script("fastapi")
    print(f"FastAPI benchmark for comparison reported: {fastapi_comparison_time:.2f}s")

    # TDD: Add a test test_fastapi_faster(): assert fast_time < flask_time
    assert fastapi_comparison_time < flask_comparison_time, "FastAPI should be significantly faster than Flask for this benchmark."

# To run these tests:
# 1. Ensure Flask server (app_flask/flask_application.py) can be started on http://127.0.0.1:3000/
# 2. Ensure FastAPI server (app_fastapi/app.py) can be started on http://127.0.0.1:8000/
# 3. Manually start BOTH servers in separate terminals before running pytest.
#    - Terminal 1: python app_flask/flask_application.py
#    - Terminal 2: uvicorn app_fastapi.app:app --host 127.0.0.1 --port 8000
# 4. Then run: pytest tests/test_benchmark.py -m benchmark_integration -s -v
#    (-s for stdout, -v for verbose, -m to pick only these tests)

# Future improvement:
# - Use pytest fixtures (e.g., session-scoped) to start/stop the Flask and FastAPI servers
#   automatically before and after these benchmark tests run. This would make them self-contained.
#   This would involve adapting the server-starting logic from test_flask_route.py and test_fastapi_route.py.
#   For example, a fixture could yield a server process, and the tests would use that. 