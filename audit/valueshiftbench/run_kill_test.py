"""Kill test runner. Requires: sentence-transformers, transformers, torch (CPU), numpy, scikit-learn.
Usage: python run_kill_test.py data/vsb_kill_v0.json results/"""
import json, sys, os, numpy as np
from sklearn.metrics import roc_auc_score
DATA, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
items = json.load(open(DATA)); rng = np.random.default_rng(0)
EMBEDDERS = {"MiniLM":"sentence-transformers/all-MiniLM-L6-v2","BGE-small":"BAAI/bge-small-en-v1.5",
  "E5-small":"intfloat/e5-small-v2","GTE-small":"thenlper/gte-small",
  "Nomic-v1.5":"nomic-ai/nomic-embed-text-v1.5","Qwen3-0.6B":"Qwen/Qwen3-Embedding-0.6B"}
PREFIX = {"E5-small":"query: ","Nomic-v1.5":"search_document: "}

def boot(x, f, B=2000):
    x = np.asarray(x); idx = rng.integers(0, len(x), (B, len(x)))
    v = np.array([f(x[i]) for i in idx]); return float(np.percentile(v,2.5)), float(np.percentile(v,97.5))

def metrics(sp, su, sup, types):
    sp, su, sup = map(np.asarray, (sp, su, sup)); res = {}
    def block(mask):
        p, u, q = sp[mask], su[mask], sup[mask]
        tau = np.percentile(p, 10)
        return dict(n=int(mask.sum()), WIN=float((p>u).mean()), WIN_ci=boot(p>u, np.mean),
                    AUROC=float(roc_auc_score(np.r_[np.ones(len(p)),np.zeros(len(u))], np.r_[p,u])),
                    COLLISION90=float((u>=tau).mean()), COLLISION90_para=float((q>=tau).mean()),
                    mean_cos_para=float(p.mean()), mean_cos_upd=float(u.mean()))
    res["all"] = block(np.ones(len(sp),bool))
    for t in sorted(set(types)): res[t] = block(np.array(types)==t)
    return res

types = [it["change_type"] for it in items]; out = {}
from sentence_transformers import SentenceTransformer
for name, path in EMBEDDERS.items():
    m = SentenceTransformer(path, device="cpu", trust_remote_code=True)
    pre = PREFIX.get(name, "")
    enc = lambda xs: m.encode([pre+x for x in xs], normalize_embeddings=True, batch_size=32)
    O, P, U, UP = (enc([it[k] for it in items]) for k in ["original","paraphrase","update_min","update_para"])
    sp, su, sup = (O*P).sum(1), (O*U).sum(1), (O*UP).sum(1)
    out[name] = metrics(sp, su, sup, types); print(name, out[name]["all"], flush=True)
    np.savez(f"{OUT}/{name}_scores.npz", sp=sp, su=su, sup=sup)
# BM25-style token overlap (Jaccard) baseline
tok = lambda s: set(s.lower().replace(".","").replace(",","").split())
jac = lambda a,b: len(tok(a)&tok(b))/len(tok(a)|tok(b))
out["TokenJaccard"] = metrics([jac(i["original"],i["paraphrase"]) for i in items],
    [jac(i["original"],i["update_min"]) for i in items], [jac(i["original"],i["update_para"]) for i in items], types)
# NLI cross-encoder: score = 1 - P(contradiction)
from sentence_transformers import CrossEncoder
ce = CrossEncoder("cross-encoder/nli-deberta-v3-small", device="cpu")
def ncs(pairs):
    lg = ce.predict(pairs, apply_softmax=True); return 1 - lg[:,0]   # label 0 = contradiction for this model
out["NLI-deberta-small"] = metrics(ncs([(i["original"],i["paraphrase"]) for i in items]),
    ncs([(i["original"],i["update_min"]) for i in items]), ncs([(i["original"],i["update_para"]) for i in items]), types)
json.dump(out, open(f"{OUT}/kill_test_results.json","w"), indent=1)
emb = [n for n in EMBEDDERS]
coll = np.median([out[n]["all"]["COLLISION90"] for n in emb]); auc = np.median([out[n]["all"]["AUROC"] for n in emb])
low_win = sum(out[n]["all"]["WIN"] < 0.70 for n in emb)
go = coll >= 0.30 and low_win >= 4 and auc < 0.90
print(f"\nmedian COLLISION@90={coll:.3f}  median AUROC={auc:.3f}  embedders with WIN<0.70: {low_win}/6  NLI AUROC={out['NLI-deberta-small']['all']['AUROC']:.3f}")
print("DECISION:", "GO" if go else "KILL")
