"""Run once in .venv_NEW. Writes scan_models.json (top-100 eligible, pinned SHAs) + scan_excluded.json."""
import json
from huggingface_hub import HfApi
api = HfApi(); picked, excl = [], []
for m in api.list_models(library="sentence-transformers", sort="downloads", direction=-1, limit=600, full=False):
    if len(picked) >= 100: break
    tag = getattr(m, "pipeline_tag", None)
    if tag not in ("sentence-similarity", "feature-extraction"): continue
    try:
        info = api.model_info(m.id, files_metadata=False, securityStatus=False)
    except Exception as e:
        excl.append({"id": m.id, "why": f"info_error: {type(e).__name__}"}); continue
    if getattr(info, "gated", False) or getattr(info, "private", False): excl.append({"id": m.id, "why": "gated/private"}); continue
    files = [s.rfilename for s in (info.siblings or [])]
    if not any(f.endswith((".safetensors", ".bin")) for f in files): excl.append({"id": m.id, "why": "no_weights"}); continue
    n = None
    st = getattr(info, "safetensors", None)
    if st is not None: n = getattr(st, "total", None)
    if n is not None and n > 1_000_000_000: excl.append({"id": m.id, "why": f"params={n}"}); continue
    picked.append({"id": m.id, "sha": info.sha, "downloads": getattr(info, "downloads", None), "params": n,
                   "remote_code": any(f.endswith(".py") for f in files), "pipeline_tag": tag})
json.dump(picked, open("scan_models.json", "w"), indent=1); json.dump(excl, open("scan_excluded.json", "w"), indent=1)
print(len(picked), "picked;", len(excl), "excluded;", sum(p["remote_code"] for p in picked), "ship .py files")
