import pandas as pd
from sklearn.ensemble import IsolationForest
from joblib import dump
from data_preprocess import preprocess_for_training

# training data
df = pd.read_csv("data/training_logs.csv")
X = preprocess_for_training(df)

model = IsolationForest(
    n_estimators=200,
    contamination=0.05, # 5% anomalies
    random_state=42
)

model.fit(X)

dump(model, "ml/model.pkl")
print("Model trained and saved as ml/model.pkl")
