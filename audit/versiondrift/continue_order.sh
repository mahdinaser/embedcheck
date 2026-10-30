#!/usr/bin/env bash
# Order-only change requested by Cloud Claude (2026-10-27, chat msg #14):
# after OLD finishes, run NEW, then the primary compare, then MID, then the full compare.
# The commands are the same ones run_all.sh uses; only their order differs.
set -uo pipefail
cd "$(dirname "$0")"
OLD_PID=${1:?usage: continue_order.sh <pid of embed.py OLD>}
while kill -0 "$OLD_PID" 2>/dev/null; do sleep 30; done
echo "OLD finished at $(date '+%F %T')"
.venv_NEW/bin/python embed.py NEW 2>&1 | tee -a results_log_NEW.txt
mkdir -p results
.venv_NEW/bin/python compare.py OLD NEW 2>&1 | tee results/compare_primary_stdout.txt
echo "PRIMARY done at $(date '+%F %T')"
.venv_MID/bin/python embed.py MID 2>&1 | tee -a results_log_MID.txt
.venv_NEW/bin/python compare.py OLD NEW MID 2>&1 | tee results/compare_stdout.txt
echo "ALL done at $(date '+%F %T')"
