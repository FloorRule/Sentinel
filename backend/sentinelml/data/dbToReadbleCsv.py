import sqlite3
import csv

db_path = "../../sentinel3.db"
csv_path = "readble_logs.csv"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT timestamp, service, level, message, is_threat FROM logs
""")
rows = cursor.fetchall()

col_names = ["timestamp", "service", "level", "message", "is_threat"]

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(col_names)
    writer.writerows(rows)

conn.close()
print("CSV exported successfully!")
