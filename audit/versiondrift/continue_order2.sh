#!/usr/bin/env bash
# Replaces continue_order.sh after the NEW embed (Cloud Claude chat msg #21). Order:
# wait for NEW -> primary compare -> EXPLORATORY NEW_fp32 -> MID -> full compare.
# Pre-registered commands are unchanged; the exploratory step writes only to
# separately named files and does not count toward the decision.
set -uo pipefail
cd "$(dirname "$0")"
NEW_PID=${1:?usage: continue_order2.sh <pid of embed.py NEW>}
while kill -0 "$NEW_PID" 2>/dev/null; do sleep 30; done
echo "NEW finished at $(date '+%F %T')"
mkdir -p results
.venv_NEW/bin/python compare.py OLD NEW 2>&1 | tee results/compare_primary_stdout.txt
cp results/compare.json results/compare_primary.json
echo "PRIMARY done at $(date '+%F %T')"

# EXPLORATORY (not pre-registered): NEW libraries, fp16 checkpoints forced to fp32
.venv_NEW/bin/python embed_fp32.py NEW_fp32 gte-small gte-base mxbai-large qwen3-0.6b 2>&1 | tee -a results_log_NEW_fp32.txt
.venv_NEW/bin/python compare.py OLD NEW_fp32 2>&1 | tee results/EXPLORATORY_fp32_stdout.txt
mv results/compare.json results/EXPLORATORY_compare_fp32.json
cp results/compare_primary.json results/compare.json
echo "EXPLORATORY fp32 done at $(date '+%F %T')"

.venv_MID/bin/python embed.py MID 2>&1 | tee -a results_log_MID.txt
.venv_NEW/bin/python compare.py OLD NEW MID 2>&1 | tee results/compare_stdout.txt
echo "ALL done at $(date '+%F %T')"
