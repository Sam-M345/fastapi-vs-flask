### Technical Design Document (TDD)

**Project — Flask vs FastAPI “Slow-Request” Benchmark**
*(Target audience: Python programming students; methodology: Test-Driven Development)*

---

#### 1  Overview & Scope

You will build two minimal web servers that respond to `/` after an artificial 3-second delay, then write an automated benchmark that fires 100 requests and records the total wall-clock time for each framework.  Development follows classic TDD: **red → green → refactor**.

---

#### 2  Technology Stack

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

#### 3  Phased Plan

Each phase contains **Objective**, **Tasks**, **Tests (written first)**, and **Expected Result**.

---

##### **Phase 0 — Environment & Repo Skeleton**

*Objective*

* Isolate project in a virtual environment; create Git repository with CI (GitHub Actions).

*Tasks*

1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install flask fastapi uvicorn pytest httpx requests`
3. Scaffold folders:

   ```
   project/
     app_flask/
     app_fastapi/
     tests/
     benchmark/
   ```
4. Pre-commit hooks for `ruff`/`black`.

*Tests*

* **None** (meta-phase) — verify by `pytest -q` returning *collected 0 items*.

*Expected Result*

* Clean repo, `pytest` runs successfully (0 tests).

---

##### **Phase 1 — Red Test for Flask Home Route**

*Objective*

* Specify behaviour of Flask server before implementation.

*Tasks*

1. Write failing test `tests/test_flask_route.py`.

```python
import httpx
import subprocess, time, os, signal

def start_server():
    proc = subprocess.Popen(["python", "-m", "app_flask.app"])
    time.sleep(0.2)  # allow startup
    return proc

def test_home_returns_html():
    proc = start_server()
    try:
        r = httpx.get("http://127.0.0.1:5000/", timeout=10)
        assert r.status_code == 200
        assert "Slow Flask Demo" in r.text
    finally:
        os.kill(proc.pid, signal.SIGINT)
```

*Expected Result*

* `pytest` fails with *ConnectionError* (❌ **red**) because server not yet written.

---

##### **Phase 2 — Green Implementation for Flask**

*Objective*

* Make the red test pass.

*Tasks*

```python
# app_flask/app.py
from flask import Flask, Response
import time

app = Flask(__name__)

@app.route("/")
def home():
    time.sleep(3)                # simulate slow work
    html = "<h1>Slow Flask Demo</h1>"
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    app.run()
```

*Tests*

* Re-run `pytest -q`.

*Expected Result*

* Test passes (✅ **green**).  Refactor if desired (logging, config).

---

##### **Phase 3 — Red Test for FastAPI Home Route**

*Objective*

* Write failing async test that mirrors Flask expectations.

*Tasks*

```python
# tests/test_fastapi_route.py
import httpx, subprocess, asyncio, os, signal, time

async def start_server():
    proc = subprocess.Popen(["uvicorn", "app_fastapi.app:app"])
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
        os.kill(proc.pid, signal.SIGINT)
```

*Expected Result*

* Test fails (❌ **red**).

---

##### **Phase 4 — Green Implementation for FastAPI**

*Objective*

* Pass the FastAPI test using non-blocking delay.

*Tasks*

```python
# app_fastapi/app.py
from fastapi import FastAPI, Response
import asyncio

app = FastAPI()

@app.get("/")
async def home():
    await asyncio.sleep(3)                    # simulate slow work (non-blocking)
    html = "<h1>Slow FastAPI Demo</h1>"
    return Response(content=html, media_type="text/html")
```

*Tests*

* Run `pytest -q`; both test suites should pass.

*Expected Result*

* All unit tests green.  Total runtime still quick because delay happens only once per request, not per test.

---

##### **Phase 5 — Benchmark Harness (Integration)**

*Objective*

* Produce reproducible timing of 100 concurrent requests against each server.

*Tasks*

1. Write script `benchmark/run_benchmark.py`.
2. Parametrise for framework (`flask` or `fastapi`).
3. For Flask: spawn 100 threads calling `requests.get`.
4. For FastAPI: spawn 100 asynchronous tasks using `httpx.AsyncClient`.
5. Record `time.perf_counter()` start/stop.
6. Output aggregate wall-clock seconds and simple histogram (optional).

*Tests*

* **Integration**: add `tests/test_benchmark.py` that asserts:
  *Flask total time > 3 seconds* (likely \~≥ 3 s × ceil(100/threads\_per\_worker)).
  *FastAPI total time ≈ 3–4 seconds* (all tasks awaited concurrently).
  Accept generous tolerance (±1 s) to avoid flaky CI.

```python
def test_fastapi_faster():
    flask_time = run_once("flask")
    fast_time = run_once("fastapi")
    assert fast_time < flask_time
```

*Expected Result*

* Benchmark script prints e.g.

```
Flask  (100 req): 18.4 s
FastAPI(100 req):  3.7 s
```

* Test asserting relative performance passes.

---

##### **Phase 6 — Refactor & Documentation**

*Objective*

* Clean code, extract common settings, add README & docstrings.

*Tasks*

1. Factor out “HTML template” constant.
2. Use environment variables for port numbers.
3. Add `requirements.txt` & `make start_flask` / `make start_fastapi`.
4. Write tutorial in `docs/` explaining how asynchronous I/O yields throughput gains.

*Tests*

* Static analysis (`ruff`, `black`), docs build passes.
* Re-run full `pytest`; no regressions.

*Expected Result*

* CI matrix (Linux, macOS, Windows) all green.
* Students understand sync vs async latency differences through quantitative evidence.

---

#### 4  Open Questions

1. **Concurrency level** — should benchmark cap threads at CPU-count × N or always 100?
2. **CI resources** — GitHub Actions offers limited RAM; long benchmarks may time-out.
3. **Optional extras** — Would you like to visualise results (matplotlib bar chart) or stick to plain text?

Let me know if any of the open questions need refinement before you start coding — otherwise you can begin with *Phase 0* and run the initial (failing) Flask test.
