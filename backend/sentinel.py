from math import floor
from pydantic import BaseModel
from db.init_db_script import get_connection
from sentinelml.ml.model import IsolationForestDetector
from wsManage import broadcast
from Redis.redis_client import cache_get, cache_set

TEST_MODE = False

detector = IsolationForestDetector()

class LogProccedEntry(BaseModel):
    timestamp: str
    service: str
    level: str
    message: str
    is_threat: bool

async def run_sentinel(log):
    if(TEST_MODE): print("Processing:", log)
    #is_threating = (log["level"] == "ERROR" or log["message"].find("SQL Injection") != -1);
    prediction = detector.predict_log(log)

    if(TEST_MODE): print(prediction["score"])
    is_threating = prediction["is_anomaly"]

    entry = LogProccedEntry(
        timestamp=log["timestamp"],
        service=log["service"],
        level=log["level"],
        message=log["message"],
        is_threat=is_threating
    )
    insert_log(entry.model_dump())

    return entry.model_dump()

def insert_log(log: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO logs (timestamp, service, level, message, is_threat)
        VALUES (?, ?, ?, ?, ?)
    """, (
        log["timestamp"],
        log["service"],
        log["level"],
        log["message"],
        log["is_threat"],
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
    result = [dict(zip(columns, row)) for row in rows]

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
    total_vol = cursor.fetchall()[0][0]

    cursor.execute("SELECT COUNT(*) FROM logs WHERE is_threat==true")
    threats_detected = cursor.fetchall()[0][0]
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