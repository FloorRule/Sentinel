from math import floor
from pydantic import BaseModel
from db.init_db_script import get_connection
from sentinelml.ml.model import IsolationForestDetector
from wsManage import broadcast

detector = IsolationForestDetector()

class LogProccedEntry(BaseModel):
    timestamp: str
    service: str
    level: str
    message: str
    is_threat: bool

async def run_sentinel(log):
    print("Processing:", log)
    #is_threating = (log["level"] == "ERROR" or log["message"].find("SQL Injection") != -1);
    prediction = detector.predict_log(log)
    print(prediction["score"])
    is_threating = prediction["is_anomaly"]

    entry = LogProccedEntry(
        timestamp=log["timestamp"],
        service=log["service"],
        level=log["level"],
        message=log["message"],
        is_threat=is_threating
    )
    insert_log(entry.model_dump())

    await broadcast("logs", entry.model_dump())
    await broadcast("stats", get_stats())
    await broadcast("chart-data", get_charts_data())
    return "done"

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
def get_stats():
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
    return result_dict

# api/chart-data
def get_charts_data():
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

    return result