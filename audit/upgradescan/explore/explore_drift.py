"""EXPLORATORY (Cloud Claude msg #48): why does gmunkhtur/paraphrase-multilingual-minilm-l12-v3-mn
drift between OLD and NEW? Dumps module list, pooling config, max_seq_length, normalize,
tokenizer outputs and embeddings for the current env.
Usage: python explore_drift.py <TAG>  -> explore/drift_<TAG>.json + .npy"""
import json, sys
import numpy as np, torch, transformers, sentence_transformers
from sentence_transformers import SentenceTransformer

TAG = sys.argv[1]
MID = "gmunkhtur/paraphrase-multilingual-minilm-l12-v3-mn"
SHA = next(m["sha"] for m in json.load(open("scan_models.json")) if m["id"] == MID)
SENTS = ["The cat sat on the mat.", "How do I reset my router password?",
         "Climate change increases the frequency of heatwaves."]
torch.set_num_threads(1)
m = SentenceTransformer(MID, revision=SHA, device="cpu", trust_remote_code=True)
out = {"tag": TAG, "st": sentence_transformers.__version__, "tf": transformers.__version__,
       "modules": str(m), "max_seq_length": m.max_seq_length,
       "module_types": [type(x).__name__ for x in m],
       "dtype": str(next(m.parameters()).dtype)}
for x in m:
    if hasattr(x, "get_config_dict"):
        out.setdefault("configs", {})[type(x).__name__] = x.get_config_dict()
tok = m.tokenizer(SENTS, padding=True, truncation=True)
out["input_ids"] = [list(map(int, r)) for r in tok["input_ids"]]
out["tokenizer_class"] = type(m.tokenizer).__name__
E = m.encode(SENTS, normalize_embeddings=True, convert_to_numpy=True)
np.save(f"explore/drift_{TAG}.npy", E.astype(np.float32))
# raw transformer output norm, to see whether the backbone itself differs
feats = m.tokenize(SENTS)
with torch.no_grad():
    tok_emb = m[0](feats)["token_embeddings"]
out["token_emb_first_vals"] = tok_emb[0, 0, :5].tolist()
json.dump(out, open(f"explore/drift_{TAG}.json", "w"), indent=1, default=str)
print(TAG, "ok", out["module_types"], out["max_seq_length"])
