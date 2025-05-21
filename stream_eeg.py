from idun_guardian_sdk import GuardianClient
import asyncio

client = GuardianClient(api_token="idun_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJlMzcxZTg3MS01YWE0LTRlMWEtYTc3Yi02M2M1MmJiY2M0ODAiLCJkaWQiOiJGNy1EOS1BNi05OS1CQy1EOCJ9.XqrcIU2qg7c0ITzDQxD3jG8f7awtCSUHKbXrLtR6dlA")

def handle_impedance(data):
    print(f"Impedance: {data} Ohm")

async def stream_impedance():
    await client.connect_device()
    await client.stream_impedance(handler=handle_impedance)

asyncio.run(stream_impedance())
