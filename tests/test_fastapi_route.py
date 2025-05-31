# tests/test_fastapi_route.py
import httpx
import subprocess, asyncio, os, signal, time # signal and time may not be needed if Popen is handled well
import pytest # For @pytest.mark.asyncio

# Adjusted to be an async function and use uvicorn
async def start_server_fastapi():
    # Ensure CWD is project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    # Command to run FastAPI app with uvicorn
    # Assuming app_fastapi/app.py and app instance is named 'app'
    cmd = ["uvicorn", "app_fastapi.app:app", "--host", "0.0.0.0", "--port", "8000"]
    
    proc = subprocess.Popen(
        cmd,
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    await asyncio.sleep(1.5) # Allow uvicorn to start
    return proc

@pytest.mark.asyncio
async def test_home_returns_html_fastapi():
    proc = await start_server_fastapi()
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("http://127.0.0.1:8000/") # Default FastAPI port
            assert r.status_code == 200
            assert "<h1>Slow FastAPI Demo</h1>" in r.text # Expected content
    finally:
        proc.terminate()
        try:
            # Use communicate to get output and ensure process is reaped
            stdout, stderr = proc.communicate(timeout=5)
            # print(f"FastAPI stdout:\n{stdout.decode(errors='replace')}") # Optional: for debugging
            # print(f"FastAPI stderr:\n{stderr.decode(errors='replace')}") # Optional: for debugging
        except subprocess.TimeoutExpired:
            print("FastAPI server did not terminate/communicate gracefully, killing.")
            proc.kill()
            proc.wait() # Ensure kill completes 