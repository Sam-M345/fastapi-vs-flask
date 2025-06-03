# FastAPI vs Flask Performance Benchmark

This project provides a benchmarking suite to compare the performance of FastAPI and Flask web frameworks under various conditions, including scenarios with and without artificial delays.

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
├── Design Docs/              # (Placeholder for design documents)
├── project/                  # (Purpose to be clarified)
├── SOP/                      # Standard Operating Procedures & Handoff notes
├── static/                   # (Placeholder for static assets)
├── tests/                    # (Placeholder for automated tests)
├── .gitignore                # Files and directories ignored by Git
├── custom.css                # (Purpose to be clarified)
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── run_benchmark_NO_RESTRICTIONS.py # Runs benchmarks for no-delay apps
└── run_benchmark_table.py    # Runs benchmarks for apps with delays and generates a table
```

## Prerequisites

- Python 3.8+
- Git

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
