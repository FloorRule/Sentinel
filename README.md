
# Sentinel

A high-throughput, real-time log ingestion and hybrid threat detection system.

Sentinel ingests raw HTTP access and application logs through an asynchronous FastAPI pipeline, evaluates them across a multi-stage hybrid inspection engine (deterministic regex signatures, live Tor threat intelligence, and an unsupervised Isolation Forest model), and streams enriched security telemetry to a React/TypeScript dashboard via WebSockets.

https://github.com/user-attachments/assets/d904cd6f-01fa-4bc9-9cf8-c7e1f5edce39

---

## Key Highlights

* **Hybrid Detection Engine:** Combines deterministic signature matching (eliminating false positives on known exploits) with unsupervised anomaly detection (catching zero-days and behavioral outliers).
* **8-Dimensional Security Feature Extraction:** Evaluates mathematical entropy, syntactic structure, and protocol metadata for real-time ML inference.
* **Live Threat Intelligence:** Tracks active Tor exit nodes with periodic sync and in-memory $O(1)$ lookup complexity.
* **Explainable Multi-Signal Scoring:** Normalizes disparate security signals into a $0.0 - 1.0$ risk score mapped to actionable severity tiers with granular reason arrays.
* **Decoupled Asynchronous Streaming:** Uses Redis Pub/Sub to decouple high-volume log ingestion from ML scoring and WebSocket client broadcasting.

---

## System Architecture

```
[ Log Stream / Ingestion ]
           │  POST /api/logs
           ▼
[ FastAPI Ingestion API ]
           │
           ▼  (Redis Broker)
┌───────────────────────────────────────────────────────────┐
│              HYBRID THREAT DETECTION PIPELINE             │
│                                                           │
│ 1. Rule Engine  ──► 2. Threat Intel ──► 3. Isolation Forest│
│   (rules.yaml)       (Tor Relays)        (8D Vector)      │
│                                                           │
│                             │                             │
│                             ▼                             │
│             4. Multi-Signal Risk Scorer                   │
│          (Normalized 0.0 - 1.0 & Severity)                │
└───────────────────────────────────────────────────────────┘
           │
           ├────────────────────────┬──────────────────────┐
           ▼                        ▼                      ▼
  [ SQLite / DB Cache ]     [ Redis Pub/Sub ]      [ Console Audit ]
                                    │
                                    ▼  (WebSocket Feed)
                      [ React + Shadcn Dashboard ]
```

---

## Detection Pipeline Deep-Dive

Sentinel does not rely on a single detection paradigm. Every ingested log passes through an orchestrated 4-stage evaluation flow:

### 1. Deterministic Signature Engine (`rule_engine.py`, `rules.yaml`)
* Evaluates request parameters, paths, and headers against pre-compiled regular expressions.
* Detects explicit exploit attempts:
  * **SQL Injection (SQLi):** Union-based, boolean blind, and error-based payloads.
  * **Path Traversal / LFI:** Directory traversal sequences (`../`, `/etc/passwd`).
  * **Cross-Site Scripting (XSS):** Script tags, event handlers, and attribute injection.
  * **Automated Scanners:** Flags probing by tools such as `sqlmap`, `nikto`, `nmap`, or `gobuster`.

### 2. Threat Intelligence & Anonymity Tracking (`tor_intel.py`)
* Automatically synchronizes with the official Tor Project bulk exit node directory on a configurable background interval.
* Ingests addresses into an in-memory hash set for $O(1)$ lookup overhead during stream evaluation.
* Immediate correlation: raises base risk score when malicious patterns originate from anonymous exit relays.

### 3. Behavioral Anomaly Detection (`data_preprocess.py`, `train_isolation_forest.py`)
* Employs Scikit-Learn’s `IsolationForest` trained on clean baseline traffic to detect unknown zero-day anomalies.
* Extracts an **8-dimensional numerical feature vector** on every request:
  1. **Shannon Entropy:** Measures character randomness across query paths (identifies hex-encoding, encrypted shells, and obfuscated shellcode).
  2. **Endpoint Length:** Identifies buffer overflow attempts and deeply nested URI fuzzing.
  3. **Path Depth:** Slash count (`/`) measuring hierarchy navigation.
  4. **Special Character Density:** Ratio of non-alphanumeric security delimiters (`'`, `"`, `<`, `>`, `;`, `%`, `&`, `|`).
  5. **User-Agent Length:** Detects stripped, missing, or abnormally long UA strings.
  6. **HTTP Status Code:** Incorporates downstream server responses (e.g., 401, 403, 500).
  7. **Log Severity Weight:** Numeric weighting based on application log level.
  8. **Method Weighting:** Assigns risk factors to non-idempotent HTTP verbs (POST, PUT, DELETE).

