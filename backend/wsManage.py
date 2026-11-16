from typing import List
from fastapi import WebSocket

connected_clients: List[WebSocket] = []

async def broadcast(event_type, data):
    message = {"type": event_type, "data": data}
    for ws in connected_clients:
        await ws.send_json(message)
