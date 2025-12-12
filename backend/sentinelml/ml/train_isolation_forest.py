import pandas as pd
from sklearn.ensemble import IsolationForest
from joblib import dump
from data_preprocess import preprocess_for_training

# training data
df = pd.read_csv("../data/training_logs.csv")
X = preprocess_for_training(df)

model = IsolationForest(
    n_estimators=200,
    contamination="auto", # we train on clear data
    random_state=42
)

model.fit(X)

dump(model, "updated_model.pkl")
print("Model trained and saved as ml/updated_model.pkl")
