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
# NUM_REQUESTS = 100 # Removed, will be passed as argument

def fetch_url_sync(url):
    try:
        response = requests.get(url, timeout=10) # Increased timeout for potentially more requests
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        # print(f"Request to {url} failed: {e}") # Silenced for cleaner benchmark output
        return None

def run_flask_benchmark(num_requests):
    print(f"Starting Flask benchmark: {num_requests} requests to {FLASK_URL}...")
    # print("[DIAG-BRB-FLASK] Running requests SEQUENTIALLY for diagnosis.", flush=True) # Can be verbose
    start_time = time.perf_counter()
    
    results_list = []
    # successful_so_far = 0 # Not strictly needed here

    for i in range(num_requests):
        try:
            status_code = fetch_url_sync(FLASK_URL)
            print(f"REQ_STATUS:{status_code}", flush=True) # Progress for the calling script to count
            results_list.append(status_code)
            # if status_code == 200:
            #     successful_so_far += 1
            # print(f"[DIAG-BRB-FLASK] Request {i+1}/{num_requests} result: {status_code}", flush=True)
        except Exception as e:
            # print(f"[DIAG-BRB-FLASK] Request {i+1}/{num_requests} failed with exception: {e}", flush=True)
            results_list.append(None)

    end_time = time.perf_counter()
    total_time = end_time - start_time
    successful_requests = sum(1 for r in results_list if r == 200)
    print(f"Final Flask benchmark summary: {successful_requests}/{num_requests} successful requests in {total_time:.2f} seconds.")
    return total_time

async def fetch_url_async(client, url):
    try:
        response = await client.get(url, timeout=20) # Increased timeout from 10 to 20 seconds
        response.raise_for_status()
        return response.status_code
    except httpx.RequestError as e:
        # More verbose error printing
        print(f"Request to {url} failed. Type: {type(e)}, Str: {str(e)}, Repr: {repr(e)}", flush=True)
        return None

async def run_fastapi_benchmark_async(num_requests):
    print(f"Starting FastAPI benchmark: {num_requests} requests to {FASTAPI_URL}...")
    start_time = time.perf_counter()
    results_list = [] # To store results for final count
    
    # Configure httpx limits
    limits = httpx.Limits(max_connections=500, max_keepalive_connections=50)
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = [fetch_url_async(client, FASTAPI_URL) for _ in range(num_requests)]
        
        completed_count = 0
        for i, task_future in enumerate(asyncio.as_completed(tasks)):
            try:
                result = await task_future
                results_list.append(result)
            except Exception as e:
                # print(f"FASTAPI_TASK_ERROR: Task {i+1} failed with {e}", flush=True) # Optional: log task errors
                results_list.append(None) # Mark as failed
            finally:
                completed_count += 1
                print(f"REQ_STATUS:FASTAPI_TASK_COMPLETED_{completed_count}", flush=True)
    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    successful_requests = sum(1 for r in results_list if r == 200)
    print(f"FastAPI benchmark: {successful_requests}/{num_requests} successful requests in {total_time:.2f} seconds.")
    return total_time

def run_fastapi_benchmark(num_requests):
    return asyncio.run(run_fastapi_benchmark_async(num_requests))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run web server benchmarks.")
    parser.add_argument(
        "framework", 
        choices=["flask", "fastapi"], 
        help="Specify the framework to benchmark (flask or fastapi)"
    )
    parser.add_argument(
        "num_requests",
        type=int,
        help="Number of requests to perform"
    )
    args = parser.parse_args()

    if args.framework == "flask":
        run_flask_benchmark(args.num_requests)
    elif args.framework == "fastapi":
        run_fastapi_benchmark(args.num_requests)
    else:
        print("Invalid framework specified. Choose 'flask' or 'fastapi'.") 