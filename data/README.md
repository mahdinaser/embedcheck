# Data for *Same Weights, Different Behavior*

Raw outputs of the experiments behind the paper. Environments throughout:
OLD = sentence-transformers 3.4.1 / transformers 4.48.3, MID = 4.1.0 / 4.51.3,
NEW = 6.2.0 / 5.21.0; all with torch 2.14.1+cpu, Python 3.12.3, CPU only
(Intel i7-6700, 4 cores, Ubuntu 24.04 under WSL2). Local home paths in error
messages and tracebacks were replaced with `~` before release; nothing else was edited.

## upgradescan/ — pre-registered compatibility scan (decision: GO, 22/90 regressed)

| File | Contents |
|---|---|
| `PREREGISTRATION.md` | Frozen protocol and decision rule |
| `scan_models.json` | The 100 selected models with pinned commit SHAs, downloads, params, remote-code flag |
| `scan_excluded.json` | 17 excluded models and the reason (>1.0B params, no weights, gated) |
| `deviations.txt` | Infrastructure deviations (see below) |
| `scan/OLD/*.json`, `scan/NEW/*.json` | Per-model probe records: versions, load time, parameter dtype, encode time, dim, error + traceback tail. Embedding arrays (`.npy`) are not included |
| `scan/NEW_fp32/*.json` | Exploratory: the 11 SLOW models re-probed in NEW with `torch_dtype=float32` |
| `results/scan_compare.json` | Per-model outcome (BREAK / DRIFT / SLOW / ok / fails_old_only / fails_both) |
| `results/scan_stdout.txt` | Output of `compare_scan.py` including the DECISION line |
| `results/EXPLORATORY_scan_rows.csv` | One row per model: status, family, root cause, downloads, remote_code |
| `results/EXPLORATORY_tokenizer.json` | Tokenizer class / is_fast / vocab / input_ids, OLD vs NEW, 86 models |
| `results/EXPLORATORY_slow_fp32.json` | fp32-forced timing and cosine for the 11 SLOW models |
| `results/EXPLORATORY_slow_real.json` | Throughput (docs/sec) and peak RSS on 200 SciFact docs, OLD / NEW / NEW-fp32, 1 and 4 threads |
| `results/EXPLORATORY_exact_equal.json` | Exact float32 equality OLD vs NEW (scan models and SciFact models) |
| `results/EXPLORATORY_tatoeba_mon_eng.json` | Tatoeba mon→eng bitext mining for the tokenizer case and a control |
| `results/EXPLORATORY_tatoeba_selfretrieval.json` | Index-with-OLD / query-with-NEW self-retrieval on the same sentences |
| `results/EXPLORATORY_embedcheck_validation.json` | embedcheck vs scan labels for 22 regressed + 10 control models |

## versiondrift/ — pre-registered SciFact retrieval test (decision: GO, via 2 BREAKs)

| File | Contents |
|---|---|
| `PREREGISTRATION.md` | Frozen protocol and decision rule |
| `order_change_note.txt` | Log of the order-only changes to the run sequence |
| `env/{OLD,NEW,NEW_fp32}_env.json` | Per-model load status, dim, max_seq_length, runtime, errors |
| `results/INTERIM_compare.json` / `_stdout.txt` | OLD vs NEW for the 14 recorded models (cosine, nDCG@10 old/new/cross, top-10 overlap, drift flag) |
| `results/EXPLORATORY_fp32_compare.json` / `_stdout.txt` | gte-small and gte-base re-embedded in NEW with fp32 forced |

## valueshiftbench/

`kill_test_results.json` — the earlier ValueShiftBench kill test (decision: KILL).

## Known deviations

- **VersionDrift: mxbai-large not embedded in NEW.** In fp16 it was projected at ~21–22 h on this CPU, longer
  than the window between the machine's nightly reboots, so the run was dropped. The reported result is the
  INTERIM comparison with mxbai-large excluded. The official `compare.py` would count it as a BREAK.
  The decision (GO, 2 BREAKs) does not depend on it.
- **VersionDrift: Qwen3-Embedding-0.6B fails to load in OLD** (`qwen3` architecture unknown to transformers
  4.48.3) and is `not_in_old`, as anticipated by the pre-registration. It was not embedded in NEW or MID.
- **VersionDrift: MID environment not run.** The secondary MID-vs-NEW contrast is absent.
- **UpgradeScan: `select_models.py` ran in the OLD environment.** NEW's huggingface_hub 2.3.0 rejects
  `list_models(library=...)`. The script itself was unchanged; this affects model selection only.
- **UpgradeScan: `results/scan_stdout.txt` was recovered from the run log.** `run_scan.sh` piped into
  `results/` before that directory existed.
- **R3 (`EXPLORATORY_slow_real.json`): timeouts.** For the 6 large models, NEW at 1 thread hit the 3600 s
  per-job cap. These entries are recorded as errors, and their ratios are lower bounds only.
- **R3: deadline cut-off.** One NEW 1-thread job was cut by a nightly deadline after 786 s and was later
  re-run in full. The cut record was excluded from the data.
- All `EXPLORATORY_*` files are post-hoc analyses and do not count toward either pre-registered decision.
