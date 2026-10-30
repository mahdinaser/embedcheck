#!/usr/bin/env bash
# EXPLORATORY (Cloud Claude msg #55): fp32-forced probe in NEW for the 11 SLOW models. Resumable.
set -uo pipefail
S=~/vscan; cd $S; export HF_HOME=$S/hf_cache; V=~/vdrift; mkdir -p scan/NEW_fp32
while read -r ID SHA; do
  SAFE=${ID//\//__}
  [ -f scan/NEW_fp32/$SAFE.json ] && continue
  timeout 900 $V/.venv_NEW/bin/python explore/probe_fp32.py NEW_fp32 "$ID" "$SHA" >> explore/slow_fp32_log.txt 2>&1
  [ -f scan/NEW_fp32/$SAFE.json ] || echo "{\"tag\":\"NEW_fp32\",\"id\":\"$ID\",\"ok\":false,\"error\":\"crash or timeout\"}" > scan/NEW_fp32/$SAFE.json
  rm -rf "$HF_HOME/hub/models--${ID//\//--}"
done < explore/slow_todo.txt
echo SLOW_FP32_DONE
