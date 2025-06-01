# app_fastapi/app.py
from fastapi import FastAPI, Response
import asyncio

app = FastAPI()

@app.get("/")
async def home():
    await asyncio.sleep(3)  # simulate slow work (non-blocking)
    html = "<h1>FastAPI Server: 3-Seconds Artificial Delay Demo</h1>"
    return Response(content=html, media_type="text/html") 