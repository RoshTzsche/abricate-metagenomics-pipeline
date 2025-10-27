#!/usr/bin/env bash

# Configuration file for Abricate pipeline
ABRICATE_PATH="./abricate/bin/abricate"

SAMPLES_DIR="data/samples"
RAW_DIR="results/raw"
SUMMARY_DIR="results/summary"

# Minimum thresholds (optional)
MIN_IDENTITY=70
MIN_COVERAGE=70

# Number of threads for GNU parallel
THREADS=8

# Enable or disable Python merging (optional, can be commented out in main script)
MERGE_SCRIPT="scripts/merge_results.py"
