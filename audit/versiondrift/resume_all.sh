#!/usr/bin/env bash
# Safe to rerun at any time (e.g. after the nightly 00:30 reboot): restarts the chat
# server + ngrok keep-alive if needed, then continues VersionDrift where it stopped.
# Order (Cloud Claude msgs #14, #21, #23, #26), all order-only:
#   NEW short models -> mxbai-large (only if it can finish before 00:30) -> primary compare
#   -> qwen3 NEW -> EXPLORATORY NEW_fp32 -> MID -> full compare. OLD is complete.
# Optional: bash resume_all.sh <pid>  waits for that process (a running embed) first.
set -uo pipefail
cd "$(dirname "$0")"
MB=~/mailbox-mcp
MXBAI_EST=${MXBAI_EST:-74200}   # projected seconds for mxbai-large in fp16 (~9x its OLD 8246 s)
if ! { [ -f $MB/keepalive.pid ] && kill -0 "$(cat $MB/keepalive.pid)" 2>/dev/null; }; then
  (cd $MB && nohup ./keepalive.sh > keepalive.log 2>&1 & echo $! > $MB/keepalive.pid)
fi
if [ $# -ge 1 ]; then while kill -0 "$1" 2>/dev/null; do sleep 30; done; fi
echo "resume_all start $(date '+%F %T')"
mkdir -p results
SHORT="MiniLM-L6 mpnet-base multiqa-MiniLM para-multi-MiniLM bge-small bge-base e5-small-v2 e5-base-v2 me5-small gte-small gte-base nomic-v1.5 arctic-s jina-v2-small"
.venv_NEW/bin/python embed_resume.py NEW $SHORT 2>&1 | tee -a results_log_NEW.txt

done_mxbai=$(.venv_NEW/bin/python -c "import json,os;e=json.load(open('emb/NEW/_env.json'))['models'].get('mxbai-large');print(int(bool(e) and (e.get('ok') is False or os.path.exists('emb/NEW/mxbai-large.npz'))))")
if [ "$done_mxbai" != 1 ]; then
  left=$(.venv_NEW/bin/python -c "
import datetime as d; n=d.datetime.now(); t=n.replace(hour=0,minute=30,second=0,microsecond=0)
t = t if t > n else t + d.timedelta(days=1); print(int((t-n).total_seconds()))")
  if [ "$left" -lt "$MXBAI_EST" ]; then
    echo "WAITING: mxbai-large needs ~${MXBAI_EST}s but only ${left}s remain before 00:30; not starting it. Rerun after the reboot. $(date '+%F %T')"
    exit 0
  fi
  echo "mxbai-large START $(date '+%F %T') (${left}s before 00:30)"
  .venv_NEW/bin/python embed_resume.py NEW mxbai-large 2>&1 | tee -a results_log_NEW.txt
fi

if ! grep -q DECISION results/compare_primary_stdout.txt 2>/dev/null; then
  .venv_NEW/bin/python compare.py OLD NEW 2>&1 | tee results/compare_primary_stdout.txt
  cp results/compare.json results/compare_primary.json
  echo "PRIMARY done at $(date '+%F %T')"
fi

.venv_NEW/bin/python embed_resume.py NEW qwen3-0.6b 2>&1 | tee -a results_log_NEW.txt

# EXPLORATORY (not pre-registered): NEW libraries, fp16 checkpoints forced to fp32
.venv_NEW/bin/python embed_fp32_resume.py NEW_fp32 gte-small gte-base mxbai-large qwen3-0.6b 2>&1 | tee -a results_log_NEW_fp32.txt
.venv_NEW/bin/python compare.py OLD NEW_fp32 2>&1 | tee results/EXPLORATORY_fp32_stdout.txt
mv results/compare.json results/EXPLORATORY_compare_fp32.json
cp results/compare_primary.json results/compare.json
echo "EXPLORATORY fp32 done at $(date '+%F %T')"

.venv_MID/bin/python embed_resume.py MID 2>&1 | tee -a results_log_MID.txt
.venv_NEW/bin/python compare.py OLD NEW MID 2>&1 | tee results/compare_stdout.txt
echo "ALL done at $(date '+%F %T')"
