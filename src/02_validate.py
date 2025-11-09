# src/02_validate.py
import pandas as pd
from pathlib import Path
import re

BASE = Path(__file__).resolve().parents[1]
PROC = BASE / "data" / "processed"

def validate():
    members = pd.read_csv(PROC / "members_canonical.csv", parse_dates=["coverage_start", "coverage_end"])
    providers = pd.read_csv(PROC / "providers_canonical.csv")
    claims = pd.read_csv(PROC / "claims_canonical.csv", parse_dates=["service_date"])

    issues = []

    # 1. Missing critical fields
    for df, name, cols in [
        (members, "members", ["member_id","coverage_start","coverage_end"]),
        (providers, "providers", ["provider_id","npi"]),
        (claims, "claims", ["claim_id","member_id","provider_id","service_date"])
    ]:
        for c in cols:
            missing = df[c].isna().sum()
            if missing > 0:
                issues.append(f"{missing} missing values in {name}.{c}")

    # 2. NPI format check
    npi_bad = ~providers["npi"].astype(str).str.fullmatch(r"\d{10}")
    if npi_bad.any():
        issues.append(f"{npi_bad.sum()} providers with invalid NPI format")

    # 3. Claims referencing unknown members/providers
    unknown_members = (~claims["member_id"].isin(members["member_id"])).sum()
    unknown_providers = (~claims["provider_id"].isin(providers["provider_id"])).sum()
    if unknown_members > 0:
        issues.append(f"{unknown_members} claims reference unknown members")
    if unknown_providers > 0:
        issues.append(f"{unknown_providers} claims reference unknown providers")

    # 4. Simple ICD-10 code pattern check
    icd_bad = ~claims["icd10_code"].astype(str).str.fullmatch(r"[A-Z]\d{2}(\.\d+)?")
    if icd_bad.any():
        issues.append(f"{icd_bad.sum()} claims with non-standard ICD-10 format")

    # Write report
    report_path = PROC / "validation_report.txt"
    with open(report_path, "w") as f:
        if issues:
            f.write("\n".join(issues))
        else:
            f.write("No validation issues found.\n")

    print("Validation complete. See", report_path)

if __name__ == "__main__":
    validate()
