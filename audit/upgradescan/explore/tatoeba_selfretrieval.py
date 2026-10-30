"""EXPLORATORY R1b (Cloud Claude msg #63): index-corruption scenario on the 440 Tatoeba Mongolian sentences.
Index with one env's embeddings, query with the other env's embeddings of the SAME sentences; the correct hit is the identical sentence."""
import json
import numpy as np
out = []
for mid in ["gmunkhtur/paraphrase-multilingual-minilm-l12-v3-mn", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"]:
    s = mid.replace("/", "__")
    o = np.load(f"explore/tatoeba/OLD__{s}.npz")["mon"]; n = np.load(f"explore/tatoeba/NEW__{s}.npz")["mon"]
    def pr(q, idx):
        rank = np.argsort(-(q @ idx.T), 1); gold = np.arange(len(q))[:, None]
        return float((rank[:, :1] == gold).any(1).mean()), float((rank[:, :10] == gold).any(1).mean())
    r = {"id": mid, "n": len(o)}
    for name, q, idx in [("OLD->OLD (sanity)", o, o), ("index OLD, query NEW", n, o), ("index NEW, query OLD", o, n)]:
        p1, r10 = pr(q, idx); r[name] = {"P@1": p1, "R@10": r10}
    r["median_cos_same_sentence"] = float(np.median((o * n).sum(1)))
    out.append(r); print(json.dumps(r))
json.dump(out, open("results/EXPLORATORY_tatoeba_selfretrieval.json", "w"), indent=1)
