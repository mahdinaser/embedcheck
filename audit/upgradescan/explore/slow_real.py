"""EXPLORATORY R3 (Cloud Claude msg #58): realistic throughput for a SLOW model.
Encodes the first 200 SciFact documents (truncated at the model's max length), batch 16,
after one excluded warm-up batch. Reports docs/sec and peak RSS. One config per process.
Usage: python slow_real.py <ENV> <fp32:0|1> <threads> <model_id> <sha>  -> explore/slow_real/<ENV><_fp32>_<threads>t__<safe>.json"""
import json, os, resource, sys, time
import torch
from sentence_transformers import SentenceTransformer

ENV, FP32, THREADS, MID, SHA = sys.argv[1], sys.argv[2] == "1", int(sys.argv[3]), sys.argv[4], sys.argv[5]
tag = f"{ENV}{'_fp32' if FP32 else ''}_{THREADS}t"
os.makedirs("explore/slow_real", exist_ok=True)
docs = [d["text"] for d in json.load(open(os.path.expanduser("~/vdrift/data/scifact.json")))["docs"][:200]]
torch.set_num_threads(THREADS)
kw = {"model_kwargs": {"torch_dtype": torch.float32}} if FP32 else {}
m = SentenceTransformer(MID, revision=SHA, device="cpu", trust_remote_code=True, **kw)
m.encode(docs[:16], batch_size=16, normalize_embeddings=True, show_progress_bar=False)  # warm-up batch, not timed
t = time.time()
m.encode(docs, batch_size=16, normalize_embeddings=True, show_progress_bar=False)
dt = time.time() - t
out = {"config": tag, "id": MID, "dtype": str(next(m.parameters()).dtype), "max_seq_length": m.max_seq_length,
       "seconds": round(dt, 2), "docs_per_sec": round(200 / dt, 3),
       "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)}
json.dump(out, open(f"explore/slow_real/{tag}__{MID.replace('/', '__')}.json", "w"), indent=1)
print(json.dumps(out), flush=True)
