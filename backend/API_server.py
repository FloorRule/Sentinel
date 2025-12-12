from fastapi import FastAPI, WebSocket
from sentinel import get_recent_logs, run_sentinel, get_stats, get_charts_data
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from wsManage import broadcast, connected_clients

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
    print("Received log:", log)
    result = await run_sentinel(log.model_dump())

    return {"result": result}


@app.websocket("/ws/dashboard")
async def dashboard_ws(ws: WebSocket):
    await ws.accept()
    connected_clients.append(ws)

    try:
        while True:
            await ws.receive_text()
    except:
        connected_clients.remove(ws)

