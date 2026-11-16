import sqlite3
import csv

db_path = "../../sentinel4.db"
csv_path = "training_logs.csv"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT timestamp, service, level, message, 
        endpoint, status_code, user_agent, client_ip FROM logs WHERE is_threat = 0
""")
rows = cursor.fetchall()

col_names = [
    "timestamp", "service", "level", "message", 
    "endpoint", "status_code", "user_agent", "client_ip"
]

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(col_names)
    writer.writerows(rows)

conn.close()
print("[] CSV exported successfully!")
