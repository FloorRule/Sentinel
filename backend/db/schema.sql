CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    service TEXT,
    level TEXT,
    message TEXT,
    endpoint TEXT,
    status_code INTEGER,
    user_agent TEXT,
    client_ip TEXT,
    is_threat INTEGER,
    risk_score REAL,
    severity TEXT,
    tags TEXT,
    reasons TEXT
);