"""EXPLORATORY R3 summary -> results/EXPLORATORY_slow_real.json (+ printed compact table)."""
import glob, json, os
todo = [l.split()[0] for l in open("explore/slow_real_todo.txt")]
CFG = ["OLD_1t", "NEW_1t", "NEW_fp32_1t", "OLD_4t", "NEW_4t", "NEW_fp32_4t"]
rows = []
for mid in todo:
    r = {"id": mid}
    for c in CFG:
        p = f"explore/slow_real/{c}__{mid.replace('/', '__')}.json"
        if not os.path.exists(p): r[c] = "NOT RUN"; continue
        d = json.load(open(p)); r[c] = {"dps": d["docs_per_sec"], "rss": d["peak_rss_mb"]} if "docs_per_sec" in d else d.get("error", "error")
    rows.append(r)
json.dump(rows, open("results/EXPLORATORY_slow_real.json", "w"), indent=1)
def f(v):
    if isinstance(v, dict): return f"{v['dps']}"
    if v == "NOT RUN": return "NR"
    return "TO" if "limit 3600s" in str(v) else "CUT"  # CUT = stopped early by the nightly deadline, not a real timeout
g = lambda v: f"{v['rss']:.0f}" if isinstance(v, dict) else "-"
for r in rows:
    print(f"{r['id'].split('/')[-1][:28]} | 1t {f(r['OLD_1t'])}/{f(r['NEW_1t'])}/{f(r['NEW_fp32_1t'])} | 4t {f(r['OLD_4t'])}/{f(r['NEW_4t'])}/{f(r['NEW_fp32_4t'])} | RSS1t {g(r['OLD_1t'])}/{g(r['NEW_1t'])}/{g(r['NEW_fp32_1t'])}")
