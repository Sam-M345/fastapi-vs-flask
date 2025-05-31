import httpx
import subprocess, time, os, signal

def start_server():
    # Ensure the Python interpreter can find the app_flask module.
    # This might require adjusting PYTHONPATH or running pytest from the project root.
    proc = subprocess.Popen(["python", "-m", "app_flask.app"]) # Removed cwd=".."
    time.sleep(1)  # Increased sleep to allow server startup, especially on slower systems
    return proc

def test_home_returns_html():
    proc = start_server()
    try:
        r = httpx.get("http://127.0.0.1:5000/", timeout=10)
        assert r.status_code == 200
        assert "Hello from Flask :)" in r.text  # Corrected assertion
    finally:
        # It's important to ensure the server process is terminated.
        # os.kill might not be cross-platform for SIGINT.
        # proc.terminate() followed by proc.wait() is generally safer.
        proc.terminate()
        try:
            proc.wait(timeout=5) # Wait for the process to terminate
        except subprocess.TimeoutExpired:
            proc.kill() # Force kill if terminate doesn't work
            proc.wait() # Wait for the kill to complete 