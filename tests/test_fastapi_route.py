# tests/test_fastapi_route.py
import httpx
import asyncio
import pytest # For @pytest.mark.asyncio
import uvicorn
import threading
import time
from multiprocessing import Process # Using Process for better isolation
import os

# Server configuration
HOST = "127.0.0.1"
PORT = 8000

class UvicornServer(threading.Thread):
    def __init__(self, app_module_str):
        super().__init__(daemon=True)
        self.app_module_str = app_module_str
        self.server_started = threading.Event()
        self.config = uvicorn.Config(app_module_str, host=HOST, port=PORT, log_level="info")
        self.server = uvicorn.Server(config=self.config)

    def run(self):
        # Need to set a new event loop for the thread if running asyncio components
        # For uvicorn.Server.serve(), it typically manages its own loop or integrates
        # with an existing one if started from an async context. 
        # However, running it in a separate thread needs care.
        # Simpler: uvicorn.run() which handles loop creation.
        uvicorn.run(self.app_module_str, host=HOST, port=PORT, log_level="warning") # log_level warning to reduce noise

    # UvicornServer using Process for cleaner start/stop
    # This might be more robust for test isolation.

def run_server_process(app_module_str, host, port, project_root_dir):
    # Add project root to Python path for the new process
    import sys
    sys.path.insert(0, project_root_dir)
    uvicorn.run(app_module_str, host=host, port=port, log_level="warning")

async def start_server_fastapi():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    # Using Process to run Uvicorn. This provides better isolation and cleanup.
    proc = Process(target=run_server_process, args=("app_fastapi.app:app", HOST, PORT, project_root), daemon=True)
    proc.start()
    await asyncio.sleep(2.0) # Increased sleep to ensure server is fully up
    if not proc.is_alive():
        raise RuntimeError("FastAPI server process failed to start.")
    return proc # Return the process object

@pytest.mark.asyncio
async def test_home_returns_html_fastapi():
    server_process = await start_server_fastapi()
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"http://{HOST}:{PORT}/")
            assert r.status_code == 200
            assert "<h1>FastAPI Server: 3-Seconds Artificial Delay Demo</h1>" in r.text # Expected content
    finally:
        if server_process and server_process.is_alive():
            server_process.terminate() # Send SIGTERM
            server_process.join(timeout=5) # Wait for termination
            if server_process.is_alive(): # Still alive after timeout
                print("FastAPI server process did not terminate gracefully, killing.")
                server_process.kill() # Force kill
                server_process.join(timeout=5) # Wait for kill
            # print("FastAPI server process stopped.") # Optional debug 