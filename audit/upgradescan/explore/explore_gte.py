"""EXPLORATORY (Cloud Claude msg #48): is the Alibaba-NLP/gte-base-en-v1.5 IndexError in NEW
deterministic, and does any successful forward pass give non-deterministic output?
Each call is a fresh process. Usage: python explore_gte.py <TAG> <RUN>  -> explore/gte_<TAG>_<RUN>.json"""
import hashlib, json, sys, traceback
import numpy as np, torch, transformers, sentence_transformers
from sentence_transformers import SentenceTransformer

TAG, RUN = sys.argv[1], sys.argv[2]
MID = "Alibaba-NLP/gte-base-en-v1.5"
SHA = next(m["sha"] for m in json.load(open("scan_models.json")) if m["id"] == MID)
CASES = {
    "short": ["Hi."],
    "mixed3": ["Hi.", "The train to Boston departs at 9 am.",
               "Climate change increases the frequency and intensity of heatwaves across many regions of the world, "
               "with consequences for agriculture, health and infrastructure."],
    "scan20_first3": ["The cat sat on the mat.", "Quantum computing uses qubits to perform calculations.",
                      "How do I reset my router password?"],
}
torch.set_num_threads(1)
out = {"tag": TAG, "run": RUN, "st": sentence_transformers.__version__, "tf": transformers.__version__, "cases": {}}
try:
    m = SentenceTransformer(MID, revision=SHA, device="cpu", trust_remote_code=True)
    out["load"] = "ok"
    for name, sents in CASES.items():
        r = {}
        for rep in range(2):  # two passes in the same process
            try:
                E = m.encode(sents, normalize_embeddings=True, convert_to_numpy=True)
                r[f"pass{rep}"] = {"ok": True, "sha": hashlib.sha256(E.astype(np.float32).tobytes()).hexdigest()[:16],
                                   "first": [round(float(v), 6) for v in E[0, :3]]}
            except Exception as e:
                r[f"pass{rep}"] = {"ok": False, "error": f"{type(e).__name__}: {str(e)[:200]}",
                                   "tb_tail": traceback.format_exc()[-700:]}
        out["cases"][name] = r
except Exception as e:
    out["load"] = f"{type(e).__name__}: {str(e)[:300]}"
    out["tb_tail"] = traceback.format_exc()[-700:]
json.dump(out, open(f"explore/gte_{TAG}_{RUN}.json", "w"), indent=1)
print(TAG, RUN, out["load"], {k: {p: (v["sha"] if v["ok"] else v["error"][:80]) for p, v in c.items()} for k, c in out["cases"].items()})
