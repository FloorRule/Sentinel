import json
from math import floor
from typing import List
from pydantic import BaseModel
from db.init_db_script import get_connection
from wsManage import broadcast
from Redis.redis_client import cache_get, cache_set
from multi_detector import MultiDetector

TEST_MODE = False
TRAIN_MODE = False

detector = None if TRAIN_MODE else MultiDetector()

class LogProccedEntry(BaseModel):
    timestamp: str
    service: str
    level: str
    message: str
    endpoint: str = "/"
    status_code: int = 200
    user_agent: str = "unknown"
    client_ip: str = "127.0.0.1"
    is_threat: bool = False
    risk_score: float = 0.0
    severity: str = "INFO"
    tags: List[str]
    reasons: List[str]

async def run_sentinel(log):
    if(TEST_MODE): print("Processing:", log)

    if not TRAIN_MODE and detector is not None:
        prediction = detector.analyze(log)
    else:
        #! Clean result
        prediction = {
            "is_threat": False,
            "risk_score": 0.0,
            "severity": "INFO",
            "tags": [],
            "reasons": []
        }

    if(TEST_MODE): print(prediction["score"])

    entry = LogProccedEntry(
        timestamp = log["timestamp"],
        service = log["service"],
        level = log["level"],
        message = log["message"],
        endpoint = log["endpoint"],
        status_code = log["status_code"],
        is_threat = prediction["is_threat"],
        client_ip = log["client_ip"],
        risk_score = prediction["risk_score"],
        severity = prediction["severity"],
        tags = prediction["tags"],
        reasons = prediction["reasons"]
    )
    entry_data = entry.model_dump()
    insert_log(entry_data)

    return entry_data

def insert_log(log: dict):
    conn = get_connection()
    cursor = conn.cursor()

    tags_json = json.dumps(log.get("tags", []))
    reasons_json = json.dumps(log.get("reasons", []))

    cursor.execute("""
        INSERT INTO logs(
            timestamp, service, level, message,
            endpoint, status_code, user_agent, client_ip,
            is_threat, risk_score, severity, tags, reasons
            )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        log.get("timestamp"),
        log.get("service"),
        log.get("level"),
        log.get("message"),
        log.get("endpoint", "/"),
        log.get("status_code", 200),
        log.get("user_agent", "unknown"),
        log.get("client_ip", "127.0.0.1"),
        1 if log.get("is_threat") else 0,
        log.get("risk_score", 0.0),
        log.get("severity", "INFO"),
        tags_json,
        reasons_json
    ))

    conn.commit()
    conn.close()

# api/logs
def get_recent_logs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 50")
    rows = cursor.fetchall()

    columns = [col[0] for col in cursor.description]
    result = []

    for row in rows:
        dictRepresent = dict(zip(columns, row))

        if "tags" in dictRepresent:
            try: 
                dictRepresent["tags"] = json.loads(dictRepresent["tags"])
            except: 
                dictRepresent["tags"] = []

        if "reasons" in dictRepresent:
            try: 
                dictRepresent["reasons"] = json.loads(dictRepresent["reasons"])
            except: 
                dictRepresent["reasons"] = []
        result.append(dictRepresent)

    conn.close()
    return result

# api/stats
async def get_stats():
    # check Redis first
    cached_stats = await cache_get("dashboard_stats")
    if cached_stats:
        return cached_stats
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM logs")
    total_vol = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM logs WHERE is_threat = 1")
    threats_detected = cursor.fetchone()[0]

    if total_vol == 0:
        error_rate = 0
    else:
        error_rate = floor((threats_detected/total_vol)*100)

    result_dict = {"total_vol":total_vol, "threats_detected":threats_detected, "error_rate": error_rate}
    conn.close()

    # save to Redis
    await cache_set("dashboard_stats", result_dict, expire=2)
    return result_dict

# api/chart-data
async def get_charts_data():
    # check Redis first
    cached_charts = await cache_get("dashboard_charts")
    if cached_charts:
        return cached_charts

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            SUBSTR(timestamp, 1, 19) AS time_bucket, 
            SUM(CASE WHEN is_threat = 1 THEN 1 ELSE 0 END) AS error,
            SUM(CASE WHEN is_threat = 0 THEN 1 ELSE 0 END) AS success
        FROM logs
        GROUP BY time_bucket
        ORDER BY time_bucket ASC;
        """)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        timestamp, error, success = row
        result.append({
            "time": timestamp, 
            "error": error,
            "success": success
        })

    # save to Redis
    await cache_set("dashboard_charts", result, expire=2)
    return result