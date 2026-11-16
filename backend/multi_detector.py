import numpy as np
from typing import Dict, Any, List
from joblib import load

from sklearn.ensemble import IsolationForest
from sentinelml.ml.data_preprocess import extract_single_log_features
from rule_engine import RuleEngine
from tor_Info import TorInfo

import pandas as pd

FEATURE_NAMES = [
    "status_code", "level_num", "endpoint_len", "endpoint_depth",
    "endpoint_entropy", "special_chars", "user_agent_len", "msg_len"
]

class MultiDetector:

    def __init__(self, rules_path: str = "rules.yaml", model_path="./sentinelml/ml/updated_model.pkl"):
        self.rule_engine = RuleEngine(rules_path)
        self.tor_intel = TorInfo()
        self.tor_intel.start_background_updater()
        self.ml_model: IsolationForest = load(model_path)


    def _extract_ml_features(self, log: Dict[str, Any]) -> list:
        status_code = float(log.get("status_code", 200))
        endpoint_len = float(len(str(log.get("endpoint", ""))))
        is_error = 1.0 if status_code >= 400 else 0.0
        
        return [status_code, endpoint_len, is_error]


    def determineFinalScore(self, base: float) -> str:
        if base >= 0.8:
            severity = "CRITICAL"
        elif base >= 0.5:
            severity = "HIGH"
        elif base >= 0.25:
            severity = "MEDIUM"
        elif base > 0.0:
            severity = "LOW"
        else:
            severity = "INFO"
    
        return severity

    def analyze(self, log: Dict[str, Any]) -> Dict[str, Any]:
        #! Deterministic Rule Matching
        rule_matches = self.rule_engine.evaluate(log)
        
        #! Tor Detection
        client_ip = log.get("client_ip", "")
        is_tor = self.tor_intel.is_tor_exit(client_ip)

        #! Anomaly Check
        is_anomaly = False
        anomaly_raw_score = 0.0
        
        if self.ml_model is not None:
            raw_features = extract_single_log_features(log)
            features_df = pd.DataFrame([raw_features], columns=FEATURE_NAMES)

            #! -1 -> anomaly, 1 -> norm
            prediction = self.ml_model.predict(features_df)[0]
            anomaly_raw_score = float(self.ml_model.score_samples(features_df)[0])
            is_anomaly = (prediction == -1) and anomaly_raw_score < -0.62

        #! Risk
        base_score = 0.0
        reasons = []
        tags = []
        matchSeverity = {"HIGH": 0.75, "MEDIUM": 0.50}

        #! Process Rule Hits
        if rule_matches:
            for match in rule_matches:
                tags.append(f"RULE:{match.rule_id}")
                reasons.append(f"[{match.severity}] {match.name}: {match.description}")
                base_score = max(base_score, matchSeverity[match.severity])

        #! Process Tor
        if is_tor:
            tags.append("ANONYMITY:TOR")
            reasons.append(f"Origin IP ({client_ip}) is an active Tor Exit Node")
            # ! Tor + Rule match adds more to score
            if rule_matches:
                base_score = min(1.0, base_score + 0.25)
            else:
                base_score = max(base_score, 0.20)

        #! Process Anomaly
        if is_anomaly and not rule_matches:
            tags.append("ML:ANOMALY")
            reasons.append(f"Isolation Forest flagged behavioral outlier (score: {anomaly_raw_score:.2f})")
            base_score = max(base_score, 0.15)

        #! Determine Final Severity
        severity = self.determineFinalScore(base_score)

        return {
            "log": log,
            "is_threat": base_score >= 0.40,
            "risk_score": round(base_score, 2),
            "severity": severity,
            "tags": tags,
            "reasons": reasons,
            "is_tor": is_tor,
            "is_anomaly": is_anomaly,
            "triggered_rules": [rule.to_dict() for rule in rule_matches]
        }