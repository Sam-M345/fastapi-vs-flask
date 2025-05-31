import httpx
import subprocess, time, os, signal

def start_server():
    # Ensure the path to app_flask.app is correct if run from project/tests/
    # Assuming app_flask is a module in the parent directory of 'tests' when running pytest from 'project'
    # Or, if running pytest from workspace root, it might need to be "project.app_flask.app"
    # For now, let's assume pytest is run from the root and adjust if needed.
    # The TDD uses "app_flask.app", which implies the app_flask directory is on PYTHONPATH
    # or the command is run from a directory where 'app_flask' is a subdir.
    # Let's adjust the command to be more robust from the workspace root.
    proc = subprocess.Popen(["python", "-m", "project.app_flask.app"])
    time.sleep(0.2)  # allow startup
    return proc

def test_home_returns_html():
    proc = start_server()
    try:
        r = httpx.get("http://127.0.0.1:5000/", timeout=10)
        assert r.status_code == 200
        assert "Slow Flask Demo" in r.text
    finally:
        # On Windows, os.kill with SIGINT might not work as expected for subprocess.Popen.
        # proc.terminate() or proc.send_signal(signal.CTRL_C_EVENT) might be more reliable.
        # For now, sticking to TDD, but we might need to adjust this.
        if os.name == 'nt': # Windows
            proc.send_signal(signal.CTRL_C_EVENT)
            # Or use taskkill
            # subprocess.run(f"taskkill /F /PID {proc.pid} /T", check=True, shell=True)
        else: # POSIX
            os.kill(proc.pid, signal.SIGINT)
        proc.wait(timeout=5) # Wait for process to terminate 