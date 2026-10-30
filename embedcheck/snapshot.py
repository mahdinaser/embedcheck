"""Snapshot a model in the *current* Python environment. Requires sentence-transformers."""
import base64, json, platform, time, traceback

def _b64(a):
    import numpy as np
    a = np.ascontiguousarray(a, dtype=np.float32)
    return {"shape": list(a.shape), "b64": base64.b64encode(a.tobytes()).decode()}

def take_snapshot(model_id, revision=None, sentences=None, dtype=None, trust_remote_code=False,
                  device="cpu", threads=None, repeats=3, prompt=""):
    from .sentences import DEFAULT_SENTENCES
    sentences = list(sentences or DEFAULT_SENTENCES)
    snap = {"embedcheck": 1, "model": model_id, "revision": revision, "requested_dtype": dtype,
            "python": platform.python_version(), "platform": platform.platform(), "ok": False,
            "n_sentences": len(sentences), "prompt": prompt}
    try:
        import numpy as np, torch, transformers, sentence_transformers
        from sentence_transformers import SentenceTransformer
        snap.update(torch=torch.__version__, transformers=transformers.__version__,
                    sentence_transformers=sentence_transformers.__version__, device=device)
        if threads: torch.set_num_threads(int(threads))
        snap["threads"] = torch.get_num_threads()
        kw = {}
        if dtype: kw["model_kwargs"] = {"torch_dtype": getattr(torch, dtype)}
        t0 = time.time()
        m = SentenceTransformer(model_id, revision=revision, device=device, trust_remote_code=trust_remote_code, **kw)
        snap["load_s"] = round(time.time() - t0, 3)
        snap["param_dtype"] = str(next(m.parameters()).dtype)
        snap["max_seq_length"] = getattr(m, "max_seq_length", None)
        tok = getattr(m, "tokenizer", None)
        if tok is not None:
            ids = [tok(prompt + s)["input_ids"] for s in sentences]
            unk = getattr(tok, "unk_token_id", None)
            n = sum(len(x) for x in ids)
            snap["tokenizer"] = {"class": type(tok).__name__, "is_fast": bool(getattr(tok, "is_fast", False)),
                                 "vocab_size": len(tok), "unk_id": unk, "input_ids": ids,
                                 "unk_rate": (sum(t == unk for x in ids for t in x) / n) if (unk is not None and n) else None}
        enc = lambda: m.encode([prompt + s for s in sentences], batch_size=len(sentences),
                               normalize_embeddings=False, convert_to_numpy=True, show_progress_bar=False)
        E = enc(); ts = []
        for _ in range(max(1, repeats)):
            t = time.time(); enc(); ts.append(time.time() - t)
        snap["encode_s"] = float(sorted(ts)[len(ts) // 2])
        snap["embeddings"] = _b64(E); snap["ok"] = True
    except BaseException as e:  # record, never raise: a failure is a result
        snap["error"] = f"{type(e).__name__}: {str(e)[:800]}"
        snap["traceback_tail"] = traceback.format_exc()[-1500:]
    return snap
