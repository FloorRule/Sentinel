import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from Redis.redis_client import get_redis, publish_event
from sentinel import get_recent_logs, run_sentinel, get_stats, get_charts_data
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from wsManage import broadcast, connected_clients

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
    endpoint: str
    status_code: int

@app.post("/api/logs")
async def logAnalysis(log: LogEntry):
    if(TEST_MODE): print("Received log:", log)

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


@app.websocket("/ws/dashboard")
async def dashboard_ws(ws: WebSocket):
    await ws.accept()
    redis = await get_redis()
    pubsub = redis.pubsub()

    await pubsub.subscribe("dashboard_updates")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                #  parse Redis data
                data = json.loads(message["data"])
                
                # Send Log to Frontend
                await ws.send_json({"type": "logs", "data": data["log"]})
                
                # Send Stats to Frontend
                await ws.send_json({"type": "stats", "data": data["stats"]})

                # Send Charts to Frontend
                await ws.send_json({"type": "chart-data", "data": data["charts"]})

    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        await pubsub.unsubscribe("dashboard_updates")
