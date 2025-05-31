### Technical Design Document (TDD)

**Project — Flask vs FastAPI "Slow-Request" Benchmark**
_(Target audience: Python programming students; methodology: Test-Driven Development)_

---

#### 1 Overview & Scope

You will build two minimal web servers that respond to `/` after an artificial 3-second delay, then write an automated benchmark that fires 100 requests and records the total wall-clock time for each framework. Development follows classic TDD: **red → green → refactor**.

---

#### 2 Technology Stack

| Layer                           | Choice                                                                       | Rationale                                              |
| ------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------ |
| Language                        | Python ≥ 3.11                                                                | uniform tooling for both servers & benchmark           |
| Sync server                     | **Flask 3**                                                                  | most widely taught micro-framework                     |
| Async server                    | **FastAPI 0.111** (Starlette under the hood)                                 | modern async example                                   |
| Test runner                     | **pytest**                                                                   | de-facto Python TDD tool                               |
| HTTP client in tests            | **httpx**                                                                    | sync & async interfaces in one library                 |
| Benchmark script                | pure Python (requests & httpx)                                               | keep everything in Python for the class                |
| Concurrency model for benchmark | `concurrent.futures.ThreadPoolExecutor` (Flask) & `asyncio.gather` (FastAPI) | illustrates difference between blocking & non-blocking |

---

These project phases are:

Phase 0 — Environment & Repo Skeleton
......Objective: Setup project environment and repository.

Phase 1 — Red Test for Flask Home Route
......Objective: Write failing test for Flask server.

Phase 2 — Green Implementation for Flask
......Objective: Implement Flask server to pass test.

Phase 3 — Red Test for FastAPI Home Route
......Objective: Write failing test for FastAPI server.

Phase 4 — Green Implementation for FastAPI
......Objective: Implement FastAPI server to pass test.

Phase 5 — Benchmark Harness (Integration)
......Objective: Create benchmark script and integration tests.

Phase 6 — Refactor & Documentation
......Objective: Refactor code and add project documentation.

---

#### 3 Phased Plan

Each phase contains **Objective**, **Key Tasks**, **Tests (written first)**, and **Expected Result**.

---

##### **Phase 0 — Environment & Repo Skeleton**

_Objective_

- Isolate project in a virtual environment; create Git repository with CI (GitHub Actions).

_Key Tasks_

- Set up virtual environment: `python -m venv .venv && source .venv/bin/activate` (or equivalent for OS).
- Install core dependencies: `pip install flask fastapi uvicorn pytest httpx requests`.
- Create project directory structure:
  ```
  project/
    app_flask/
    app_fastapi/
    tests/
    benchmark/
  ```
- (Optional) Configure pre-commit hooks for `ruff`/`black`.

_Tests_

- **None** (meta-phase) — verify by `pytest -q` returning _collected 0 items_.

_Expected Result_

- Clean repo, `pytest` runs successfully (0 tests).

---

##### **Phase 1 — Red Test for Flask Home Route**

_Objective_

- Specify behaviour of Flask server before implementation.

_Key Tasks_

- Write a failing test in `tests/test_flask_route.py` that:
  - Starts a Flask server (conceptually, on port 5000).
  - Makes an HTTP GET request to `/`.
  - Asserts a 200 status code.
  - Asserts specific HTML content (e.g., "Slow Flask Demo").
  - Ensures server shutdown.

```python
# Example structure for tests/test_flask_route.py
import httpx
import subprocess, time, os, signal

def start_server():
    proc = subprocess.Popen(["python", "-m", "app_flask.app"]) # Non-existent app
    time.sleep(0.2)
    return proc

def test_home_returns_html():
    proc = start_server()
    try:
        r = httpx.get("http://127.0.0.1:5000/", timeout=10)
        assert r.status_code == 200
        assert "Slow Flask Demo" in r.text
    finally:
        os.kill(proc.pid, signal.SIGINT) # Or proc.terminate()
```

_Actual Result / Verification (Phase 1)_

To verify the "red" state, the following command was run from the project root after activating the virtual environment (`.\.venv\Scripts\activate`):

```bash
.\.venv\Scripts\python.exe -m pytest -p no:all
```

The terminal output included:

```
=========================================== short test summary info ============================================
FAILED project/tests/test_flask_route.py::test_home_returns_html - httpx.ConnectError: [WinError 10061] No con
nection could be made because the target machine actively refused it
============================================== 1 failed in X.XXs ===============================================
```

And the captured stderr showed:

```
C:\Users\Sam\AppData\Local\Programs\Python\Python312\python.exe: No module named project.app_flask.app
```

_Indications:_

- The `httpx.ConnectError` confirmed that the test failed because the HTTP server at `http://127.0.0.1:5000/` was not running or reachable.
- The `stderr` message `No module named project.app_flask.app` confirmed that the Flask application code had not yet been created.
- This aligns with the TDD expectation of a "red" test because the server is not yet written.

---

##### **Phase 2 — Green Implementation for Flask**

_Objective_

- Make the red test pass.

_Key Tasks_

- Create `app_flask/app.py` (or `app_flask/flask_application.py` as per actual implementation).
- Implement a Flask application:
  - Listens on `/`.
  - Returns "<h1>Slow Flask Demo</h1>" (or matching text from test).
  - Includes an artificial `time.sleep(3)`.
  - Runs on the port expected by the test (e.g., 5000 or 3000).

```python
# app_flask/app.py (example)
from flask import Flask, Response
import time

app = Flask(__name__)

@app.route("/")
def home():
    time.sleep(3)
    html = "<h1>Slow Flask Demo</h1>"
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    app.run(port=5000) # Match test port
```

