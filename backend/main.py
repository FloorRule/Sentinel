import threading
import time
import uvicorn
from API_server import app
from db.init_db_script import init_db

def start_fastapi():
    init_db()
    uvicorn.run(app, host="127.0.0.1", port=8000)

# Start threads
threading.Thread(target=start_fastapi, daemon=True).start()

print("Sentinel + FastAPI are running...")

while True:
    time.sleep(1)
