
# Sentinel

A lightweight, real-time log ingestion and threat monitoring dashboard. 

Sentinel ingests HTTP server events via an asynchronous FastAPI pipeline, runs baseline anomaly detection in the background, and streams flagged events to a React dashboard over WebSockets.



https://github.com/user-attachments/assets/7da93f78-06b4-4ecf-8c12-838a6b33ea8d



---

## Architecture

```bash
[ Log Source / Traffic Script ]
        │  (HTTP POST /api/logs)
        ▼
[ FastAPI Ingestion ]
        │
        ▼  (Redis Queue / PubSub)
[ Processing Worker ] ──> [ Isolation Forest Anomaly Detection ]
        │
        ▼  (WebSocket Broadcast)
[ React + Shadcn Dashboard ]
```

1. **Ingestion Layer (`FastAPI`):** Non-blocking HTTP endpoints that accept structured log payloads and offload them to Redis to prevent request bottlenecks.
2. **Buffer / Broker (`Redis`):** Decouples log ingestion from ML scoring and client broadcasting.
3. **Detection Worker:** Evaluates incoming request characteristics (response codes, payload anomalies, request frequency) using scikit-learn's `IsolationForest`.
4. **Live UI (`React`, `TypeScript`, `Tailwind`, `Recharts`):** Subscribes to the WebSocket feed to graph live throughput, calculate moving error rates, and display an inspectable triage table.

---

## Tech Stack

* **Backend:** Python 3.11+, FastAPI, Uvicorn, Redis-py, Scikit-learn
* **Frontend:** React, TypeScript, Vite, Tailwind CSS, Shadcn UI, Recharts
* **Infrastructure:** Docker, Docker Compose, Redis

---

## Getting Started

### Prerequisites
* [Docker Desktop](https://www.docker.com/) installed and running.

### Option 1: Docker Compose (Recommended)

Spins up the Backend, Redis broker, Frontend, and synthetic Traffic Generator in one command:

```bash
docker compose up --build
```

* **Dashboard UI:** `http://localhost:5173`
* **FastAPI Docs:** `http://localhost:8000/docs`

---

### Option 2: Local Development Setup

If you want to run services locally without Docker:

#### 1. Start Redis
Make sure a local Redis instance is running on port `6379`:
```bash
# Via WSL / Linux
sudo service redis-server start

# Or standalone Docker
docker run -d -p 6379:6379 redis:alpine
```

#### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

#### 3. Frontend Setup
```bash
cd frontend/sentinel-ui
npm install
npm run dev
```

#### 4. Simulate Log Traffic
To test the pipeline with a mix of organic requests and attack signatures:
```bash
cd scripts
python traffic_generator.py
```

---

## Log Event Schema

Logs are ingested via `POST /api/logs` using the following schema:

```json
{
  "service": "auth-service",
  "status_code": 401,
  "message": "Failed login attempt from IP 192.168.1.45",
  "timestamp": "2026-09-10T11:00:00Z"
}
```

Flagged events broadcast over `ws://localhost:8000/ws/dashboard` include enriched threat telemetry:

```json
{
  "id": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
  "timestamp": "2026-09-10T11:00:00Z",
  "service": "auth-service",
  "level": "CRITICAL",
  "message": "Potential credential stuffing detected",
  "statusCode": 401,
  "is_threat": true
}
```

---

## Planned Improvements

- [ ] **Detection Rules:** Add rule-based pattern matching (SQLi, Path Traversal regex, Sigma signatures) alongside the ML model to reduce false positives.
- [ ] **Stream Reliability:** Migrate from Redis Pub/Sub to Redis Streams with consumer groups for persistent message replay.
- [ ] **Real Log Collectors:** Replace the mock script with a Fluentbit / Filebeat collector parsing live Nginx logs.
