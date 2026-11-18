import pandas as pd
from pathlib import Path

ATTACK_CSV = "datasets/attacks.csv"
BENIGN_CSV = "datasets/benign.csv"
BASE_URL = "http://localhost:8000"
TIMEOUT = 120

def load_prompts_from_csv(file_path):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")
    df = pd.read_csv(path)
    # Extracts the prompt column into a list for the benchmark runner
    return df["text"].dropna().tolist()

# Inside your run_benchmark() function:
attacks = load_prompts_from_csv(ATTACK_CSV)
benign = load_prompts_from_csv(BENIGN_CSV)
