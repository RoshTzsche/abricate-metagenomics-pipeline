#!/usr/bin/env bash
set -e

# Load configuration
source "$(dirname "$0")/config.sh"

mkdir -p "$RAW_DIR"

# Check Abricate path
if [[ ! -x "$ABRICATE_PATH" ]]; then
    echo "[ERROR] Abricate not found at $ABRICATE_PATH"
    exit 1
fi

# List all databases
DBS=$($ABRICATE_PATH --list | awk 'NR>1 {print $1}')
if [[ -z "$DBS" ]]; then
    echo "[ERROR] No databases found. Run: $ABRICATE_PATH --setupdb"
    exit 1
fi

# Loop through samples and databases
for sample in "$SAMPLES_DIR"/*.fasta; do
    base=$(basename "$sample" .fasta)
    echo "[INFO] Processing sample: $base"

    for db in $DBS; do
        outdir="$RAW_DIR/$db"
        mkdir -p "$outdir"
        outfile="$outdir/${base}_${db}.tab"

        echo "   ├── Running Abricate ($db)..."
        "$ABRICATE_PATH" --db "$db" \
            --minid $MIN_IDENTITY --mincov $MIN_COVERAGE \
            "$sample" > "$outfile"
    done
done

echo "[INFO] Pipeline finished. You can now run merge_results.py"
