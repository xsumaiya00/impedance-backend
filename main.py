from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from idun_guardian_sdk import GuardianClient
import asyncio
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = GuardianClient(api_token="idun_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJlMzcxZTg3MS01YWE0LTRlMWEtYTc3Yi02M2M1MmJiY2M0ODAiLCJkaWQiOiJGNy1EOS1BNi05OS1CQy1EOCJ9.XqrcIU2qg7c0ITzDQxD3jG8f7awtCSUHKbXrLtR6dlA")

async def impedance_stream():
    await client.connect_device()
    async for data in client.stream_impedance():
        payload = json.dumps({"impedance": data})
        yield f"data: {payload}\n\n"
        await asyncio.sleep(1)

@app.get("/stream-impedance")
async def stream_impedance():
    return StreamingResponse(impedance_stream(), media_type="text/event-stream")
