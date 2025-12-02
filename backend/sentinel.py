
from pydantic import BaseModel
from db.init_db_script import get_connection

class LogProccedEntry(BaseModel):
    timestamp: str
    service: str
    level: str
    message: str
    is_threat: bool

def run_sentinel(log):
    print("Processing:", log)
    is_threating = (log["level"] == "ERROR" or log["message"].find("SQL Injection") != -1);

    entry = LogProccedEntry(
        timestamp=log["timestamp"],
        service=log["service"],
        level=log["level"],
        message=log["message"],
        is_threat=is_threating
    )
    insert_log(entry.model_dump())

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

def get_recent_logs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 50")
    rows = cursor.fetchall()

    columns = [col[0] for col in cursor.description]
    result = [dict(zip(columns, row)) for row in rows]

    conn.close()
    return result
