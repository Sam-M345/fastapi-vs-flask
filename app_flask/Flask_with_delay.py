from flask import Flask, Response
import time
import webbrowser
from datetime import datetime # Added for timestamping
import logging # Added import

app = Flask(__name__)

# Disable Werkzeug's default logger
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

request_counter = 0 # Global counter

@app.route("/")
def home():
    global request_counter
    request_id = request_counter + 1
    request_counter = request_id

    start_time = datetime.now()
    # print(f"[Flask Server] Request {request_id} received at {start_time.strftime('%Y-%m-%d %H:%M:%S.%f')}") # Removed this line
    
    time.sleep(0.3)                # simulate slow work
    
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    print(f"[Flask Server] Request {request_id} processed in {processing_time:.2f}s - OK") # Kept and simplified this line, and added - OK
    
    html = f"<h1>Flask Server: Request {request_id} processed in {processing_time:.2f}s</h1>" # Updated content
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    print("[Flask Server] Starting server on http://127.0.0.1:3000...")
    # host = "127.0.0.1" # Not strictly needed for app.run with 0.0.0.0
    # port = 3000       # Port is defined in app.run
    # url = f"http://{host}:{port}/" # Not needed as webbrowser call is removed
    
    # Open the URL in a new browser tab # THIS LINE WILL BE REMOVED
    # webbrowser.open_new_tab(url) # REMOVED
    
    app.run(host="0.0.0.0", port=3000, threaded=False) # Port 3000, explicitly single-threaded 