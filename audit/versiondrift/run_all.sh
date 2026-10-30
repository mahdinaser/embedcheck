#!/usr/bin/env bash
# VersionDrift kill test. Usage: bash run_all.sh   (from inside ~/vdrift)
set -uo pipefail
PY=${PY:-python3}; TORCH=${TORCH:-2.14.1}
if command -v nvidia-smi >/dev/null 2>&1; then TIDX=""; else TIDX="--index-url https://download.pytorch.org/whl/cpu"; fi
mk() { # $1=tag, rest=pip specs
  local t=$1; shift
  [ -d .venv_$t ] || $PY -m venv .venv_$t
  .venv_$t/bin/pip install -q -U pip
  .venv_$t/bin/pip install -q "torch==$TORCH" $TIDX
  .venv_$t/bin/pip install -q "$@" einops numpy "huggingface_hub" "datasets"
  .venv_$t/bin/python -c "import torch,transformers,sentence_transformers as s;print('$t', s.__version__, transformers.__version__, torch.__version__)"
}
mk OLD "sentence-transformers==3.4.1" "transformers==4.48.3"
mk MID "sentence-transformers==4.1.0" "transformers==4.51.3"
mk NEW "sentence-transformers" "transformers"   # latest (was ST 6.2.0 / TF 5.21.0 on 2026-10-26)
[ -f data/scifact.json ] && [ -f models.json ] || .venv_NEW/bin/python prep_data.py
for T in OLD MID NEW; do .venv_$T/bin/python embed.py $T 2>&1 | tee -a results_log_$T.txt; done
mkdir -p results; .venv_NEW/bin/python compare.py OLD NEW MID 2>&1 | tee results/compare_stdout.txt
