# Sentinel

**Real-Time SIEM & Log Analysis Platform**

Sentinel is a **Cyber-SaaS dashboard** designed to visualize, analyze, and flag high-throughput server traffic in real-time. It ingests events via a high-performance Python API, queues them to prevent blocking, processes them using Machine Learning for threat detection, and streams live updates to a React client.

https://github.com/user-attachments/assets/dea9ec61-f66b-4253-94a0-1b08c6ad3265

---

## Overview

The system allows administrators to monitor network traffic as it happens. The architecture is decoupled into a high-speed ingestion layer and a reactive visualization layer:

*   **Ingestion:** High-performance API that accepts logs without blocking.
*   **Processing:** Asynchronous background workers analyze logs for security threats.
*   **Storage:** Persistent storage of traffic history.
*   **Streaming:** Sub-second data delivery to the frontend via WebSockets.

---

## Features

### Implemented

*   **Real-Time Dashboard:** Live visualization of traffic spikes and HTTP status distributions using Recharts.
*   **Anomaly Detection:** Unsupervised Machine Learning (`Isolation Forest`) to automatically flag suspicious behavior.
*   **High-Throughput Ingestion:** FastAPI backend capable of handling concurrent log streams.
*   **Non-Blocking Queue:** Redis implementation to buffer bursts of traffic.
*   **Live Alerts:** Instant visual feedback when threats (SQLi, DDOS) are detected.
*   **Traffic Simulation:** Includes a Python script to generate realistic organic vs. malicious traffic patterns.

### Roadmap

*   JWT Authentication for analyst access.
*   Containerization via Docker Compose.
*   Historical data export (CSV/JSON).

---

## Backend (Python/FastAPI)

The backend handles the data pipeline, consisting of three main components:

1.  **API Gateway (`FastAPI`):** Accepts `POST` requests and pushes data to Redis.
2.  **ML Worker:** Pulls logs from the queue, runs the `IsolationForest` model, and scores the threat level.
3.  **WebSocket Manager:** Pushes processed data to connected clients.

### Threat Detection Logic
The system analyzes incoming logs based on status codes and message patterns.

```python
# Simplified Anomaly Logic
if model.predict([log_features]) == -1:
    log.is_threat = True
    log.severity = "CRITICAL"
```

---

## Frontend (React + TypeScript)

The dashboard (`/frontend`) is built for data density and performance.

*   **UI Library:** Shadcn/UI + Tailwind CSS for a professional, "dark mode" enterprise look.
*   **State Management:** React Hooks manage the WebSocket connection state.
*   **Visualization:** Recharts for rendering time-series data without rendering lag.

It connects to the backend via a persistent WebSocket:

```typescript
const ws = new WebSocket("ws://localhost:8000/ws/logs");

ws.onmessage = (event) => {
    const newLog = JSON.parse(event.data);
    setLogs((prev) => [newLog, ...prev]);
};
```

---

## Communication Protocol

The system uses standard JSON over HTTP for ingestion and JSON over WebSockets for streaming.

### 1. Ingestion (Generator → API)
Endpoint: `POST /api/logs`

```json
{
  "service": "payment-gateway",
  "status_code": 200,
  "message": "Transaction verified",
  "timestamp": "2023-10-25T10:30:00Z"
}
```

### 2. Streaming (API → Dashboard)
The WebSocket stream sends enriched objects with threat scores:

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID | Unique Event ID |
| `is_threat` | Bool | Flagged by ML model |
| `severity` | Enum | INFO / WARNING / CRITICAL |
| `source_ip` | String | Originating IP address |

---

## How to Run

You can run the project using **Docker** (recommended for quick start) or **Manually** (recommended for development).

### Option 1: Docker (Fastest)

Run the entire stack (Frontend, Backend, Redis, Database) with one command.

1.  Ensure **Docker Desktop** is running.
2.  In the root directory, run:

```bash
docker-compose up --build
```

3.  The app will be available at `http://localhost:5173`.

### Option 2: Manual Setup (Dev Mode)

#### 1. Setup the Backend

Navigate to the backend folder and create a virtual environment:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Start the API server:
```bash
python main.py
```

#### 2. Start the Dashboard

Navigate to the frontend folder and install dependencies:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

### 3. Generate Traffic

The dashboard will be empty initially because the database is fresh. You need to run the simulation script to create organic traffic and attacks.

**If running via Docker:**
```bash
# Execute the script inside the running backend container
docker-compose exec backend python traffic_generator.py
```

**If running Manually:**
```bash
cd backend
python traffic_generator.py
```

*You should see the graphs and logs update instantly on the dashboard.*
