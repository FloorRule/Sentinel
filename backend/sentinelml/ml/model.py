import pandas as pd
from sklearn.ensemble import IsolationForest
from joblib import load

from sentinelml.ml.data_preprocess import preprocess_for_training


class IsolationForestDetector:
    def __init__(self, model_path="./sentinelml/ml/updated_model.pkl"):
        self.model: IsolationForest = load(model_path)

    def predict_log(self, log: dict):
        allowed = ["level", "message"]
        log = {k: v for k, v in log.items() if k in allowed}
        
        df = pd.DataFrame([log])
        X = preprocess_for_training(df)
        score = float(self.model.decision_function(X)[0])

        # 1 = normal
        #-1 = anomaly
        return {
            "is_anomaly": score < -0.07,
            "score": score
        }
