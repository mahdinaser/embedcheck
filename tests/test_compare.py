import base64, json, numpy as np
from embedcheck.compare import compare
from embedcheck.cli import main

def snap(E, ok=True, dtype="torch.float32", ids=None, t=1.0, err=None, cls="BertTokenizerFast"):
    s = {"model": "m", "revision": "r", "ok": ok, "param_dtype": dtype, "encode_s": t, "max_seq_length": 128,
         "tokenizer": {"class": cls, "is_fast": True, "vocab_size": 10, "unk_id": 3, "unk_rate": 0.0, "input_ids": ids or [[1, 2], [4, 5]]}}
    if ok: s["embeddings"] = {"shape": list(E.shape), "b64": base64.b64encode(E.astype(np.float32).tobytes()).decode()}
    else: s["error"] = err or "AttributeError: boom"
    return s

E = np.random.default_rng(0).normal(size=(2, 8)).astype(np.float32)

def test_identical(): assert compare(snap(E), snap(E))[0] == "OK"
def test_break(): assert compare(snap(E), snap(E, ok=False))[0] == "REGRESSED"
def test_fixed(): assert compare(snap(E, ok=False), snap(E))[0] == "FIXED"
def test_drift(): assert compare(snap(E), snap(E + 1.0))[0] == "REGRESSED"
def test_slow(): assert compare(snap(E), snap(E, t=5.0))[0] == "REGRESSED"
def test_dtype_warn(): assert compare(snap(E), snap(E, dtype="torch.float16"))[0] == "WARN"
def test_tokenization():
    st, F = compare(snap(E), snap(E, ids=[[1, 3], [4, 5]]))
    assert st == "REGRESSED" and any(f["code"] == "TOKENIZATION_CHANGED" for f in F)
def test_rename_only():
    st, F = compare(snap(E), snap(E, cls="BertTokenizer"))
    assert st == "OK" and any(f["code"] == "TOKENIZER_RENAMED" for f in F)
def test_cli_exit(tmp_path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    json.dump(snap(E), open(a, "w")); json.dump(snap(E, ok=False), open(b, "w"))
    assert main(["compare", str(a), str(b)]) == 1
