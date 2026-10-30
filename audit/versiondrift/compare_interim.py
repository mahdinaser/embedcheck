"""INTERIM copy of compare.py (Cloud Claude chat msg #31). Identical except it skips models still pending
(mxbai-large, qwen3-0.6b) and writes results/INTERIM_compare.json. Not the official result.
Usage: python compare_interim.py OLD NEW"""
PENDING = {"mxbai-large", "qwen3-0.6b"}
import json, sys, os, numpy as np
A, B = sys.argv[1], sys.argv[2]; MID = sys.argv[3] if len(sys.argv) > 3 else None
D = json.load(open("data/scifact.json")); docs = [d["id"] for d in D["docs"]]; qs = D["queries"]; qrels = D["qrels"]
os.makedirs("results", exist_ok=True)
def ndcg10(Q, X):
    S = Q @ X.T; top = np.argsort(-S, 1)[:, :10]; vals = []
    for i, q in enumerate(qs):
        rel = qrels[q["id"]]; g = [rel.get(docs[j], 0) for j in top[i]]
        dcg = sum(r/np.log2(k+2) for k, r in enumerate(g))
        ideal = sorted(rel.values(), reverse=True)[:10]; idcg = sum(r/np.log2(k+2) for k, r in enumerate(ideal))
        vals.append(dcg/idcg if idcg else 0)
    return 100*float(np.mean(vals)), top
def cmp(a, b):
    ea, eb = json.load(open(f"emb/{a}/_env.json")), json.load(open(f"emb/{b}/_env.json")); res = {}
    for name in ea["models"]:
        if name in PENDING: continue
        oa, ob = ea["models"][name].get("ok"), eb["models"].get(name, {}).get("ok")
        if oa and not ob: res[name] = {"status": "BREAK", "error": eb["models"].get(name, {}).get("error")}; continue
        if not oa: res[name] = {"status": "not_in_old"}; continue
        x, y = np.load(f"emb/{a}/{name}.npz"), np.load(f"emb/{b}/{name}.npz")
        if x["D"].shape != y["D"].shape: res[name] = {"status": "DIM_CHANGE", "old": x["D"].shape, "new": y["D"].shape, "drifted": True}; continue
        cos = np.r_[(x["D"]*y["D"]).sum(1), (x["Q"]*y["Q"]).sum(1)]
        n_aa, t_aa = ndcg10(x["Q"], x["D"]); n_bb, t_bb = ndcg10(y["Q"], y["D"]); n_ab, _ = ndcg10(y["Q"], x["D"])
        ov = float(np.mean([len(set(p) & set(q))/10 for p, q in zip(t_aa, t_bb)]))
        med = float(np.median(cos)); d = n_ab - n_aa
        res[name] = {"status": "ok", "cos_median": med, "cos_p01": float(np.percentile(cos, 1)), "cos_min": float(cos.min()),
                     "ndcg_old": n_aa, "ndcg_new": n_bb, "ndcg_cross": n_ab, "delta_cross": d, "top10_overlap": ov,
                     "maxlen_old": ea["models"][name].get("max_seq_length"), "maxlen_new": eb["models"][name].get("max_seq_length"),
                     "drifted": bool(med < 0.99 or abs(d) >= 1.0)}
    return {"envs": [{k: ea[k] for k in ("st","tf","torch","device")}, {k: eb[k] for k in ("st","tf","torch","device")}], "models": res}
R = {"primary": cmp(A, B)}
if MID: R["secondary"] = cmp(MID, B)
json.dump(R, open("results/INTERIM_compare.json", "w"), indent=1)
for k, r in R.items():
    print(f"\n== INTERIM {k} (pending skipped: {sorted(PENDING)}): {r['envs']}")
    print(f"{'model':20s} {'status':9s} {'cosMed':>8s} {'cosMin':>8s} {'nOld':>6s} {'nNew':>6s} {'nCross':>6s} {'dCross':>7s} {'ovl':>5s} drift")
    for n, v in r["models"].items():
        if v["status"] != "ok": print(f"{n:20s} {v['status']:9s} {v.get('error','') or ''}"[:160]); continue
        print(f"{n:20s} ok        {v['cos_median']:8.5f} {v['cos_min']:8.5f} {v['ndcg_old']:6.2f} {v['ndcg_new']:6.2f} {v['ndcg_cross']:6.2f} {v['delta_cross']:+7.2f} {v['top10_overlap']:5.3f} {v['drifted']}")
P = R["primary"]["models"]; comp = [v for v in P.values() if v["status"] in ("ok", "DIM_CHANGE")]
nd = sum(v.get("drifted", False) for v in comp); nb = sum(v["status"] == "BREAK" for v in P.values())
go = (len(comp) > 0 and nd/len(comp) >= 0.20) or nb >= 2
print(f"\nPRIMARY OLD vs NEW: drifted {nd}/{len(comp)}  breaks {nb}")
print("INTERIM DECISION (not official):", "GO" if go else "KILL")
