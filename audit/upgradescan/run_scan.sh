#!/usr/bin/env bash
# Usage (from ~/vdrift, reusing .venv_OLD/.venv_NEW): bash ~/vscan/run_scan.sh   — resumable
set -uo pipefail
S=~/vscan; cd $S; export HF_HOME=$S/hf_cache; mkdir -p scan/OLD scan/NEW
V=~/vdrift
[ -f scan_models.json ] || $V/.venv_NEW/bin/python select_models.py
$V/.venv_NEW/bin/python - <<'PY' > _todo.txt
import json; [print(m["id"], m["sha"]) for m in json.load(open("scan_models.json"))]
PY
while read -r ID SHA; do
  SAFE=${ID//\//__}
  for T in OLD NEW; do
    [ -f scan/$T/$SAFE.json ] && continue
    timeout 900 $V/.venv_$T/bin/python probe.py $T "$ID" "$SHA" >> scan_log_$T.txt 2>&1; RC=$?
    if [ ! -f scan/$T/$SAFE.json ] || [ $RC -eq 124 ]; then
      if [ $RC -eq 124 ]; then MSG="Timeout after 900 s"; else MSG="Crash, exit code $RC"; fi
      echo "{\"tag\":\"$T\",\"id\":\"$ID\",\"sha\":\"$SHA\",\"ok\":false,\"error\":\"$MSG\"}" > scan/$T/$SAFE.json
    fi
  done
  rm -rf "$HF_HOME/hub/models--${ID//\//--}"   # free disk; this scan's own cache only
done < _todo.txt
$V/.venv_NEW/bin/python compare_scan.py | tee results/scan_stdout.txt
