
LEVEL_MAP = {
    "INFO": 1, 
    "WARNING": 2, 
    "ERROR": 3, 
    "CRITICAL": 4
}

def preprocess_for_training(df):
    df["message_length"] = df["message"].str.len()

    df["level_num"] = df["level"].map(LEVEL_MAP).fillna(1) 

    return df[["message_length", "level_num"]]