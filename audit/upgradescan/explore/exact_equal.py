"""EXPLORATORY R2 (Cloud Claude msg #58): exact float32 equality OLD vs NEW.
Scan: 68 'ok' models (20-sentence .npy). SciFact: the 10 fp32 models ok in both VersionDrift envs (Q and D)."""
import glob, json, os
import numpy as np
out = {"scan": [], "scifact": []}
for r in json.load(open("results/scan_compare.json")):
    if r["status"] != "ok": continue
    s = r["id"].replace("/", "__"); x = np.load(f"scan/OLD/{s}.npy"); y = np.load(f"scan/NEW/{s}.npy")
    out["scan"].append({"id": r["id"], "equal": bool(np.array_equal(x, y)), "max_abs_diff": float(np.abs(x - y).max()) if x.shape == y.shape else None})
V = os.path.expanduser("~/vdrift")
eo = json.load(open(f"{V}/emb/OLD/_env.json"))["models"]; en = json.load(open(f"{V}/emb/NEW/_env.json"))["models"]
for name in eo:
    if not (eo[name].get("ok") and en.get(name, {}).get("ok")) or name in ("gte-small", "gte-base"): continue
    a = np.load(f"{V}/emb/OLD/{name}.npz"); b = np.load(f"{V}/emb/NEW/{name}.npz")
    out["scifact"].append({"model": name, "Q_equal": bool(np.array_equal(a["Q"], b["Q"])), "D_equal": bool(np.array_equal(a["D"], b["D"])),
                           "max_abs_diff": float(max(np.abs(a["Q"] - b["Q"]).max(), np.abs(a["D"] - b["D"]).max()))})
os.makedirs("results", exist_ok=True); json.dump(out, open("results/EXPLORATORY_exact_equal.json", "w"), indent=1)
ne = [r for r in out["scan"] if not r["equal"]]
print("scan: exactly equal", len(out["scan"]) - len(ne), "/", len(out["scan"]))
for r in sorted(ne, key=lambda r: -r["max_abs_diff"]): print(f"  not equal: {r['id']}  max|diff|={r['max_abs_diff']:.3e}")
print("scifact fp32 models:", len(out["scifact"]))
for r in out["scifact"]: print(f"  {r['model']:18s} Q_equal={r['Q_equal']} D_equal={r['D_equal']} max|diff|={r['max_abs_diff']:.3e}")
