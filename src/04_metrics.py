# src/04_metrics.py
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PROC = BASE / "data" / "processed"

def metrics():
    members = pd.read_csv(PROC / "members_transformed.csv", parse_dates=["coverage_start","coverage_end"])
    claims = pd.read_csv(PROC / "claims_transformed.csv", parse_dates=["service_date"])

    # Aggregate claims by member
    agg = claims.groupby("member_id").agg(
        total_allowed = ("allowed_amount", "sum"),
        total_paid    = ("paid_amount", "sum"),
        visits        = ("claim_id", "count")
    ).reset_index()

    # Merge with members
    merged = members.merge(agg, how="left", on="member_id")
    merged[["total_allowed","total_paid","visits"]] = merged[["total_allowed","total_paid","visits"]].fillna(0)

    # Compute PMPM and visits per 1000
    merged["pmpm_allowed"] = merged.apply(lambda r: r["total_allowed"]/r["member_months"] if r["member_months"]>0 else 0, axis=1)
    merged["visits_per_1000"] = merged["visits"] / merged["member_months"].replace(0,1) * 1000

    output_path = PROC / "member_level_metrics.csv"
    merged.to_csv(output_path, index=False)

    print("Metrics computed. See", output_path)

if __name__ == "__main__":
    metrics()
