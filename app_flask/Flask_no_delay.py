from flask import Flask, Response
# import time # No longer needed for sleep
# import webbrowser # Not needed here
from datetime import datetime

app = Flask(__name__)

request_counter = 0

@app.route("/")
def home():
    global request_counter
    request_id = request_counter + 1
    request_counter = request_id

    start_time = datetime.now()
    # print(f"[Flask No-Delay Server] Request {request_id} received at {start_time.strftime('%Y-%m-%d %H:%M:%S.%f')}") # Optional: keep for debugging if needed
    
    # time.sleep(0.3) # Removed delay
    
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    # print(f"[Flask No-Delay Server] Request {request_id} finishing at {end_time.strftime('%Y-%m-%d %H:%M:%S.%f')}, processed in {processing_time:.2f}s") # Optional
    
    html = f"<h1>Flask Server (No Delay, Threaded): Request {request_id} processed in {processing_time:.6f}s</h1>"
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    print("[Flask No-Delay Server] Starting server on http://127.0.0.1:3000...")
    # Running with threaded=True to allow Werkzeug to handle requests concurrently
    app.run(host="0.0.0.0", port=3000, threaded=True)

# To run this app (for testing): python app_flask/flask_application_no_delay.py 