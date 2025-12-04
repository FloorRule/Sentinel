import pandas as pd

def preprocess_for_training(df):
    df["message_length"] = df["message"].str.len()

    level_map = {"INFO":1, "WARNING":2, "ERROR":3, "CRITICAL":4}
    df["level_num"] = df["level"].map(level_map)

    df["service_num"] = df["service"].astype("category").cat.codes

    dt = pd.to_datetime(df["timestamp"])
    df["minute"] = dt.dt.minute
    df["second"] = dt.dt.second

    return df[["message_length", "level_num", "service_num", "minute", "second"]]
