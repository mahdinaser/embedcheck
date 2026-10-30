#!/usr/bin/env bash
# EXPLORATORY R3 runner: 11 SLOW models, smallest first; per model OLD/NEW/NEW_fp32 at 1 and 4 threads.
# Hard deadline 00:20 (nightly reboot at 00:30): each job's timeout is capped by the time left. Resumable.
set -uo pipefail
S=~/vscan; cd $S; export HF_HOME=$S/hf_cache; V=~/vdrift
python3 - > explore/slow_real_todo.txt <<'PY'
import json
R = json.load(open("results/scan_compare.json")); M = {m["id"]: m["sha"] for m in json.load(open("scan_models.json"))}
slow = [r for r in R if r["status"] == "SLOW"]
for r in sorted(slow, key=lambda r: json.load(open(f"scan/OLD/{r['id'].replace('/','__')}.json"))["encode_s"]): print(r["id"], M[r["id"]])
PY
left() { python3 -c "
import datetime as d; n=d.datetime.now(); t=n.replace(hour=0,minute=20,second=0,microsecond=0)
t = t if t > n else t + d.timedelta(days=1); print(int((t-n).total_seconds()))"; }
while read -r ID SHA; do
  SAFE=${ID//\//__}
  for TH in 1 4; do for CFG in "OLD 0" "NEW 0" "NEW 1"; do
    set -- $CFG; ENV=$1; FP=$2; TAG="${ENV}$([ $FP = 1 ] && echo _fp32)_${TH}t"
    [ -f explore/slow_real/${TAG}__$SAFE.json ] && continue
    L=$(left); [ "$L" -lt 120 ] && { echo "DEADLINE reached before $TAG $ID"; echo R3_STOPPED_AT_DEADLINE; exit 0; }
    T=$(( L < 3600 ? L : 3600 ))
    timeout $T $V/.venv_$ENV/bin/python explore/slow_real.py $ENV $FP $TH "$ID" "$SHA" >> explore/slow_real_log.txt 2>&1 \
      || echo "{\"config\":\"$TAG\",\"id\":\"$ID\",\"error\":\"timeout or crash (limit ${T}s)\"}" > explore/slow_real/${TAG}__$SAFE.json
  done; done
  rm -rf "$HF_HOME/hub/models--${ID//\//--}"
done < explore/slow_real_todo.txt
echo R3_DONE
