from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import datetime
import json
import os
import csv

try:
    from idun_guardian_sdk import GuardianClient
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_TOKEN = os.getenv("IDUN_API_TOKEN") or "idun_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJlMzcxZTg3MS01YWE0LTRlMWEtYTc3Yi02M2M1MmJiY2M0ODAiLCJkaWQiOiJGNy1EOS1BNi05OS1CQy1EOCJ9.XqrcIU2qg7c0ITzDQxD3jG8f7awtCSUHKbXrLtR6dlA"
client = GuardianClient(api_token=API_TOKEN) if SDK_AVAILABLE else None
eeg_data_store = []

# --- Impedance Stream ---
async def impedance_stream():
    if SDK_AVAILABLE:
        await client.connect_device()
        async for data in client.stream_impedance():
            yield f"data: {json.dumps({'impedance': data})}\n\n"
            await asyncio.sleep(1)
    else:
        while True:
            fake = round(500 + 200 * (0.5 - asyncio.get_event_loop().time() % 1), 2)
            yield f"data: {json.dumps({'impedance': fake})}\n\n"
            await asyncio.sleep(1)

@app.get("/stream-impedance")
async def stream_impedance():
    return StreamingResponse(impedance_stream(), media_type="text/event-stream")

# --- EEG Stream + Store in memory ---
async def eeg_stream():
    global eeg_data_store
    eeg_data_store = []

    if SDK_AVAILABLE:
        await client.connect_device()

        async for sample in client.stream_eeg():
            timestamp = datetime.datetime.now().isoformat()
            eeg_data_store.append({"timestamp": timestamp, "data": sample.samples})
            yield f"data: {json.dumps({'eeg': sample.samples})}\n\n"
            await asyncio.sleep(0.02)
    else:
        while True:
            simulated = [round(100 * (0.5 - asyncio.get_event_loop().time() % 1), 2) for _ in range(4)]
            timestamp = datetime.datetime.now().isoformat()
            eeg_data_store.append({"timestamp": timestamp, "data": simulated})
            yield f"data: {json.dumps({'eeg': simulated})}\n\n"
            await asyncio.sleep(0.02)

@app.get("/stream-eeg")
async def stream_eeg():
    return StreamingResponse(eeg_stream(), media_type="text/event-stream")

# --- Start EEG trigger ---
@app.get("/start-eeg-stream")
async def start_eeg_stream():
    return JSONResponse(content={"status": "EEG stream started"})

# --- Stop and Save EEG to CSV ---
@app.get("/stop-and-save-eeg")
async def stop_and_save_eeg():
    global eeg_data_store

    try:
        if SDK_AVAILABLE:
            await client.disconnect()

        filename = f"eeg_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        os.makedirs("data", exist_ok=True)
        filepath = os.path.join("data", filename)

        with open(filepath, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "sample1", "sample2", "sample3", "sample4"])
            for entry in eeg_data_store:
                row = [entry["timestamp"]] + entry["data"]
                writer.writerow(row)

        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="text/csv"
        )

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health():
    return {"status": "ok", "sdk": SDK_AVAILABLE}
