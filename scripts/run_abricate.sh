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

# Ask user for execution mode
echo "════════════════════════════════════════════════════════════"
echo "  Abricate Pipeline - Execution Mode Selection"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Choose execution mode:"
echo "  [1] Parallel mode (faster, requires GNU parallel)"
echo "  [2] Single-threaded mode (slower, no dependencies)"
echo ""
read -p "Enter your choice [1-2]: " MODE_CHOICE

case $MODE_CHOICE in
    1)
        # Check if GNU parallel is available
        if ! command -v parallel &> /dev/null; then
            echo "[ERROR] GNU parallel not found. Install it with: sudo apt install parallel"
            echo "[INFO] Falling back to single-threaded mode..."
            USE_PARALLEL=false
        else
            USE_PARALLEL=true
            # Ask for number of jobs
            DEFAULT_JOBS=$(nproc)
            echo ""
            read -p "Enter number of parallel jobs [default: $DEFAULT_JOBS]: " NUM_JOBS
            NUM_JOBS=${NUM_JOBS:-$DEFAULT_JOBS}
            echo "[INFO] Using parallel mode with $NUM_JOBS jobs"
        fi
        ;;
    2)
        USE_PARALLEL=false
        echo "[INFO] Using single-threaded mode"
        ;;
    *)
        echo "[ERROR] Invalid choice. Defaulting to single-threaded mode."
        USE_PARALLEL=false
        ;;
esac

echo "════════════════════════════════════════════════════════════"
echo ""

# Count total tasks for progress reporting
SAMPLE_COUNT=$(ls -1 "$SAMPLES_DIR"/*.fasta 2>/dev/null | wc -l)
DB_COUNT=$(echo "$DBS" | wc -w)
TOTAL_TASKS=$((SAMPLE_COUNT * DB_COUNT))

echo "[INFO] Found $SAMPLE_COUNT samples and $DB_COUNT databases"
echo "[INFO] Total tasks to process: $TOTAL_TASKS"
echo ""

# Function to run a single Abricate job
run_abricate_job() {
    local sample=$1
    local db=$2
    local base=$(basename "$sample" .fasta)
    local outdir="$RAW_DIR/$db"
    local outfile="$outdir/${base}_${db}.tab"
    
    mkdir -p "$outdir"
    
    "$ABRICATE_PATH" --db "$db" \
        --minid $MIN_IDENTITY --mincov $MIN_COVERAGE \
        "$sample" > "$outfile" 2>/dev/null
    
    echo "[✓] Completed: $base → $db"
}

# Export function and variables for parallel
export -f run_abricate_job
export ABRICATE_PATH MIN_IDENTITY MIN_COVERAGE RAW_DIR

if [ "$USE_PARALLEL" = true ]; then
    # Parallel mode
    echo "[INFO] Starting parallel processing..."
    echo ""
    
    # Create a job list
    JOBLIST=$(mktemp)
    for sample in "$SAMPLES_DIR"/*.fasta; do
        for db in $DBS; do
            echo "$sample $db"
        done
    done > "$JOBLIST"
    
    # Run with parallel
    parallel --colsep ' ' -j "$NUM_JOBS" --bar \
        run_abricate_job {1} {2} :::: "$JOBLIST"
    
    # Cleanup
    rm -f "$JOBLIST"
    
else
    # Single-threaded mode
    echo "[INFO] Starting single-threaded processing..."
    echo ""
    
    CURRENT_TASK=0
    for sample in "$SAMPLES_DIR"/*.fasta; do
        base=$(basename "$sample" .fasta)
        echo "[INFO] Processing sample: $base"
        
        for db in $DBS; do
            CURRENT_TASK=$((CURRENT_TASK + 1))
            outdir="$RAW_DIR/$db"
            mkdir -p "$outdir"
            outfile="$outdir/${base}_${db}.tab"
            
            echo "   ├── [$CURRENT_TASK/$TOTAL_TASKS] Running Abricate ($db)..."
            "$ABRICATE_PATH" --db "$db" \
                --minid $MIN_IDENTITY --mincov $MIN_COVERAGE \
                "$sample" > "$outfile"
        done
        echo ""
    done
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "[INFO] All Abricate jobs completed successfully!"
echo "════════════════════════════════════════════════════════════"
echo ""

# Run merge script
echo "[INFO] Running merge script..."
python3 "$(dirname "$0")/merge_abricate_results.py"

echo ""
echo "[✓] Pipeline finished! Results available in: $SUMMARY_DIR"