"""EXPLORATORY (Cloud Claude msg #52): summarize the tokenizer sweep -> results/EXPLORATORY_tokenizer.json"""
import glob, json, os

rows = []
for p in sorted(glob.glob("explore/tok/OLD/*.json")):
    a = json.load(open(p))
    q = p.replace("/OLD/", "/NEW/")
    b = json.load(open(q)) if os.path.exists(q) else {"ok": False, "error": "missing"}
    r = {"id": a["id"], "old_ok": a["ok"], "new_ok": b["ok"]}
    if a["ok"] and b["ok"]:
        diff_sents = sum(x != y for x, y in zip(a["input_ids"], b["input_ids"]))
        r.update(class_old=a["tok_class"], class_new=b["tok_class"], fast_old=a["is_fast"], fast_new=b["is_fast"],
                 vocab_old=a["vocab_size"], vocab_new=b["vocab_size"],
                 class_change=a["tok_class"] != b["tok_class"], fast_to_slow=a["is_fast"] and not b["is_fast"],
                 ids_differ_sents=diff_sents, unk_old=a["unk_frac"], unk_new=b["unk_frac"])
    else:
        r["error_old"] = a.get("error"); r["error_new"] = b.get("error")
    rows.append(r)
both = [r for r in rows if r["old_ok"] and r["new_ok"]]
summary = {
    "models_compared": len(both),
    "not_comparable": [(r["id"], r.get("error_old") or r.get("error_new")) for r in rows if not (r["old_ok"] and r["new_ok"])],
    "a_fast_to_slow": [r["id"] for r in both if r["fast_to_slow"]],
    "a_class_change": [(r["id"], r["class_old"], r["class_new"]) for r in both if r["class_change"]],
    "b_any_input_id_diff": [(r["id"], r["ids_differ_sents"]) for r in both if r["ids_differ_sents"]],
    "c_unk_frac_old_mean": sum((r["unk_old"] or 0) for r in both) / max(len(both), 1),
    "c_unk_frac_new_mean": sum((r["unk_new"] or 0) for r in both) / max(len(both), 1),
    "c_unk_increase": [(r["id"], r["unk_old"], r["unk_new"]) for r in both if (r["unk_new"] or 0) > (r["unk_old"] or 0)],
}
os.makedirs("results", exist_ok=True)
json.dump({"summary": summary, "rows": rows}, open("results/EXPLORATORY_tokenizer.json", "w"), indent=1)
print(json.dumps(summary, indent=1)[:4000])
