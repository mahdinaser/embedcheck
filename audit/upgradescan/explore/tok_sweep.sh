#!/usr/bin/env bash
# EXPLORATORY (Cloud Claude msg #52): tokenizer sweep over the 90 OLD-loadable scan models,
# OLD then NEW per model, cache deleted after both. Resumable. Then writes the summary.
set -uo pipefail
S=~/vscan; cd $S; export HF_HOME=$S/hf_cache; V=~/vdrift
python3 - > explore/tok_todo.txt <<'PY'
import json
ok = {r["id"] for r in json.load(open("results/scan_compare.json")) if r["status"] in ("ok", "BREAK", "DRIFT", "SLOW")}
for m in json.load(open("scan_models.json")):
    if m["id"] in ok: print(m["id"], m["sha"])
PY
while read -r ID SHA; do
  SAFE=${ID//\//__}
  for T in OLD NEW; do
    [ -f explore/tok/$T/$SAFE.json ] && continue
    timeout 900 $V/.venv_$T/bin/python explore/tok_probe.py $T "$ID" "$SHA" >> explore/tok_log_$T.txt 2>&1
    [ -f explore/tok/$T/$SAFE.json ] || echo "{\"tag\":\"$T\",\"id\":\"$ID\",\"ok\":false,\"error\":\"crash or timeout\"}" > explore/tok/$T/$SAFE.json
  done
  rm -rf "$HF_HOME/hub/models--${ID//\//--}"
done < explore/tok_todo.txt
python3 explore/tok_summary.py
