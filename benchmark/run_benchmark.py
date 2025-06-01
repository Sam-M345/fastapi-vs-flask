# benchmark/run_benchmark.py
import argparse
import time
import asyncio
import httpx
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys # Added for sys.stdout.flush()

# Server URLs (ensure these match your running servers)
FLASK_URL = "http://127.0.0.1:3000/"
FASTAPI_URL = "http://127.0.0.1:8000/"
NUM_REQUESTS = 100

def fetch_url_sync(url):
    try:
        response = requests.get(url, timeout=5) # Added timeout to prevent hanging
        response.raise_for_status() # Raise an exception for bad status codes
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Request to {url} failed: {e}")
        return None

def run_flask_benchmark():
    print(f"Starting Flask benchmark: {NUM_REQUESTS} requests to {FLASK_URL}...")
    print("[DIAG-BRB-FLASK] Running requests SEQUENTIALLY for diagnosis.", flush=True)
    start_time = time.perf_counter()
    
    results_list = []
    successful_so_far = 0

    for i in range(NUM_REQUESTS):
        print(f"[DIAG-BRB-FLASK] Processing request {i+1}/{NUM_REQUESTS}", flush=True)
        try:
            status_code = fetch_url_sync(FLASK_URL) # Direct call
            results_list.append(status_code)
            if status_code == 200:
                successful_so_far += 1
            print(f"[DIAG-BRB-FLASK] Request {i+1} result: {status_code}", flush=True)
        except Exception as e:
            print(f"[DIAG-BRB-FLASK] Request {i+1} generated an exception: {e}", flush=True)
            results_list.append(None)

        if (i + 1) % 10 == 0 and (i + 1) < NUM_REQUESTS:
            print(f"Flask progress: Handled {i+1}/{NUM_REQUESTS} requests... ({successful_so_far} successful so far)")
            sys.stdout.flush()
    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    successful_requests = sum(1 for r in results_list if r == 200)
    print(f"Final Flask benchmark summary: {successful_requests}/{NUM_REQUESTS} successful requests in {total_time:.2f} seconds.")
    return total_time

async def fetch_url_async(client, url):
    try:
        response = await client.get(url) # REMOVED timeout=10
        response.raise_for_status()
        return response.status_code
    except httpx.RequestError as e:
        print(f"Request to {url} failed: {e}")
        return None

async def run_fastapi_benchmark_async():
    print(f"Starting FastAPI benchmark: {NUM_REQUESTS} requests to {FASTAPI_URL}...")
    start_time = time.perf_counter()
    
    async with httpx.AsyncClient() as client:
        tasks = [fetch_url_async(client, FASTAPI_URL) for _ in range(NUM_REQUESTS)]
        results = await asyncio.gather(*tasks)
    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    successful_requests = sum(1 for r in results if r == 200)
    print(f"FastAPI benchmark: {successful_requests}/{NUM_REQUESTS} successful requests in {total_time:.2f} seconds.")
    return total_time

def run_fastapi_benchmark():
    return asyncio.run(run_fastapi_benchmark_async())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run web server benchmarks.")
    parser.add_argument(
        "framework", 
        choices=["flask", "fastapi"], 
        help="Specify the framework to benchmark (flask or fastapi)"
    )
    args = parser.parse_args()

    if args.framework == "flask":
        run_flask_benchmark()
    elif args.framework == "fastapi":
        run_fastapi_benchmark()
    else:
        print("Invalid framework specified. Choose 'flask' or 'fastapi'.") 