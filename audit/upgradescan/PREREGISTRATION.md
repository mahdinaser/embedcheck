# UpgradeScan kill test: pre-registration (frozen 2026-10-27, before any run)
**Question.** For widely used embedding models, how often does upgrading from (sentence-transformers 3.4.1 / transformers 4.48.3) to (ST 6.2.0 / TF 5.21.0) cause a regression — keeping the same model commit, torch 2.14.1 and CPU?
**Population.** The top 100 Hugging Face models by all-time downloads with library `sentence-transformers` and pipeline_tag `sentence-similarity` or `feature-extraction`, as listed on the run date. Excluded and logged:
- models with more than 1.0B parameters (RAM limit),
- gated or private repos,
- repos without weights.
Each model is pinned to the commit SHA recorded at selection time.
**Probe (per model, per environment, run back to back).**
- Load with `trust_remote_code=True` and `revision=sha`.
- Encode 20 fixed sentences, normalized.
- Timing: 1 warm-up, then the median of 3 encodes, with `torch.set_num_threads(1)` in both environments.
- Record parameter dtype and any error. Per-probe timeout is 900 s.
**Per-model outcome (only for models that load in OLD).**
- BREAK: fails or errors in NEW.
- DRIFT: median same-sentence cosine < 0.99, or the embedding dimension changes.
- SLOW: NEW median encode time ≥ 3× OLD, or NEW times out while OLD does not.
- DTYPE: parameter dtype differs (reported, but not counted as a regression by itself).
- A model is REGRESSED if it is BREAK, DRIFT or SLOW.
**Decision.**
- **GO** (write the audit paper and tool) if ≥ 20% of the OLD-loadable models are REGRESSED.
- **KILL** if below 20%.
- Also reported: models that fail in both environments, and models that fail only in OLD (an upgrade fixes them).
**Caveat, noted up front.** The scan runs at the same time as another CPU job. OLD and NEW are probed back to back, single-threaded, to equalize contention, and SLOW uses a deliberately coarse 3× threshold.
