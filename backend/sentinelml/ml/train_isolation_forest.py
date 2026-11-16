import pandas as pd
from sklearn.ensemble import IsolationForest
from joblib import dump
from data_preprocess import preprocess_for_training

# training data
df = pd.read_csv("../data/training_logs.csv")

print(f"[] Loaded {len(df)} training logs")
X = preprocess_for_training(df)

print(f"[] Columns: {list(X.columns)}")

#! Train Isolation Forest
model = IsolationForest(
    n_estimators = 150,
    contamination = "auto", # We train on clean logs
    max_samples = "auto",
    random_state = 42,
    n_jobs = -1
)

model.fit(X)

dump(model, "updated_model.pkl")
print("[] Model trained and saved as updated_model.pkl")
