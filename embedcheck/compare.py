"""Compare two snapshots. Pure numpy; no ML libraries needed."""
import base64
import numpy as np

DEFAULTS = {"min_cosine": 0.999, "max_slowdown": 2.0}

def _arr(e):
    return np.frombuffer(base64.b64decode(e["b64"]), dtype=np.float32).reshape(e["shape"])

def compare(a, b, min_cosine=DEFAULTS["min_cosine"], max_slowdown=DEFAULTS["max_slowdown"]):
    """Return (status, findings). status in {OK, WARN, REGRESSED, BOTH_FAIL, FIXED}."""
    F = []
    def add(level, code, msg): F.append({"level": level, "code": code, "msg": msg})
    if a.get("model") != b.get("model"): add("WARN", "MODEL_MISMATCH", f"{a.get('model')} vs {b.get('model')}")
    if a.get("revision") != b.get("revision"): add("WARN", "REVISION_MISMATCH", f"{a.get('revision')} vs {b.get('revision')}")
    if not a.get("ok") and not b.get("ok"): add("FAIL", "BOTH_FAIL", f"A: {a.get('error')} | B: {b.get('error')}"); return "BOTH_FAIL", F
    if not a.get("ok"): add("INFO", "FIXED", f"A failed, B loads: {a.get('error')}"); return "FIXED", F
    if not b.get("ok"): add("FAIL", "BREAK", b.get("error", "")); return "REGRESSED", F
    if a.get("param_dtype") != b.get("param_dtype"):
        add("WARN", "DTYPE_CHANGE", f"{a.get('param_dtype')} -> {b.get('param_dtype')} (pin torch_dtype to keep it stable)")
    ta, tb = a.get("tokenizer"), b.get("tokenizer")
    if ta and tb:
        if ta["input_ids"] != tb["input_ids"]:
            nd = sum(x != y for x, y in zip(ta["input_ids"], tb["input_ids"]))
            add("FAIL", "TOKENIZATION_CHANGED", f"{nd}/{len(ta['input_ids'])} sentences tokenize differently; "
                f"unk rate {ta.get('unk_rate')} -> {tb.get('unk_rate')}; class {ta['class']} -> {tb['class']}")
        elif ta["class"] != tb["class"]:
            add("INFO", "TOKENIZER_RENAMED", f"{ta['class']} -> {tb['class']} (ids identical)")
    if a.get("max_seq_length") != b.get("max_seq_length"):
        add("WARN", "MAX_SEQ_LENGTH_CHANGE", f"{a.get('max_seq_length')} -> {b.get('max_seq_length')}")
    x, y = _arr(a["embeddings"]), _arr(b["embeddings"])
    if x.shape != y.shape:
        add("FAIL", "DIM_CHANGE", f"{x.shape} -> {y.shape}")
    else:
        exact = bool(np.array_equal(x, y))
        cos = (x * y).sum(1) / (np.linalg.norm(x, axis=1) * np.linalg.norm(y, axis=1) + 1e-12)
        stats = f"exact={exact} cos_min={cos.min():.6f} cos_median={np.median(cos):.6f} max_abs_diff={np.abs(x - y).max():.3e}"
        if cos.min() < min_cosine: add("FAIL", "EMBEDDING_DRIFT", stats)
        elif not exact: add("INFO", "NUMERIC_JITTER", stats)
        else: add("INFO", "BIT_IDENTICAL", stats)
    sa, sb = a.get("encode_s"), b.get("encode_s")
    if sa and sb:
        r = sb / sa
        if r >= max_slowdown: add("FAIL", "SLOWDOWN", f"{r:.1f}x slower ({sa:.3f}s -> {sb:.3f}s, threads {a.get('threads')}/{b.get('threads')})")
        elif r <= 1 / max_slowdown: add("INFO", "SPEEDUP", f"{1/r:.1f}x faster")
    lv = {f["level"] for f in F}
    return ("REGRESSED" if "FAIL" in lv else "WARN" if "WARN" in lv else "OK"), F
