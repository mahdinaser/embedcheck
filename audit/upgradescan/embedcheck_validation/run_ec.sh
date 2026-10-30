#!/usr/bin/env bash
# EMBEDCHECK VALIDATION (EXPLORATORY, Cloud Claude msg #65): snapshot each model in OLD and NEW, then compare.
set -uo pipefail
S=~/vscan; cd $S; export HF_HOME=$S/hf_cache; V=~/vdrift
while read -r ID SHA KIND; do
  SAFE=${ID//\//__}
  for T in OLD NEW; do
    [ -f ec/$T/$SAFE.json ] && continue
    t0=$(date +%s.%N)
    timeout 900 $V/.venv_$T/bin/embedcheck snapshot "$ID" --revision "$SHA" --trust-remote-code --threads 1 -o ec/$T/$SAFE.json >> ec/snap_log_$T.txt 2>&1
    echo "$T $ID $(python3 -c "print(round($(date +%s.%N)-$t0,1))")" >> ec/runtime.txt
  done
  $V/.venv_NEW/bin/embedcheck compare ec/OLD/$SAFE.json ec/NEW/$SAFE.json --json > ec/cmp/$SAFE.json 2>&1; echo "$ID $KIND $?" >> ec/exitcodes.txt
  rm -rf "$HF_HOME/hub/models--${ID//\//--}"
done < ec/todo.txt
echo EC_DONE