### 4. Multi-Signal Risk Scoring (`multi_detector.py`)
* Synthesizes outputs from all previous stages into a unified risk score normalized between **`0.0`** and **`1.0`**.
* Maps scores into standard operational severity tiers:
  * `0.0 - 0.2` -> **INFO**
  * `0.2 - 0.5` -> **LOW**
  * `0.5 - 0.7` -> **MEDIUM**
  * `0.7 - 0.85` -> **HIGH**
  * `0.85 - 1.0` -> **CRITICAL**
* Generates an **explainable reason array** (e.g., `["SQL Injection pattern matched", "Traffic from active Tor exit node", "High URL Shannon entropy"]`) ensuring security operators know exactly why an alert was triggered.

---

## Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend & Ingestion** | Python 3.11+, FastAPI, Uvicorn, Pydantic v2 |
| **Detection & Analytics**| Scikit-Learn (Isolation Forest), NumPy, Pandas, PyYAML |
| **Caching & Messaging** | Redis (Pub/Sub & message brokering), SQLite |
| **Frontend UI** | React 18, TypeScript, Vite, Tailwind CSS, Shadcn UI, Recharts |
| **DevOps & Containers** | Docker, Docker Compose |

---

## Getting Started

### Prerequisites
* [Docker Desktop](https://www.docker.com/) installed and running.

---

### Option 1: Docker Compose (Recommended)

Spins up the Ingestion API, Redis broker, ML evaluation pipeline, React frontend, and a synthetic traffic generator with a single command:

```bash
docker compose up --build
```

* **Interactive Dashboard:** `http://localhost:5173`
* **FastAPI Swagger Docs:** `http://localhost:8000/docs`
* **WebSocket Stream Endpoint:** `ws://localhost:8000/ws/dashboard`

---

### Option 2: Local Development Setup

#### 1. Start Redis
Make sure a local Redis instance is running on port `6379`:
```bash
# Via native service
sudo service redis-server start

# Or standalone Docker
docker run -d -p 6379:6379 --name sentinel-redis redis:alpine
```

#### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt

# (Optional) Re-train baseline Isolation Forest model
python train_isolation_forest.py

# Launch API
python main.py
```

#### 3. Frontend Setup
```bash
cd frontend/sentinel-ui
npm install
npm run dev
```

#### 4. Run Traffic Simulation
Generate realistic traffic containing benign queries alongside simulated SQLi, XSS, and Tor-originating events:
```bash
cd scripts
python traffic_generator.py
```

---

## Data Schemas

### 1. Ingestion Payload (`POST /api/logs`)
```json
{
  "service": "auth-service",
  "endpoint": "/api/v1/login?user=admin' OR 1=1 --",
  "method": "POST",
  "status_code": 401,
  "client_ip": "185.220.101.5",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
  "message": "Authentication failed for user payload",
  "timestamp": "2026-09-17T12:00:00Z"
}
```

### 2. Enriched WebSocket Telemetry Event (`ws://.../ws/dashboard`)
```json
{
  "id": "e4b3c79a-6c12-4d22-92a1-b8478d10b8cf",
  "timestamp": "2026-09-17T12:00:00Z",
  "service": "auth-service",
  "endpoint": "/api/v1/login?user=admin' OR 1=1 --",
  "client_ip": "185.220.101.5",
  "risk_score": 0.94,
  "level": "CRITICAL",
  "is_threat": true,
  "is_tor": true,
  "rule_matches": ["SQL_INJECTION_AUTH_BYPASS"],
  "reasons": [
    "Matched deterministic SQLi signature: OR 1=1",
    "Originating IP matches active Tor Exit Node",
    "High punctuation and delimiter density in endpoint"
  ]
}
```

---

## Roadmap

- [x] **Rule-Based Engine:** Pre-compiled regex evaluation for SQLi, XSS, and scanner signatures.
- [x] **Threat Intelligence:** In-memory Tor exit node correlation.
- [x] **Unsupervised ML:** Isolation Forest integration for zero-day entropy anomalies.
- [ ] **Stream Reliability:** Migrate internal Redis messaging from Pub/Sub to **Redis Streams** with consumer groups for persistent message replay.
- [ ] **Sigma Rule Parser:** Native support for compiling community Sigma detection rules into Sentinel signatures.
- [ ] **Daemon Log Agent:** Standalone Go-based log shipping daemon (alternative to Filebeat) for direct Nginx/kernel auditd log harvesting.
```
