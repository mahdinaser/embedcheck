# embedcheck

Catch embedding-model regressions **before you re-index**: crashes, silent drift, tokenizer changes,
dtype changes and slowdowns across library upgrades.

From the audit in *Same Weights, Different Behavior* (2026): upgrading sentence-transformers 3.4.1 /
transformers 4.48.3 → 6.2.0 / 5.21.0, with the same pinned weights, regressed 22 of 90 popular
embedding models (10 crashes, 11 CPU slowdowns from fp16/bf16 checkpoint-dtype loading, 1 silent
tokenizer change that returned wrong vectors with no warning).

```bash
pip install "embedcheck[snapshot]"

# in your current environment
embedcheck snapshot BAAI/bge-small-en-v1.5 --revision <sha> -o before.json
# in the upgraded environment (another venv, container, or after pip install -U)
embedcheck snapshot BAAI/bge-small-en-v1.5 --revision <sha> -o after.json

embedcheck compare before.json after.json   # exit 1 on regression -> use in CI
```

Checks: load/encode failure (BREAK), embedding cosine vs golden vectors (default min 0.999) and exact
equality, token-id changes and `<unk>` rate, parameter dtype, max_seq_length, encode-time ratio.
`compare` needs only numpy. Snapshots are plain JSON you can commit next to your index.

Tips: pin `--dtype float32` (or the dtype your index was built with); pin `--revision`; treat
`trust_remote_code` models as code dependencies tied to a transformers version.
