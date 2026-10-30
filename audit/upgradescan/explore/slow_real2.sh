#!/usr/bin/env bash
# EXPLORATORY R3 continuation (Cloud Claude msg #71): the 5 not-run SLOW models, 4 threads first for all,
# then 1 thread. Same slow_real.py and settings. Deadline 00:15. Skips configs already recorded.
set -uo pipefail
S=~/vscan; cd $S; export HF_HOME=$S/hf_cache; V=~/vdrift
MODELS="thenlper/gte-large mixedbread-ai/deepset-mxbai-embed-de-large-v1 intfloat/multilingual-e5-large-instruct sdadas/mmlw-retrieval-roberta-large mixedbread-ai/mxbai-embed-large-v1"
left() { python3 -c "
import datetime as d; n=d.datetime.now(); t=n.replace(hour=0,minute=15,second=0,microsecond=0)
t = t if t > n else t + d.timedelta(days=1); print(int((t-n).total_seconds()))"; }
sha() { python3 -c "import json,sys; print(next(m['sha'] for m in json.load(open('scan_models.json')) if m['id']==sys.argv[1]))" "$1"; }
for TH in 4 1; do for ID in $MODELS; do
  SAFE=${ID//\//__}; SHA=$(sha "$ID")
  for CFG in "OLD 0" "NEW 0" "NEW 1"; do
    set -- $CFG; ENV=$1; FP=$2; TAG="${ENV}$([ $FP = 1 ] && echo _fp32)_${TH}t"
    [ -f explore/slow_real/${TAG}__$SAFE.json ] && continue
    L=$(left); [ "$L" -lt 120 ] && { echo "DEADLINE reached before $TAG $ID"; echo R3B_STOPPED_AT_DEADLINE; exit 0; }
    T=$(( L < 3600 ? L : 3600 ))
    timeout $T $V/.venv_$ENV/bin/python explore/slow_real.py $ENV $FP $TH "$ID" "$SHA" >> explore/slow_real_log.txt 2>&1 \
      || echo "{\"config\":\"$TAG\",\"id\":\"$ID\",\"error\":\"timeout or crash (limit ${T}s)\"}" > explore/slow_real/${TAG}__$SAFE.json
  done
done; done
echo R3B_DONE
