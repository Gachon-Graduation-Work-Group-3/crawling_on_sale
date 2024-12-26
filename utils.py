import pandas as pd


# Save to CSV
def save_to_csv(df, path):
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"Save a csv file on {path}")


# Load to CSV
def load_to_csv(path):
    df = pd.read_csv(path)
    print(f"Load a csv file from {path}")
    return df
