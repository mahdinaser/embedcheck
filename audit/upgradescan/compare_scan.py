"""Usage: python compare_scan.py  (numpy only) -> results/scan_compare.json, prints table + DECISION"""
import json, os, numpy as np
M = json.load(open("scan_models.json")); rows = []
def load(tag, mid):
    p = f"scan/{tag}/{mid.replace('/','__')}"
    return (json.load(open(p+".json")) if os.path.exists(p+".json") else None), p
for m in M:
    a, pa = load("OLD", m["id"]); b, pb = load("NEW", m["id"])
    r = {"id": m["id"], "remote_code": m["remote_code"], "downloads": m["downloads"]}
    if a is None or b is None: r["status"] = "missing"; rows.append(r); continue
    oa, ob = a["ok"], b["ok"]
    if not oa: r["status"] = "fails_both" if not ob else "fails_old_only"; r["err_old"] = a.get("error"); rows.append(r); continue
    to_b = "Timeout" in (b.get("error") or "")
    if not ob and not to_b: r.update(status="BREAK", err_new=b.get("error")); rows.append(r); continue
    if to_b: r.update(status="SLOW", note="NEW timeout"); rows.append(r); continue
    x, y = np.load(pa+".npy"), np.load(pb+".npy")
    if x.shape != y.shape: r.update(status="DRIFT", note=f"dim {x.shape}->{y.shape}"); rows.append(r); continue
    cos = (x*y).sum(1) / (np.linalg.norm(x,axis=1)*np.linalg.norm(y,axis=1)); med = float(np.median(cos))
    ratio = b["encode_s"]/max(a["encode_s"], 1e-6)
    r.update(cos_med=med, cos_min=float(cos.min()), slow_ratio=ratio, dtype_old=a["dtype"], dtype_new=b["dtype"],
             DTYPE=a["dtype"] != b["dtype"])
    r["status"] = "DRIFT" if med < 0.99 else ("SLOW" if ratio >= 3 else "ok")
    rows.append(r)
os.makedirs("results", exist_ok=True); json.dump(rows, open("results/scan_compare.json","w"), indent=1)
base = [r for r in rows if r["status"] in ("ok","BREAK","DRIFT","SLOW")]
reg = [r for r in base if r["status"] != "ok"]
from collections import Counter
print("status counts:", dict(Counter(r["status"] for r in rows)))
print("DTYPE changes among ok-in-both:", sum(r.get("DTYPE", False) for r in rows))
print("remote_code among REGRESSED:", sum(r["remote_code"] for r in reg), "/", len(reg), "; remote_code overall:", sum(r["remote_code"] for r in base), "/", len(base))
for r in reg: print(f"  {r['status']:5s} {r['id']}  {r.get('err_new') or r.get('note') or ('cos=%.4f ratio=%.1f' % (r.get('cos_med',0), r.get('slow_ratio',0)))}"[:220])
frac = len(reg)/len(base) if base else 0
print(f"\nREGRESSED {len(reg)}/{len(base)} = {frac:.1%}")
print("DECISION:", "GO" if frac >= 0.20 else "KILL")