_Tests_

- Re-run `pytest -q`.

_Expected Result_

- Test passes (✅ **green**). Refactor if desired (logging, config).

---

##### **Phase 3 — Red Test for FastAPI Home Route**

_Objective_

- Write failing async test that mirrors Flask expectations.

_Key Tasks_

- Create `tests/test_fastapi_route.py`.
- Write a failing `pytest` test using `async` and `httpx.AsyncClient`:
  - Starts a FastAPI server using `uvicorn` (conceptually, on port 8000).
  - Makes an HTTP GET request to `/`.
  - Asserts a 200 status code.
  - Asserts specific HTML content (e.g., "Slow FastAPI Demo").
  - Ensures server shutdown.

```python
# tests/test_fastapi_route.py (example)
import httpx, subprocess, asyncio, os, signal, time
import pytest

async def start_server():
    proc = subprocess.Popen(["uvicorn", "app_fastapi.app:app", "--port", "8000"]) # Non-existent app
    await asyncio.sleep(0.2)
    return proc

@pytest.mark.asyncio
async def test_home_returns_html():
    proc = await start_server()
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("http://127.0.0.1:8000/")
            assert r.status_code == 200
            assert "Slow FastAPI Demo" in r.text
    finally:
        os.kill(proc.pid, signal.SIGINT) # Or proc.terminate()
```

_Expected Result_

- Test fails (❌ **red**), likely due to connection error as `app_fastapi/app.py` is not yet created.

---

##### **Phase 4 — Green Implementation for FastAPI**

_Objective_

- Pass the FastAPI test using non-blocking delay.

_Key Tasks_

- Create `app_fastapi/app.py`.
- Implement a FastAPI application:
  - Listens on `/`.
  - Returns "<h1>Slow FastAPI Demo</h1>" (or matching text from test).
  - Includes an artificial `await asyncio.sleep(3)` (non-blocking).
  - Ensure `uvicorn` runs it on the port expected by the test (e.g., 8000).

```python
# app_fastapi/app.py (example)
from fastapi import FastAPI, Response
import asyncio

app = FastAPI()

@app.get("/")
async def home():
    await asyncio.sleep(3)
    html = "<h1>Slow FastAPI Demo</h1>"
    return Response(content=html, media_type="text/html")

# Uvicorn will run this: uvicorn app_fastapi.app:app --port 8000
```

_Tests_

- Run `pytest -q`; both test suites (Flask & FastAPI) should pass.

_Expected Result_

- All unit tests green. Total runtime still quick because delay happens only once per request, not per test.

---

##### **Phase 5 — Benchmark Harness (Integration)**

_Objective_

- Produce reproducible timing of 100 concurrent requests against each server.

_Key Tasks_

- Create script `benchmark/run_benchmark.py`.
- Parameterize script for framework (`flask` or `fastapi`).
- Implement Flask benchmark:
  - Use `concurrent.futures.ThreadPoolExecutor` to spawn 100 threads.
  - Each thread calls `requests.get` to the Flask server's endpoint.
- Implement FastAPI benchmark:
  - Use `asyncio.gather` with `httpx.AsyncClient` to make 100 concurrent requests.
- Record and output total wall-clock time for each framework using `time.perf_counter()`.
- (Optional) Output a simple histogram of request times.

_Tests_

- **Integration Test**: Create `tests/test_benchmark.py`.

  - Assert that Flask total time > 3 seconds (actual time depends on concurrency).
  - Assert that FastAPI total time ≈ 3–4 seconds (more truly concurrent).
  - Add a test `test_fastapi_faster()`:

    ```python
    def test_fastapi_faster():
        flask_time = run_once("flask") # Assumes run_once executes the benchmark
        fast_time = run_once("fastapi")
        assert fast_time < flask_time
    ```

  - Use generous time tolerances (e.g., ±1 s) for CI stability.

_Expected Result_

- Benchmark script prints comparative timings, e.g.:
  ```
  Flask  (100 req): 18.4 s
  FastAPI(100 req):  3.7 s
  ```
- Integration test asserting relative performance passes.

---

##### **Phase 6 — Refactor & Documentation**

_Objective_

- Clean code, extract common settings, add README & docstrings.

_Key Tasks_

- Refactor code:
  - Extract common HTML template string into a constant if used in multiple places.
  - Consider using environment variables or a config file for port numbers.
- Create `requirements.txt`: `pip freeze > requirements.txt`.
- (Optional) Add convenience scripts/Makefile targets (e.g., `make start_flask`).
- Write a tutorial in `docs/` (or update README.md) explaining:
  - How to run the servers and benchmark.
  - The concepts of synchronous vs. asynchronous I/O.
  - How the benchmark results demonstrate throughput gains with async.
- Add docstrings to functions and modules.

_Tests_

- Run static analysis (e.g., `ruff`, `black`).
- (If applicable) Ensure documentation builds successfully.
- Re-run full `pytest` suite to check for regressions.

_Expected Result_

- CI matrix (Linux, macOS, Windows) all green.
- Project is well-documented and easy for students to understand and run.
- Students understand sync vs. async latency/throughput differences through quantitative evidence.

---

#### 4 Open Questions

1. **Concurrency level** — should benchmark cap threads at CPU-count × N or always 100?
2. **CI resources** — GitHub Actions offers limited RAM; long benchmarks may time-out.
3. **Optional extras** — Would you like to visualise results (matplotlib bar chart) or stick to plain text?

Let me know if any of the open questions need refinement before you start coding — otherwise you can begin with _Phase 0_ and run the initial (failing) Flask test.
