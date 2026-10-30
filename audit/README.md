# Audit scripts for *Same Weights, Different Behavior*

These are the scripts exactly as they ran to produce `data/`. Each experiment has two kinds:

- **Pre-registered originals**, frozen before the run and used unchanged.
- **Local additions**, written during the run, each documented in its header. They are of three kinds:
  - resume or ordering wrappers that do not change any computation;
  - copies of an original that differ by a stated line or two;
  - exploratory analyses that do not count toward any pre-registered decision.

Paths assume the experiment folders were `~/vscan`, `~/vdrift` and `~/valueshiftbench`, with the three
virtual environments in `~/vdrift/.venv_{OLD,MID,NEW}`.

## upgradescan/ (data: `data/upgradescan/`)

Pre-registered originals: `PREREGISTRATION.md`, `select_models.py`, `probe.py`, `compare_scan.py`, `run_scan.sh`.
`select_models.py` was run in `.venv_OLD`, because NEW's huggingface_hub rejects `list_models(library=...)`.

Local additions, all exploratory:

| File | Purpose |
|---|---|
| `explore/explore_drift.py` | Root-cause dump for the DRIFT model: modules, pooling, tokenizer, input_ids |
| `explore/explore_gte.py` | Determinism and crash test for Alibaba gte-base-en-v1.5 in NEW |
| `explore/tok_probe.py`, `tok_sweep.sh`, `tok_summary.py` | Tokenizer sweep over 86 models → `EXPLORATORY_tokenizer.json` |
| `explore/tok_mechanism.py` | Tokenizer files vs. built backend for the DRIFT model |
| `explore/probe_fp32.py` | `probe.py` plus `model_kwargs={"torch_dtype": float32}` (one line) → `scan/NEW_fp32/` |
| `explore/slow_fp32.sh` | Runner for `probe_fp32.py` on the 11 SLOW models |
| `explore/slow_real.py`, `slow_real.sh`, `slow_real2.sh`, `slow_real_summary.py` | R3 throughput and peak RSS on 200 SciFact docs |
| `explore/exact_equal.py` | R2 exact float32 equality |
| `explore/tatoeba.py`, `tatoeba_report.py`, `tatoeba_selfretrieval.py` | R1 / R1b Tatoeba mon-eng tests |
| `embedcheck_validation/run_ec.sh` | Snapshot and compare of 22 regressed + 10 control models with embedcheck |

## versiondrift/ (data: `data/versiondrift/`)

Pre-registered originals: `PREREGISTRATION.md`, `prep_data.py`, `embed.py`, `compare.py`, `run_all.sh`.

Local additions:

| File | Kind | What differs |
|---|---|---|
| `embed_resume.py` | resume copy of `embed.py` | Skips models already recorded; atomic writes. Computation unchanged |
| `embed_fp32.py`, `embed_fp32_resume.py` | exploratory copy | `embed.py` plus `torch_dtype=float32` (one line) |
| `compare_interim.py` | interim copy of `compare.py` | Skips pending models (mxbai-large, qwen3-0.6b); writes `INTERIM_*`. This is the reported primary table |
| `compare_exploratory.py` | exploratory copy | Compares only gte-small and gte-base → `EXPLORATORY_fp32_*` |
| `continue_order.sh`, `continue_order2.sh`, `handoff_after_gte_base.sh`, `resume_all.sh` | order-only wrappers | Run the same commands in a changed order, and survive the nightly reboot |

## valueshiftbench/ (data: `data/valueshiftbench/`)

Pre-registered originals: `gen_triples.py`, `run_kill_test.py`. Run with transformers 4.57.6 and
sentence-transformers 5.7.0; attempt 1 under transformers 5.21 crashed at Nomic.
