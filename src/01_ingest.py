# src/01_ingest.py
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROC = BASE / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

def load_and_save():
    members = pd.read_csv(RAW / "members.csv")
    providers = pd.read_csv(RAW / "providers.csv")
    claims = pd.read_csv(RAW / "claims.csv")

    members.to_csv(PROC / "members_canonical.csv", index=False)
    providers.to_csv(PROC / "providers_canonical.csv", index=False)
    claims.to_csv(PROC / "claims_canonical.csv", index=False)

    print("Ingest complete. Files saved to data/processed")

if __name__ == "__main__":
    load_and_save()