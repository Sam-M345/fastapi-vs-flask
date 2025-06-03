# app_fastapi/app.py
from fastapi import FastAPI, Response
import asyncio

app = FastAPI()

@app.get("/")
async def home():
    await asyncio.sleep(0.3)  # simulate slow work (non-blocking, changed from 3s to 0.3s)
    html = "<h1>FastAPI Server: 0.3-Seconds Artificial Delay Demo</h1>"
    return Response(content=html, media_type="text/html") 