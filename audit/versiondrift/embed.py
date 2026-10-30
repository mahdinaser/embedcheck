"""Usage: python embed.py <ENV_TAG> [model ...]   Writes emb/<ENV_TAG>/<model>.npz and emb/<ENV_TAG>/_env.json"""
import json, sys, os, time, traceback, platform, numpy as np, torch
import sentence_transformers, transformers
from sentence_transformers import SentenceTransformer
TAG = sys.argv[1]; only = sys.argv[2:]
D = json.load(open("data/scifact.json")); MODELS = json.load(open("models.json"))
out = f"emb/{TAG}"; os.makedirs(out, exist_ok=True)
dev = "cuda" if torch.cuda.is_available() else "cpu"
env = {"tag": TAG, "st": sentence_transformers.__version__, "tf": transformers.__version__, "torch": torch.__version__,
       "python": platform.python_version(), "device": dev, "models": {}}
envf = f"{out}/_env.json"
if os.path.exists(envf): env["models"] = json.load(open(envf)).get("models", {})
torch.manual_seed(0)
for name, m in MODELS.items():
    if only and name not in only: continue
    t0 = time.time()
    try:
        model = SentenceTransformer(m["repo"], revision=m["sha"], device=dev, trust_remote_code=True)
        model.eval()
        enc = lambda xs: model.encode(xs, batch_size=32, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False).astype(np.float32)
        Q = enc([m["qp"] + q["text"] for q in D["queries"]])
        Dm = enc([m["dp"] + d["text"] for d in D["docs"]])
        np.savez_compressed(f"{out}/{name}.npz", Q=Q, D=Dm)
        env["models"][name] = {"ok": True, "max_seq_length": getattr(model, "max_seq_length", None), "dim": int(Q.shape[1]), "sec": round(time.time()-t0, 1)}
    except Exception as e:
        env["models"][name] = {"ok": False, "error": f"{type(e).__name__}: {str(e)[:400]}"}
        traceback.print_exc()
    print(TAG, name, env["models"][name], flush=True)
    json.dump(env, open(envf, "w"), indent=1)
    if dev == "cuda": torch.cuda.empty_cache()
