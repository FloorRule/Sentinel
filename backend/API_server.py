import json
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from Redis.redis_client import get_redis, publish_event
from sentinel import get_recent_logs, run_sentinel, get_stats, get_charts_data
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

TEST_MODE = False

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LogEntry(BaseModel):
    timestamp: str
    service: str
    level: str
    message: str
    endpoint: str = "/"
    status_code: int = 200
    user_agent: str = "unknown"
    client_ip: str = "127.0.0.1"

@app.post("/api/logs")
async def logAnalysis(log: LogEntry):
    if TEST_MODE: 
        print("Received log:", log)

    result = await run_sentinel(log.model_dump())
    stats = await get_stats()
    charts = await get_charts_data()

    update_package = {
        "log": result,
        "stats": stats,
        "charts": charts
    }
    
    await publish_event("dashboard_updates", update_package)

    return {"result": result}

#! For initial page load
@app.get("/api/logs")
def fetch_recent_logs():
    return get_recent_logs()

@app.get("/api/stats")
async def fetch_stats():
    return await get_stats()

@app.get("/api/chart-data")
async def fetch_charts():
    return await get_charts_data()

#! WebSocket
@app.websocket("/ws/dashboard")
async def dashboard_ws(ws: WebSocket):
    await ws.accept()
    redis = await get_redis()
    pubsub = redis.pubsub()

    await pubsub.subscribe("dashboard_updates")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                #! Parse Redis event
                data = json.loads(message["data"])
                
                #! Stream to React frontend
                await ws.send_json({"type": "logs", "data": data["log"]})
                await ws.send_json({"type": "stats", "data": data["stats"]})
                await ws.send_json({"type": "chart-data", "data": data["charts"]})

    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        await pubsub.unsubscribe("dashboard_updates")