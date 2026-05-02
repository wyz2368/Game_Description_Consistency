METHOD=${1:-Direct}
NUM_GENERATIONS=${2:-5}
MODEL=${3:-gpt-5-mini}

python match_and_check_all.py \
  --dataset_root Dataset \
  --generated_root "Benchmark/Dataset_Generate/${METHOD}" \
  --output_root "Results/${METHOD}/Output" \
  --report_root "Results/${METHOD}/Check_Reports" \
  --num_generations "${NUM_GENERATIONS}" \
  -m "${MODEL}"
