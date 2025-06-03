# app_fastapi/app_no_delay.py
from fastapi import FastAPI, Response
# import asyncio # No longer needed for sleep

app = FastAPI()

@app.get("/")
async def home():
    # await asyncio.sleep(0.3) # Removed delay
    html = "<h1>FastAPI Server: No Artificial Delay</h1>"
    return Response(content=html, media_type="text/html")

# To run this app (for testing): uvicorn app_fastapi.app_no_delay:app --reload --port 8000 