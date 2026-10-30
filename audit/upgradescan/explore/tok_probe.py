"""EXPLORATORY (Cloud Claude msg #52): record the tokenizer sentence-transformers actually attaches.
Loads the model exactly like probe.py (revision=sha, trust_remote_code=True), no forward pass.
Usage: python tok_probe.py <TAG> <model_id> <sha>  -> explore/tok/<TAG>/<safe_id>.json"""
import json, os, sys, traceback

TAG, MID, SHA = sys.argv[1:4]
safe = MID.replace("/", "__")
os.makedirs(f"explore/tok/{TAG}", exist_ok=True)
SENTS = ["The cat sat on the mat.", "Quantum computing uses qubits to perform calculations.", "How do I reset my router password?",
 "Vaccines train the immune system to recognize pathogens.", "The stock market fell sharply on Monday.", "Photosynthesis converts light into chemical energy.",
 "What is the capital of Australia?", "She plays the violin in a symphony orchestra.", "Climate change increases the frequency of heatwaves.",
 "The recipe calls for two cups of flour.", "Neural networks learn representations from data.", "The train to Boston departs at 9 am.",
 "Insulin regulates blood glucose levels.", "He forgot his umbrella and got soaked.", "The Treaty of Versailles ended World War I.",
 "Python is a popular programming language.", "Bees communicate through a waggle dance.", "The hotel offers free breakfast and parking.",
 "Black holes bend light through gravity.", "Please summarize the attached quarterly report."]
out = {"tag": TAG, "id": MID, "sha": SHA, "ok": False}
try:
    import torch
    from sentence_transformers import SentenceTransformer
    torch.set_num_threads(1)
    m = SentenceTransformer(MID, revision=SHA, device="cpu", trust_remote_code=True)
    tok = m.tokenizer
    ids = [list(map(int, tok(s)["input_ids"])) for s in SENTS]
    unk = getattr(tok, "unk_token_id", None)
    n = sum(len(x) for x in ids)
    out.update(ok=True, tok_class=type(tok).__name__, is_fast=bool(getattr(tok, "is_fast", False)),
               vocab_size=len(tok), unk_id=unk, input_ids=ids,
               unk_frac=(sum(t == unk for x in ids for t in x) / n) if (unk is not None and n) else None)
except BaseException as e:
    out["error"] = f"{type(e).__name__}: {str(e)[:300]}"
    out["tb_tail"] = traceback.format_exc()[-500:]
json.dump(out, open(f"explore/tok/{TAG}/{safe}.json", "w"), indent=1)
print(TAG, MID, out.get("tok_class") if out["ok"] else out["error"][:120], flush=True)
