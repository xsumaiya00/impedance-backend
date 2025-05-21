from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os

try:
    from idun_guardian_sdk import GuardianClient
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

app = FastAPI()

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your actual API token here
API_TOKEN = os.getenv("IDUN_API_TOKEN") or "idun_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJlMzcxZTg3MS01YWE0LTRlMWEtYTc3Yi02M2M1MmJiY2M0ODAiLCJkaWQiOiJGNy1EOS1BNi05OS1CQy1EOCJ9.XqrcIU2qg7c0ITzDQxD3jG8f7awtCSUHKbXrLtR6dlA"

client = GuardianClient(api_token=API_TOKEN) if SDK_AVAILABLE else None

# --- Impedance Stream (real or simulated) ---
async def impedance_stream():
    if SDK_AVAILABLE:
        await client.connect_device()
        async for data in client.stream_impedance():
            yield f"data: {json.dumps({'impedance': data})}\n\n"
            await asyncio.sleep(1)
    else:
        # Simulated fallback
        while True:
            fake_impedance = round(500 + 200 * (0.5 - asyncio.get_event_loop().time() % 1), 2)
            yield f"data: {json.dumps({'impedance': fake_impedance})}\n\n"
            await asyncio.sleep(1)

@app.get("/stream-impedance")
async def stream_impedance():
    return StreamingResponse(impedance_stream(), media_type="text/event-stream")

# --- EEG Stream (real or simulated) ---
async def eeg_stream():
    if SDK_AVAILABLE:
        await client.connect_device()
        async for sample in client.stream_eeg():
            yield f"data: {json.dumps({'eeg': sample})}\n\n"
            await asyncio.sleep(0.02)  # ~50 Hz
    else:
        # Simulated EEG values
        while True:
            simulated = [round(100 * (0.5 - asyncio.get_event_loop().time() % 1), 2) for _ in range(4)]
            yield f"data: {json.dumps({'eeg': simulated})}\n\n"
            await asyncio.sleep(0.02)

@app.get("/stream-eeg")
async def stream_eeg():
    return StreamingResponse(eeg_stream(), media_type="text/event-stream")

# --- Start Endpoint (for frontend trigger) ---
@app.get("/start-eeg-stream")
async def start_eeg_stream():
    return JSONResponse(content={"status": "EEG stream started"})

@app.get("/health")
async def health():
    return {"status": "ok", "sdk": SDK_AVAILABLE}
