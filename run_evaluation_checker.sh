#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

METHOD="${1:-Direct}"
NUM_GENERATIONS="${2:-20}"
MODEL="${3:-gpt-5-mini}"

python process_evaluation.py \
  --dataset_root Dataset \
  --generated_root "Benchmark/Dataset_Generate/${METHOD}" \
  --output_root "Results/${METHOD}/Output" \
  --report_root "Results/${METHOD}/Check_Reports" \
  --num_generations "${NUM_GENERATIONS}" \
  -m "${MODEL}"
