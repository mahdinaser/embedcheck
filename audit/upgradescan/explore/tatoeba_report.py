"""EXPLORATORY R1 report: P@1 for mon->eng bitext mining, OLD / NEW / cross (OLD eng index, NEW mon queries)."""
import json
import numpy as np
out = []
for mid in ["gmunkhtur/paraphrase-multilingual-minilm-l12-v3-mn", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"]:
    s = mid.replace("/", "__")
    o = np.load(f"explore/tatoeba/OLD__{s}.npz"); n = np.load(f"explore/tatoeba/NEW__{s}.npz")
    jo = json.load(open(f"explore/tatoeba/OLD__{s}.json")); jn = json.load(open(f"explore/tatoeba/NEW__{s}.json"))
    p1 = lambda q, idx: float(((q @ idx.T).argmax(1) == np.arange(len(q))).mean())
    r = {"id": mid, "n_pairs": jo["n_pairs"], "source": jo["source"],
         "P@1_OLD": p1(o["mon"], o["eng"]), "P@1_NEW": p1(n["mon"], n["eng"]), "P@1_cross_NEWmon_OLDeng": p1(n["mon"], o["eng"]),
         "unk_rate_mon_OLD": jo["unk_rate_mon"], "unk_rate_mon_NEW": jn["unk_rate_mon"],
         "eng_side_equal": bool(np.array_equal(o["eng"], n["eng"])), "mon_side_equal": bool(np.array_equal(o["mon"], n["mon"]))}
    out.append(r); print(json.dumps(r))
json.dump(out, open("results/EXPLORATORY_tatoeba_mon_eng.json", "w"), indent=1)
