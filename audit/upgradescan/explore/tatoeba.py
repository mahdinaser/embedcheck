"""EXPLORATORY R1 (Cloud Claude msg #58): Tatoeba mon-eng bitext mining, OLD vs NEW.
Embeds both sides with the pinned scan revision and saves them; analysis is in tatoeba_report.py.
Usage: python tatoeba.py <TAG>  -> explore/tatoeba/<TAG>__<model>.npz and <TAG>__<model>.json"""
import json, os, sys
import numpy as np, torch
from sentence_transformers import SentenceTransformer

TAG = sys.argv[1]
MODELS = ["gmunkhtur/paraphrase-multilingual-minilm-l12-v3-mn",
          "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"]
SHAS = {m["id"]: m["sha"] for m in json.load(open("scan_models.json"))}
os.makedirs("explore/tatoeba", exist_ok=True)

def load_pairs():
    from datasets import load_dataset
    try:
        ds = load_dataset("mteb/tatoeba-bitext-mining", "mon-eng", split="test")
        return [r["sentence1"] for r in ds], [r["sentence2"] for r in ds], "mteb/tatoeba-bitext-mining mon-eng test"
    except Exception as e:
        print("mteb dataset failed:", type(e).__name__, str(e)[:200])
        ds = load_dataset("Helsinki-NLP/tatoeba", lang1="en", lang2="mn", split="train", trust_remote_code=True)
        pairs = [r["translation"] for r in ds][:1000]
        return [p["mn"] for p in pairs], [p["en"] for p in pairs], "Helsinki-NLP/tatoeba en-mn train (first 1000)"

mon, eng, source = load_pairs()
torch.set_num_threads(4)
for mid in MODELS:
    m = SentenceTransformer(mid, revision=SHAS[mid], device="cpu", trust_remote_code=True)
    enc = lambda xs: m.encode(xs, batch_size=32, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False).astype(np.float32)
    tok = m.tokenizer
    unk = tok.unk_token_id
    ids = [tok(s)["input_ids"] for s in mon]
    n = sum(len(x) for x in ids)
    safe = mid.replace("/", "__")
    np.savez_compressed(f"explore/tatoeba/{TAG}__{safe}.npz", mon=enc(mon), eng=enc(eng))
    json.dump({"tag": TAG, "id": mid, "source": source, "n_pairs": len(mon), "tok_class": type(tok).__name__,
               "unk_rate_mon": sum(t == unk for x in ids for t in x) / n}, open(f"explore/tatoeba/{TAG}__{safe}.json", "w"), indent=1)
    print(TAG, mid, "done", len(mon), "pairs from", source, flush=True)
