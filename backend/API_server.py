from fastapi import FastAPI
from sentinel import get_recent_logs, run_sentinel
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
def logAnalysis(log: LogEntry):
    print("Received log:", log)
    result = run_sentinel(log.model_dump())
    return {"status": "ok", "result": result}

@app.get("/api/logs")
def getLogAnalysis():
    return {"status": "ok", "result": get_recent_logs()}

