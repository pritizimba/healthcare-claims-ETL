# src/03_transform.py
import pandas as pd
from pathlib import Path
from dateutil.relativedelta import relativedelta

BASE = Path(__file__).resolve().parents[1]
PROC = BASE / "data" / "processed"

def standardize():
    members = pd.read_csv(PROC / "members_canonical.csv", parse_dates=["coverage_start", "coverage_end"])
    claims = pd.read_csv(PROC / "claims_canonical.csv", parse_dates=["service_date"])
    providers = pd.read_csv(PROC / "providers_canonical.csv")

    # Standardize gender
    members["gender_std"] = members["gender"].str.upper().map({"M":"Male","F":"Female"}).fillna("Unknown")

    # Relationship mapping
    rel_map = {"01":"Self","19":"Child","20":"Student","53":"Life Partner"}
    members["relationship_std"] = members["relationship_code"].astype(str).map(rel_map).fillna("Other")

    # Fix coverage_end before coverage_start
    members["coverage_end"] = pd.to_datetime(members["coverage_end"])
    members["coverage_start"] = pd.to_datetime(members["coverage_start"])
    members.loc[members["coverage_end"] < members["coverage_start"], "coverage_end"] = members["coverage_start"]

    # Compute member-months
    def member_months(row):
        start = row["coverage_start"]
        end = row["coverage_end"]
        if pd.isna(start) or pd.isna(end):
            return 0
        months = (end.year - start.year) * 12 + (end.month - start.month) + 1
        return max(0, months)

    members["member_months"] = members.apply(member_months, axis=1)

    # Save transformed files
    members.to_csv(PROC / "members_transformed.csv", index=False)
    providers.to_csv(PROC / "providers_transformed.csv", index=False)
    claims.to_csv(PROC / "claims_transformed.csv", index=False)

    print("Transformation complete. Transformed files in data/processed")

if __name__ == "__main__":
    standardize()
