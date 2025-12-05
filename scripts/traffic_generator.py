import os
import sys
import requests
import time
import random
import json
from datetime import datetime

# CONFIG
API_URL = os.getenv("API_URL","http://backend:8000/api/logs")
SERVICES = ["auth-service", "payment-api", "frontend-ui", "database-worker"]
NORMAL_Endpoints = ["/login", "/home", "/products", "/checkout", "/user/profile"]
ATTACK_PAYLOADS = [
    "/admin' OR '1'='1", 
    "/../../etc/passwd", 
    "<script>alert(1)</script>", 
    "/cgi-bin/php?cmd=ls"
]

def generate_log(is_attack=False):
    service = random.choice(SERVICES)
    
    if is_attack:
        level = "ERROR" if random.random() > 0.5 else "WARNING"
        status = random.choice([401, 403, 404, 500])
        endpoint = random.choice(ATTACK_PAYLOADS)
        msg = f"Suspicious activity detected from IP {random.randint(100,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
    else:
        level = "INFO"
        status = random.choice([200, 201, 304])
        endpoint = random.choice(NORMAL_Endpoints)
        msg = f"User action processed successfully"

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "service": service,
        "level": level,
        "message": msg,
        "endpoint": endpoint,
        "status_code": status
    }

def main():
    if len(sys.argv) <= 1:
        return
    
    print(f" Traffic Generator started. Target: {API_URL}")
    while True:
        # 10% chance of a "burst" attack
        if random.random() < 0.1 and sys.argv[1] == "Attack":
            print("  SIMULATING ATTACK BURST!")
            for _ in range(20):
                log = generate_log(is_attack=True)
                try:
                    requests.post(API_URL, json=log)
                    print(f" [ATTACK] Sent: {log['endpoint']}")
                except:
                    print("API offline?")
                time.sleep(0.1)
        else:
            # Normal traffic
            log = generate_log(is_attack=False)
            try:
                requests.post(API_URL, json=log)
                print(f" [NORMAL] Sent: {log['endpoint']}")
            except:
                print("API offline?")
            time.sleep(random.uniform(0.5, 2.0))

if __name__ == "__main__":
    main()