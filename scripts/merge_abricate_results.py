#!/usr/bin/env python3
"""
Merge Abricate Results Script
Combines all .tab outputs into comprehensive CSV summaries
"""

import pandas as pd
import glob
import os
import sys
from datetime import datetime

RAW_DIR = "results/raw"
SUMMARY_DIR = "results/summary"

def main():
    print("=" * 70)
    print("  Abricate Results Merger")
    print("=" * 70)
    print()
    
    # Create summary directory
    os.makedirs(SUMMARY_DIR, exist_ok=True)
    
    # === 1. Find and merge all tabular outputs ===
    print("[INFO] Searching for .tab files in:", RAW_DIR)
    all_files = glob.glob(f"{RAW_DIR}/*/*.tab")
    
    if not all_files:
        print("[ERROR] No .tab files found in results/raw/")
        print("[HINT] Run './scripts/run_abricate.sh' first to generate results")
        sys.exit(1)
    
    print(f"[INFO] Found {len(all_files)} .tab files")
    print()
    
    dfs = []
    skipped = 0
    empty = 0
    
    for file in all_files:
        # Extract database and sample name from path
        # Path structure: results/raw/{database}/{sample}_{database}.tab
        db = file.split("/")[-2]
        sample = os.path.basename(file).replace(f"_{db}.tab", "")
        
        try:
            df = pd.read_csv(file, sep="\t")
            
            if df.empty:
                empty += 1
                continue
            
            # Add metadata columns
            df["Sample"] = sample
            df["Database"] = db
            dfs.append(df)
            
        except pd.errors.EmptyDataError:
            empty += 1
            continue
        except Exception as e:
            print(f"[WARN] Error reading {file}: {e}")
            skipped += 1
    
    if not dfs:
        print("[ERROR] No valid data found in .tab files")
        print(f"[INFO] Empty files: {empty}, Skipped: {skipped}")
        sys.exit(1)
    
    print(f"[INFO] Successfully parsed {len(dfs)} files")
    print(f"[INFO] Empty results: {empty}, Errors: {skipped}")
    print()
    
    # === 2. Combine all results ===
    print("[INFO] Merging all results...")
    combined = pd.concat(dfs, ignore_index=True)
    
    # Reorder columns for better readability
    cols = combined.columns.tolist()
    priority_cols = ["Sample", "Database"]
    other_cols = [c for c in cols if c not in priority_cols]
    combined = combined[priority_cols + other_cols]
    
    # Save combined results
    output_file = f"{SUMMARY_DIR}/abricate_all_results.csv"
    combined.to_csv(output_file, index=False)
    print(f"[✓] Combined results saved: {output_file}")
    print(f"    → Total hits: {len(combined)} across {combined['Sample'].nunique()} samples")
    print()
    
    # === 3. Build presence/absence matrix ===
    print("[INFO] Building presence/absence matrix...")
    
    # Check if GENE column exists (standard Abricate output)
    if "GENE" not in combined.columns:
        print("[WARN] 'GENE' column not found. Available columns:", combined.columns.tolist())
        # Try alternative column names
        gene_col = None
        for alt in ["Gene", "gene", "SEQUENCE", "Sequence"]:
            if alt in combined.columns:
                gene_col = alt
                break
        
        if gene_col is None:
            print("[ERROR] Cannot create presence matrix: no gene identifier column found")
        else:
            print(f"[INFO] Using '{gene_col}' column instead")
            combined.rename(columns={gene_col: "GENE"}, inplace=True)
    
    if "GENE" in combined.columns:
        # Create a pivot table: rows = samples, columns = genes, values = presence (1) or absence (0)
        presence = combined.groupby(["Sample", "GENE"]).size().unstack(fill_value=0)
        
        # Convert counts to binary (1 if gene present, 0 if absent)
        presence = (presence > 0).astype(int)
        
        matrix_file = f"{SUMMARY_DIR}/abricate_presence_matrix.csv"
        presence.to_csv(matrix_file)
        print(f"[✓] Presence matrix saved: {matrix_file}")
        print(f"    → Dimensions: {presence.shape[0]} samples × {presence.shape[1]} genes")
        print()
    
    # === 4. Generate summary statistics ===
    print("[INFO] Generating summary statistics...")
    
    summary_stats = []
    for sample in combined["Sample"].unique():
        sample_data = combined[combined["Sample"] == sample]
        
        for db in sample_data["Database"].unique():
            db_data = sample_data[sample_data["Database"] == db]
            
            stats = {
                "Sample": sample,
                "Database": db,
                "Total_Hits": len(db_data),
                "Unique_Genes": db_data["GENE"].nunique() if "GENE" in db_data.columns else 0
            }
            
            # Add coverage and identity stats if available
            if "%COVERAGE" in db_data.columns:
                stats["Avg_Coverage"] = round(db_data["%COVERAGE"].mean(), 2)
            if "%IDENTITY" in db_data.columns:
                stats["Avg_Identity"] = round(db_data["%IDENTITY"].mean(), 2)
            
            summary_stats.append(stats)
    
    summary_df = pd.DataFrame(summary_stats)
    summary_file = f"{SUMMARY_DIR}/abricate_summary_stats.csv"
    summary_df.to_csv(summary_file, index=False)
    print(f"[✓] Summary statistics saved: {summary_file}")
    print()
    
    # === 5. Database-specific summaries ===
    print("[INFO] Creating database-specific summaries...")
    for db in combined["Database"].unique():
        db_data = combined[combined["Database"] == db]
        db_file = f"{SUMMARY_DIR}/abricate_{db}_results.csv"
        db_data.to_csv(db_file, index=False)
        print(f"    → {db}: {len(db_data)} hits saved to {db_file}")
    
    print()
    
    # === 6. Final summary ===
    print("=" * 70)
    print("  Merge Complete!")
    print("=" * 70)
    print()
    print(f"📁 Output directory: {SUMMARY_DIR}/")
    print()
    print("Generated files:")
    print(f"  1. abricate_all_results.csv       - All results combined")
    print(f"  2. abricate_presence_matrix.csv   - Presence/absence matrix")
    print(f"  3. abricate_summary_stats.csv     - Summary statistics per sample")
    print(f"  4. abricate_<db>_results.csv      - Per-database results")
    print()
    print(f"Total samples analyzed: {combined['Sample'].nunique()}")
    print(f"Total databases used: {combined['Database'].nunique()}")
    print(f"Total gene hits found: {len(combined)}")
    print()
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Analysis completed: {timestamp}")
    print("=" * 70)

if __name__ == "__main__":
    main()