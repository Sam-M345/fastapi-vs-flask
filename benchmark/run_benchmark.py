# benchmark/run_benchmark.py
import argparse
import time
import asyncio
import httpx
import requests
from concurrent.futures import ThreadPoolExecutor

# Server URLs (ensure these match your running servers)
FLASK_URL = "http://127.0.0.1:3000/"
FASTAPI_URL = "http://127.0.0.1:8000/"
NUM_REQUESTS = 100

def fetch_url_sync(url):
    try:
        response = requests.get(url) # REMOVED timeout=10
        response.raise_for_status() # Raise an exception for bad status codes
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Request to {url} failed: {e}")
        return None

def run_flask_benchmark():
    print(f"Starting Flask benchmark: {NUM_REQUESTS} requests to {FLASK_URL}...")
    start_time = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=NUM_REQUESTS) as executor:
        futures = [executor.submit(fetch_url_sync, FLASK_URL) for _ in range(NUM_REQUESTS)]
        results = [future.result() for future in futures]
    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    successful_requests = sum(1 for r in results if r == 200)
    print(f"Flask benchmark: {successful_requests}/{NUM_REQUESTS} successful requests in {total_time:.2f} seconds.")
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