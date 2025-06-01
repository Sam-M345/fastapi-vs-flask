# Handoff: Flask Benchmark Stalling Issue

---

## 1 · Affected Files

| Path                                 | Purpose                                                                                                    |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| `SOP/Handoff-FlaskBenchmarkStall.md` | This handoff document                                                                                      |
| `show_benchmark_table.py`            | Orchestrates server startup/shutdown, runs benchmarks, parses results. Flask test fails under this script. |
| `benchmark/run_benchmark.py`         | Client script that sends HTTP requests. Flask requests time out when called by `show_benchmark_table.py`.  |
| `app_flask/flask_application.py`     | The Flask server application that becomes unresponsive.                                                    |
| `app_fastapi/app.py`                 | FastAPI application (for comparison, works correctly).                                                     |

---

## 2 · Problem Statement

**What's wrong:**
The Flask server (`app_flask/flask_application.py`), when started and benchmarked automatically by `show_benchmark_table.py`, becomes unresponsive after processing approximately 52-53 requests. The client script (`benchmark/run_benchmark.py`) then experiences `requests.exceptions.ReadTimeout` for all subsequent requests to the Flask server.

**Symptoms / error messages:**

- Benchmark client output (from `benchmark/run_benchmark.py` via `show_benchmark_table.py`):
  `Request to http://127.0.0.1:3000/ failed: HTTPConnectionPool(host='127.0.0.1', port=3000): Read timed out. (read timeout=5)` for requests ~53 through 100.
- `show_benchmark_table.py` diagnostic STDOUT lines confirm this:
  `[DIAG-SBT-STDOUT] Line 111: '[DIAG-BRB-FLASK] Request 52 result: 200'`
  `[DIAG-SBT-STDOUT] Line 112: '[DIAG-BRB-FLASK] Processing request 53/100'`
  `[DIAG-SBT-STDOUT] Line 113: 'Request to http://127.0.0.1:3000/ failed: HTTPConnectionPool(host='127.0.0.1', port=3000): Read timed out. (read timeout=5)'`
  `[DIAG-SBT-STDOUT] Line 114: '[DIAG-BRB-FLASK] Request 53 result: None'`
- The Flask server itself provides no error messages on its console output when it becomes unresponsive; it simply stops processing new requests.

**Expected vs. actual behaviour:**

- **Expected:** The Flask server should handle all 100 requests successfully when benchmarked by `show_benchmark_table.py`. The script should report approximately 100 successful requests for Flask. This matches the behavior when `benchmark/run_benchmark.py flask` is executed manually against a manually started Flask server (100/100 successful).
- **Actual:** The Flask server handles ~52 requests then stops responding. `show_benchmark_table.py` reports ~52 successful requests, with the remaining ~48 requests failing due to timeouts.

**Business or user impact (severity & priority):**
The automated benchmark for Flask is unreliable and does not complete. This prevents an accurate performance comparison with FastAPI using the automated test harness, which is a key goal of the project.

- Severity: High (for the benchmarking task)
- Priority: High

---

## 3 · Reproduction Steps

1.  Ensure the Flask server (`app_flask/flask_application.py`) and FastAPI server (`app_fastapi/app.py`) are not already running manually.
2.  Open a terminal in the project root directory (`/c%3A/Users/Sam/Desktop/Side%20Projects/FastAPI%20vs%20Flask/Hacker%20Dojo`).
3.  Ensure the Python virtual environment (e.g., `(.venv)`) is activated.
4.  Execute the command: `python show_benchmark_table.py`.
5.  Observe the console output. The FastAPI benchmark should complete successfully.
6.  During the Flask benchmark portion, observe that requests are processed normally up to approximately request #52.
7.  After request #52, the script will begin logging `Read timed out` errors for subsequent requests to the Flask server. The "Flask progress" messages will show that the count of successful requests plateaus around 52.

---

## 4 · Attempted Solutions & Findings

