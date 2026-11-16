
from collections import Counter
import math

import pandas as pd


LEVEL_MAP = {
    "INFO": 1, 
    "WARNING": 2, 
    "ERROR": 3, 
    "CRITICAL": 4
}

SPECIAL_CHARS = set("'\"><=;%()\\.*&|^[]")

#! Known math formula
def calculate_shannon_entropy(text) -> float:
    if not text:
        return 0.0
    
    entropy = 0.0
    text_length = len(text)
    char_counts = Counter(text)
    
    for count in char_counts.values():
        probability = count / text_length
        entropy -= probability * math.log2(probability)
        
    return entropy


def count_special_chars(text) -> int:
    if not text:
        return 0
    return sum(1 for char in text if char in SPECIAL_CHARS)

#! Turns log into training data
def preprocess_for_training(df):
    df_training = pd.DataFrame()

    df_training["status_code"] = df["status_code"].fillna(200).astype(int)
    df_training["level_num"] = df["level"].map(LEVEL_MAP).fillna(1).astype(int)

    #! Endpoint
    endpoints = df["endpoint"].fillna("").astype(str)
    df_training["endpoint_len"] = endpoints.str.len()
    df_training["endpoint_depth"] = endpoints.apply(lambda x: x.count("/"))
    df_training["endpoint_entropy"] = endpoints.apply(calculate_shannon_entropy)
    df_training["special_chars"] = endpoints.apply(count_special_chars)

    #! User Agent & Message
    user_agents = df["user_agent"].fillna("").astype(str)
    df_training["user_agent_len"] = user_agents.str.len()
    df_training["msg_len"] = df["message"].fillna("").astype(str).str.len()

    return df_training

#! Turns single log into training data
def extract_single_log_features(log):
    endpoint = str(log["endpoint"])
    user_agent = str(log["user_agent"])
    message = str(log["message"])
    level = str(log["level"])
    status_code = float(log["status_code"])

    return [
        status_code,
        float(LEVEL_MAP.get(level, 1)),
        float(len(endpoint)),
        float(endpoint.count("/")),
        calculate_shannon_entropy(endpoint),
        float(count_special_chars(endpoint)),
        float(len(user_agent)),
        float(len(message))
    ]