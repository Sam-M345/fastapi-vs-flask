from flask import Flask, Response
import time
import webbrowser

app = Flask(__name__)

@app.route("/")
def home():
    time.sleep(3)                # simulate slow work
    html = "<h1>Slow Flask Demo</h1>" # TDD Phase 2 content
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 3000
    url = f"http://{host}:{port}/"
    
    # Open the URL in a new browser tab
    webbrowser.open_new_tab(url)
    
    app.run(host="0.0.0.0", port=3000) 