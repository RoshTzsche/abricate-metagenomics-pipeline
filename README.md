## 🧬 Overview

This pipeline will:

1. Automatically detect all databases from your local Abricate install.
2. Run each FASTA sample against **all databases**.
3. Save every `.tab` result per (sample × database).
4. Merge all outputs into **CSV summaries**:

   * `abricate_all_results.csv` → full detailed results
   * `abricate_presence_matrix.csv` → presence/absence table
   * `abricate_summary.csv` → output from Abricate’s `--summary` (for comparison)
5. Be organized with a clear folder structure and reusable scripts.

---

README 
# Abricate Metagenomic Annotation Pipeline

This repository provides a reproducible workflow to detect **antimicrobial resistance**, **virulence**, and **plasmid** genes using [Abricate](https://github.com/tseemann/abricate).

## 🔧 Requirements
- Ubuntu (tested on 22.04)
- `blast+`
- `abricate` cloned locally (`./abricate/bin/abricate`)
- `python3`, `pandas`

## ⚙️ Installation

```bash
sudo apt install ncbi-blast+ git python3-pandas
git clone https://github.com/tseemann/abricate.git
cd abricate && make && cd ..
abricate/bin/abricate --setupdb
````

## 🚀 Usage

```bash
chmod +x scripts/run_abricate.sh
./scripts/run_abricate.sh
python3 scripts/merge_results.py
```

## 📊 Output

All merged CSVs are in `results/summary/`.

| File                           | Description                     |
| ------------------------------ | ------------------------------- |
| `abricate_all_results.csv`     | All hits from all samples & DBs |
| `abricate_presence_matrix.csv` | Presence/absence matrix         |
| `abricate_summary.csv`         | Built-in summary from Abricate  |

```


## 📁 Folder Structure

```
abricate-pipeline/
├── abricate/                    # local clone of abricate
│   └── bin/abricate             # executable binary
├── data/
│   └── samples/                 # place your .fasta files here
├── results/
│   ├── raw/                     # raw .tab outputs per db/sample
│   └── summary/                 # final CSVs
├── scripts/
│   ├── run_abricate.sh          # main runner
│   ├── merge_results.py         # merging/summary script
│   └── config.sh                # optional configuration
└── README.md
```
---

## ⚙️ `scripts/config.sh`

Central place to adjust paths.

```bash
#!/usr/bin/env bash

# Configuration file for Abricate pipeline
ABRICATE_PATH="./abricate/bin/abricate"

SAMPLES_DIR="data/samples"
RAW_DIR="results/raw"
SUMMARY_DIR="results/summary"

# Minimum thresholds (optional)
MIN_IDENTITY=70
MIN_COVERAGE=70
```

---

## ⚙️ `scripts/run_abricate.sh`

This script runs all analyses.

Make it executable:
```bash
chmod +x scripts/run_abricate.sh
```
Run from project root:
```bash
./scripts/run_abricate.sh
```
---

## 🐍 `scripts/merge_results.py`

Converts everything into **CSV** and merges across all databases.

Run it:

```bash
python3 scripts/merge_results.py
```

---

## ✅  Output Summary

| File                                           | Description                       |
| ---------------------------------------------- | --------------------------------- |
| `results/raw/<db>/<sample>_<db>.tab`           | Raw Abricate output per DB/sample |
| `results/summary/abricate_all_results.csv`     | Full merged CSV with all hits     |
| `results/summary/abricate_presence_matrix.csv` | Binary matrix (samples × genes)   |
| `results/summary/abricate_summary.csv`         | Built-in summary converted to CSV |

---
