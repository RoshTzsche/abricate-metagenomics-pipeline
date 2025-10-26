#!/usr/bin/env python3
import pandas as pd
import glob
import os

RAW_DIR = "results/raw"
SUMMARY_DIR = "results/summary"
os.makedirs(SUMMARY_DIR, exist_ok=True)

# === 1. Merge all tabular outputs ===
all_files = glob.glob(f"{RAW_DIR}/*/*.tab")
dfs = []

for file in all_files:
    db = file.split("/")[-2]
    sample = os.path.basename(file).replace(f"_{db}.tab", "")
    try:
        df = pd.read_csv(file, sep="\t")
        if not df.empty:
            df["Sample"] = sample
            df["Database"] = db
            dfs.append(df)
    except Exception as e:
        print(f"[WARN] Skipping {file}: {e}")

if dfs:
    combined = pd.concat(dfs, ignore_index=True)
    combined.to_csv(f"{SUMMARY_DIR}/abricate_all_results.csv", index=False)
    print(f"[INFO] Combined results: {SUMMARY_DIR}/abricate_all_results.csv")
else:
    print("[ERROR] No .tab files found. Run run_abricate.sh first.")
    exit(1)

# === 2. Build presence/absence matrix ===
presence = (
    combined.groupby(["Sample", "Database", "GENE"])
    .size()
    .unstack(fill_value=0)
)
presence.to_csv(f"{SUMMARY_DIR}/abricate_presence_matrix.csv")
print(f"[INFO] Presence matrix: {SUMMARY_DIR}/abricate_presence_matrix.csv")

# === 3. Convert Abricate summary TSV to CSV ===
abricate_summary_tsv = f"{SUMMARY_DIR}/abricate_summary.tsv"
if os.path.exists(abricate_summary_tsv):
    try:
        summary_df = pd.read_csv(abricate_summary_tsv, sep="\t")
        summary_df.to_csv(f"{SUMMARY_DIR}/abricate_summary.csv", index=False)
        print(f"[INFO] Abricate summary CSV: {SUMMARY_DIR}/abricate_summary.csv")
    except Exception as e:
        print(f"[WARN] Could not convert summary TSV: {e}")
else:
    print("[WARN] Abricate summary TSV not found; skipping conversion.")
