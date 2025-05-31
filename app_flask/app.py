from flask import Flask, Response
import time

app = Flask(__name__)

@app.route("/")
def home():
    time.sleep(3)                # simulate slow work
    html = "Hello from Flask :)"
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    app.run() 