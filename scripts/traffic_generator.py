import os
import sys
import requests
import time
import random
import json
from datetime import datetime

# CONFIG
API_URL = os.getenv("API_URL","http://backend:8000/api/logs")
SERVICES = [
    "auth-service",
    "payment-api",
    "frontend-ui",
    "database-worker"
]

USER_AGENTS_NORMAL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0"
]

NORMAL_ENDPOINTS = [
    "/login", 
    "/home", 
    "/products", 
    "/checkout", 
    "/user/profile"
]

USER_AGENTS_ATTACK = [
    "sqlmap/1.7.2#stable (https://sqlmap.org)",
    "Nikto/2.1.6",
    "curl/7.88.1",
    # Tor signature
    "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0" 
]

ATTACK_PAYLOADS = [
    "/admin' OR '1'='1", 
    "/../../etc/passwd", 
    "<script>alert(1)</script>", 
    "/cgi-bin/php?cmd=ls"
]

NORMAL_MESSAGES = [
    "User action processed",
    "Payment verified",
    "Page load complete",
    "Database sync finished",
    "User logout success",
    "Session refreshed",
    "Health check OK"
]

#! public Tor exit node IPs for simulation
SAMPLE_TOR_IPS = ["185.220.101.5", "185.220.102.8", "51.15.43.205"]

def generate_log(is_attack=False):
    service = random.choice(SERVICES)
    
    if is_attack:
        #! Attack log
        level = "ERROR" if random.random() > 0.5 else "WARNING"
        status = random.choice([400, 401, 403, 404, 500])
        endpoint = random.choice(ATTACK_PAYLOADS)
        method = random.choice(["GET", "POST"])
        user_agent = random.choice(USER_AGENTS_ATTACK)
        client_ip = random.choice(SAMPLE_TOR_IPS) if random.random() > 0.5 else f"{random.randint(100,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        msg = f"Request error on {endpoint}"
    else:
        #! Normal log
        level = "INFO"
        status = random.choice([200, 201, 304])
        endpoint = random.choice(NORMAL_ENDPOINTS)
        method = "GET" if endpoint != "/login" and endpoint != "/checkout" else "POST"
        user_agent = random.choice(USER_AGENTS_NORMAL)
        client_ip = f"192.168.1.{random.randint(0,255)}"                
        msg = random.choice(NORMAL_MESSAGES)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "service": service,
        "level": level,
        "message": msg,
        "client_ip": client_ip,
        "method": method,
        "endpoint": endpoint,
        "user_agent": user_agent,
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
                    print("API??")
                time.sleep(0.1)
        else:
            # Normal traffic
            log = generate_log(is_attack=False)
            try:
                requests.post(API_URL, json=log)
                print(f" [NORMAL] Sent: {log['endpoint']}")
            except:
                print("API??")
            time.sleep(random.uniform(0.5, 2.0))

if __name__ == "__main__":
    main()