| Attempt                                           | Key Changes Made                                                                                                                                                                          | Outcome / Remaining Issue                                                                                                                                                                                                                |
| :------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| #1: Initial Automated Benchmark (Threaded Client) | Flask server started/stopped by `show_benchmark_table.py`. Benchmark client in `benchmark/run_benchmark.py` used `ThreadPoolExecutor` with `max_workers=100`.                             | Flask benchmark hung indefinitely after ~50-52 requests. Client did not initially have explicit timeouts, so it just waited.                                                                                                             |
| #2: Client-Side Timeout Added                     | Added `timeout=5` to `requests.get()` in `fetch_url_sync` function within `benchmark/run_benchmark.py`.                                                                                   | Revealed that the client was hanging because the Flask server became unresponsive. Requests from ~53 onwards explicitly timed out. This fixed the client hanging but not the server unresponsiveness.                                    |
| #3: Sequential Client-Side Requests (Diagnosis)   | Modified `run_flask_benchmark` in `benchmark/run_benchmark.py` to use a simple sequential `for` loop for sending requests, instead of `ThreadPoolExecutor`.                               | Confirmed the issue is not primarily client-side threading. The Flask server still became unresponsive after ~52 requests, and subsequent requests (~53+) timed out even with the sequential client.                                     |
| #4: One-Time Stabilization Pause for Flask Server | Added a `time.sleep(3)` in `show_benchmark_table.py` (within `run_test_scenario`) immediately after the Flask server was confirmed to be started and before the benchmark script was run. | This did not resolve the issue. The Flask server still becomes unresponsive after ~52 requests when managed by `show_benchmark_table.py`. The failure point remained consistent (last successful request is #52, timeout starts at #53). |

**Current blockers / unknowns:**

- The primary unknown is why the Flask development server (single-threaded, `threaded=False`, Werkzeug-based) becomes unresponsive after ~52 requests _only when_ its lifecycle (start/stop) is managed by the `show_benchmark_table.py` script using `subprocess.Popen`. Manual execution of the benchmark against a manually started Flask server completes successfully.
- Is there a resource leak, an internal connection queue limit, or another issue within the Flask development server (or Werkzeug) that is specifically triggered by the rapid automated start-test-stop cycle or by the interaction with `subprocess.Popen` as configured?
- The Flask server does not output any error messages or warnings to its console when it hangs/becomes unresponsive.

---

## 5 · Developer Instructions

**Goal:** Identify the root cause of the Flask development server becoming unresponsive after ~52 requests when managed by `show_benchmark_table.py`. Implement a sustainable fix to allow the Flask benchmark to complete all 100 requests successfully under this automated test harness.

1.  **Review Code:** Thoroughly examine the _Affected Files_ listed above, particularly how `show_benchmark_table.py` manages the Flask server process and how `benchmark/run_benchmark.py` interacts with it.
2.  **Trace Execution:** Understand the full execution path from `show_benchmark_table.py` initiating the Flask server, through `benchmark/run_benchmark.py` making HTTP requests, up to the point of failure.
3.  **Investigate Potential Causes:**
    - **Flask/Werkzeug Internals:** Research if Flask's built-in Werkzeug development server has any known limitations on concurrent connections, request queues, or resource handling that might be triggered by ~50 rapid requests, especially when programmatically started/stopped.
    - **Socket/Resource Issues:** While `threaded=False` is used, investigate if there's any subtle socket exhaustion or OS-level resource issue affecting the Flask process when run via `subprocess`.
    - **`subprocess.Popen` Interaction:** Analyze if the specific way `show_benchmark_table.py` uses `subprocess.Popen` (including PIPE usage for stdout/stderr) could be affecting the Flask server's stability under load. Consider if different Popen configurations or process group handling might be necessary.
    - **Enhanced Server Logging:** Attempt to increase the verbosity of logging from Flask and Werkzeug. This might require modifying `app_flask/flask_application.py` or how the app is run to get more detailed internal state or error messages from the server side just before it hangs.
    - **Alternative WSGI Server (for diagnosis):** As a diagnostic step, temporarily replace Flask's development server with a more production-like WSGI server that is Windows-compatible (e.g., `waitress`). Modify `show_benchmark_table.py` to start Flask with `waitress` and see if the problem persists. This can help isolate if the issue is specific to the Werkzeug dev server.
    - **Connection Keep-Alive:** Investigate if HTTP connection keep-alive behavior between `requests` (client) and Flask (server) plays a role. Though `requests` typically handles sessions, the rapid succession of individual `requests.get()` calls might interact differently than fewer, longer-lived sessions.
4.  **Propose and Implement Solution:** Based on findings, implement a robust solution. This could involve:
    - Adjusting Flask application or Werkzeug server options (if suitable options exist).
    - Modifying how `show_benchmark_table.py` launches or manages the Flask server process.
    - Minor, justified changes to the client request pattern if it's found to trigger a specific server bug (less likely, as manual client run works).
5.  **Verify:** Ensure the solution allows `show_benchmark_table.py` to successfully run both Flask and FastAPI benchmarks to completion (100 requests each) and report accurate results.
6.  **Document:** Update this handoff document with detailed findings, the rationale for the chosen solution, any trade-offs, and potential side effects.
7.  **Testing:** Ensure existing tests (if any) pass, and consider if new tests are needed for the fix.

---

_End of Handoff-FlaskBenchmarkStall.md_
