# FastAPI vs Flask Performance Benchmark

This project provides a benchmarking suite to compare the performance of FastAPI and Flask web frameworks under various conditions, including scenarios with and without artificial delays.
It originated from a challenge to build minimal Flask and FastAPI web servers, each with an artificial 3-second delay (later adjusted), and then benchmark them by sending a configurable number of requests to observe performance differences.

## Project Overview

The primary goal is to offer a clear, reproducible way to measure and contrast the request handling capabilities of FastAPI (using Uvicorn) and Flask (using Werkzeug's development server). It includes:

- Simple web applications for both FastAPI and Flask.
- Benchmark scripts to send a configurable number of concurrent requests.
- Scripts to orchestrate the server startup, benchmark execution, and result tabulation for different scenarios.

## Directory Structure

```
Hacker Dojo/
├── .venv/                    # Virtual environment
├── app_fastapi/              # FastAPI application files
│   ├── FastAPI_no_delay.py
│   └── FastAPI_with_delay.py
├── app_flask/                # Flask application files
│   ├── Flask_no_delay.py
│   └── Flask_with_delay.py
├── benchmark/                # Core benchmark script
│   └── run_benchmark.py
├── Design Docs/              # Project design documents (e.g., TDD.md, ignored by Git)
├── SOP/                      # Standard Operating Procedures & Handoff notes
├── .gitignore                # Files and directories ignored by Git
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── run_benchmark_NO_RESTRICTIONS.py # Runs benchmarks for no-delay apps
└── run_benchmark_table.py    # Runs benchmarks for apps with delays and generates a table
```

## Prerequisites

- Python 3.8+ (developed and tested with Python 3.11/3.12)
- Git

## Key Technologies Used

- **Python**: Core language for servers and scripting.
- **Flask**: Synchronous web framework.
- **FastAPI**: Asynchronous web framework.
- **Uvicorn**: ASGI server for FastAPI.
- **Werkzeug**: WSGI toolkit and development server for Flask.
- **httpx**: HTTP client for benchmarks.
- **pytest**: Testing framework (see "Development and Testing" section).
- **Rich**: For formatted table output.

## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-url>
    cd Hacker-Dojo
    ```

2.  **Create and activate a virtual environment:**

    - On Windows:
      ```bash
      python -m venv .venv
      .venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      python3 -m venv .venv
      source .venv/bin/activate
      ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Benchmarks

This project provides two main scripts to run benchmarks:

1.  **`run_benchmark_table.py`:**
    This script benchmarks applications that include an artificial `time.sleep(0.3)` delay in their request handlers. It typically tests fewer requests and is good for observing behavior with I/O-bound-like operations.

    ```bash
    python run_benchmark_table.py
    ```

    The results will be displayed in a table in your console.

2.  **`run_benchmark_NO_RESTRICTIONS.py`:**
    This script benchmarks applications that do _not_ have any artificial delays. It's designed to test CPU-bound performance and raw request throughput with a higher number of requests (typically 1000).
    ```bash
    python run_benchmark_NO_RESTRICTIONS.py
    ```
    Results will also be displayed in a table in the console.

**Important Notes:**

- Ensure no other applications are using ports 3000 (for Flask) or 8000 (for FastAPI) when running the benchmarks. The scripts attempt to manage server processes, but conflicts can still occur.
- Benchmark results can be influenced by your system's hardware, OS, and current load. For the most accurate comparisons, run benchmarks in a consistent environment.

## Development and Testing

This project was initially developed following a Test-Driven Development (TDD) methodology. The general approach involved:

1.  Writing failing tests for specific routes or functionalities (Red).
2.  Implementing the minimal code required to make the tests pass (Green).
3.  Refactoring the code for clarity and efficiency (Refactor).

The `Design Docs/TDD.md` file (which is not part of the Git repository) contains the original detailed phased plan and example tests using `pytest` and `httpx` for:

- Basic Flask and FastAPI route functionality.
- Benchmark harness integration.

While the dedicated `tests/` directory and its initial test files were removed during the project's evolution to focus on the benchmarking scripts, the `TDD.md` serves as a valuable reference for understanding the original testing strategy or for re-introducing a test suite.

If a test suite is re-established (e.g., in a `tests/` directory), tests would typically be run using a command like:

```bash
pytest
```

## Interpreting Results

The benchmark scripts will output tables summarizing:

- **Framework:** The web framework and configuration tested.
- **#Reqs:** The total number of requests sent.
- **Success:** The number of successful requests out of the total.
- **Total s:** The total time taken in seconds to complete all requests.
- **Avg s/req:** The average time per request in seconds.

Lower `Total s` and `Avg s/req` generally indicate better performance.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs, feature requests, or improvements.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
