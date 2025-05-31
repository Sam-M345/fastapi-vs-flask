import httpx
import subprocess, time, os, signal

def start_server():
    current_env = os.environ.copy()
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    script_path = os.path.join(project_root, "app_flask", "flask_application.py")
    proc = subprocess.Popen(
        ["python", script_path],
        env=current_env,
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(1.5)
    return proc

def test_home_returns_html():
    proc = start_server()
    server_stdout_data = b""
    server_stderr_data = b""
    try:
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        r = httpx.get("http://127.0.0.1:3000/", timeout=10, headers=headers)
        assert r.status_code == 200
        assert "<h1>Slow Flask Demo</h1>" in r.text
    finally:
        proc.terminate()
        try:
            stdout_bytes, stderr_bytes = proc.communicate(timeout=5)
            server_stdout_data = stdout_bytes
            server_stderr_data = stderr_bytes
        except subprocess.TimeoutExpired:
            print("Server did not terminate/communicate gracefully, killing.")
            proc.kill()
            try:
                stdout_bytes, stderr_bytes = proc.communicate(timeout=1)
                server_stdout_data = stdout_bytes
                server_stderr_data = stderr_bytes
            except subprocess.TimeoutExpired:
                print("Could not get output even after kill.")
        
        # Keep these for CI logs or if needed later, but they will be empty if flask app is quiet.
        # print(f"Server stdout captured:\n{server_stdout_data.decode(errors='replace')}")
        # print(f"Server stderr captured:\n{server_stderr_data.decode(errors='replace')}") 