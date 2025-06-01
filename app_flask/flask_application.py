from flask import Flask, Response
import time
import webbrowser

app = Flask(__name__)

@app.route("/")
def home():
    time.sleep(3)                # simulate slow work
    html = "<h1>Flask Server: 3s Artificial Delay Demo</h1>" # Updated content
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    # host = "127.0.0.1" # Not strictly needed for app.run with 0.0.0.0
    # port = 3000       # Port is defined in app.run
    # url = f"http://{host}:{port}/" # Not needed as webbrowser call is removed
    
    # Open the URL in a new browser tab # THIS LINE WILL BE REMOVED
    # webbrowser.open_new_tab(url) # REMOVED
    
    app.run(host="0.0.0.0", port=3000) # Port 3000 