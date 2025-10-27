# 🧬 Abricate Metagenomic Annotation Pipeline

A high-performance, reproducible workflow to detect **antimicrobial resistance (AMR)**, **virulence factors**, and **plasmid** genes using [Abricate](https://github.com/tseemann/abricate).

## ✨ Features

- 🚀 **Parallel Processing**: Optional GNU Parallel support for faster analysis
- 🔄 **Multi-Database**: Automatically runs against all available Abricate databases
- 📊 **Comprehensive Outputs**: Multiple CSV formats for different analysis needs
- 🎯 **Flexible**: Choose between parallel or single-threaded execution
- 📁 **Organized**: Clean folder structure with separate raw and summary results

---

## 🔧 Requirements

### Essential
- **Ubuntu** (tested on 22.04) or any Linux distribution
- **BLAST+**: `ncbi-blast+` package
- **Python 3**: with `pandas` library
- **Abricate**: Local installation

### Optional (for parallel processing)
- **GNU Parallel**: For faster multi-threaded execution

---

## ⚙️ Installation

### 1. Install system dependencies

```bash
# Install BLAST+ and Python dependencies
sudo apt update
sudo apt install ncbi-blast+ python3 python3-pip

# Install pandas
pip3 install pandas

# Optional: Install GNU Parallel for faster processing
sudo apt install parallel
```

### 2. Install Abricate

```bash
# Clone Abricate repository
git clone https://github.com/tseemann/abricate.git

# Build Abricate
cd abricate && make && cd ..

# Setup databases
./abricate/bin/abricate --setupdb

# Verify installation
./abricate/bin/abricate --list
```

### 3. Prepare your data

```bash
# Create the samples directory
mkdir -p data/samples

# Copy your FASTA files
cp /path/to/your/*.fasta data/samples/
```

---

## 🚀 Usage

### Quick Start

```bash
# 1. Make scripts executable
chmod +x scripts/run_abricate.sh

# 2. Run the pipeline
./scripts/run_abricate.sh

# 3. Follow the prompts to choose execution mode:
#    [1] Parallel mode (faster, requires GNU parallel)
#    [2] Single-threaded mode (no dependencies)
```

### Execution Modes

#### Parallel Mode (Recommended)
- **Faster**: Processes multiple samples/databases simultaneously
- **Efficient**: Utilizes all CPU cores
- **Requires**: GNU Parallel installed
- **Best for**: Large datasets (many samples or databases)

#### Single-threaded Mode
- **Reliable**: No additional dependencies
- **Progress tracking**: Shows real-time task completion
- **Best for**: Small datasets or systems without GNU Parallel

---

## 📁 Project Structure

```
abricate-pipeline/
├── abricate/                          # Local Abricate installation
│   ├── bin/abricate                   # Executable binary
│   └── db/                            # Database files
├── data/
│   └── samples/                       # Input FASTA files (place yours here)
├── results/
│   ├── raw/                           # Raw .tab outputs per database/sample
│   │   ├── ncbi/                      # e.g., NCBI database results
│   │   ├── card/                      # e.g., CARD database results
│   │   └── ...
│   └── summary/                       # Merged CSV summaries
│       ├── abricate_all_results.csv
│       ├── abricate_presence_matrix.csv
│       ├── abricate_summary_stats.csv
│       └── abricate_<db>_results.csv
├── scripts/
│   ├── config.sh                      # Configuration settings
│   ├── run_abricate.sh                # Main pipeline runner
│   └── merge_abricate_results.py      # Results merger and summarizer
├── .gitignore
└── README.md
```

---

## 📊 Output Files

### Summary Directory (`results/summary/`)

| File | Description | Use Case |
|------|-------------|----------|
| `abricate_all_results.csv` | **Complete dataset** with all hits from all samples and databases | Detailed analysis, filtering, custom queries |
| `abricate_presence_matrix.csv` | **Binary matrix** (samples × genes): 1 = present, 0 = absent | Heatmaps, clustering, comparative genomics |
| `abricate_summary_stats.csv` | **Per-sample statistics**: total hits, unique genes, avg coverage/identity | Quick overview, QC checks |
| `abricate_<db>_results.csv` | **Database-specific** results (e.g., `abricate_card_results.csv`) | Database-focused analysis |

### Raw Directory (`results/raw/`)

Contains individual `.tab` files for each sample-database combination:
- Format: `results/raw/{database}/{sample}_{database}.tab`
- Example: `results/raw/card/sample1_card.tab`

---

## ⚙️ Configuration

Edit `scripts/config.sh` to customize pipeline behavior:

```bash
#!/usr/bin/env bash

# Abricate executable path
ABRICATE_PATH="./abricate/bin/abricate"

# Directory paths
SAMPLES_DIR="data/samples"
RAW_DIR="results/raw"
SUMMARY_DIR="results/summary"

# Quality thresholds
MIN_IDENTITY=70   # Minimum % identity (default: 70)
MIN_COVERAGE=70   # Minimum % coverage (default: 70)
```

### Adjusting Thresholds

- **MIN_IDENTITY**: Lower values (e.g., 60) = more permissive, more hits
- **MIN_COVERAGE**: Lower values (e.g., 50) = detect partial genes
- **Recommended**: Start with 70/70, adjust based on your needs

---

## 🔍 Example Analysis Workflow

### 1. Run the pipeline

```bash
./scripts/run_abricate.sh
```

**Sample output:**
```
════════════════════════════════════════════════════════════
  Abricate Pipeline - Execution Mode Selection
════════════════════════════════════════════════════════════

Choose execution mode:
  [1] Parallel mode (faster, requires GNU parallel)
  [2] Single-threaded mode (slower, no dependencies)

Enter your choice [1-2]: 1

Enter number of parallel jobs [default: 8]: 8
[INFO] Using parallel mode with 8 jobs
════════════════════════════════════════════════════════════

[INFO] Found 10 samples and 12 databases
[INFO] Total tasks to process: 120

[INFO] Starting parallel processing...
```

### 2. View results

```bash
# View combined results
head results/summary/abricate_all_results.csv

# Check summary statistics
cat results/summary/abricate_summary_stats.csv

# View presence/absence matrix
head results/summary/abricate_presence_matrix.csv
```

### 3. Analyze in Python/R

```python
import pandas as pd

# Load all results
df = pd.read_csv('results/summary/abricate_all_results.csv')

# Filter by database
card_results = df[df['Database'] == 'card']

# Filter by coverage/identity
high_quality = df[(df['%COVERAGE'] > 90) & (df['%IDENTITY'] > 95)]

# Load presence matrix for heatmap
matrix = pd.read_csv('results/summary/abricate_presence_matrix.csv', index_col=0)
```

---

## 🛠️ Troubleshooting

### Issue: "No .tab files found"
**Solution**: Run `./scripts/run_abricate.sh` first to generate raw results

### Issue: "Abricate not found"
**Solution**: Check that `ABRICATE_PATH` in `config.sh` points to the correct location

### Issue: "No databases found"
**Solution**: Run `./abricate/bin/abricate --setupdb` to download databases

### Issue: Parallel mode fails
**Solution**: Install GNU Parallel (`sudo apt install parallel`) or use single-threaded mode

### Issue: Python script fails with "GENE column not found"
**Solution**: The script will automatically try alternative column names. Check your Abricate version is up to date.

---

## 📈 Performance Tips

1. **Use Parallel Mode**: 5-10x faster for large datasets
2. **Adjust Job Count**: Set to number of CPU cores minus 1
3. **Increase Thresholds**: Higher MIN_IDENTITY/MIN_COVERAGE = faster runtime, fewer hits
4. **Filter Databases**: Edit `run_abricate.sh` to run only specific databases if needed

---

## 📝 Citation

If you use this pipeline, please cite:

**Abricate**: Seemann T, *Abricate*, **Github** https://github.com/tseemann/abricate

**Databases**: Cite the specific databases you use (CARD, NCBI, ResFinder, etc.)

---

## 📄 License

This pipeline is open source. Abricate and its databases have their own licenses - please check their respective repositories.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📧 Support

For issues with:
- **This pipeline**: Open a GitHub issue
- **Abricate**: Visit https://github.com/tseemann/abricate
- **Databases**: Contact the respective database maintainers

---

**Last updated**: 2025
