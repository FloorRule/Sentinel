from fastapi import FastAPI
from sentinel import run_sentinel
from pydantic import BaseModel

app = FastAPI()

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

