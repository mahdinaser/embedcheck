"""EXPLORATORY copy of probe.py (Cloud Claude msg #55): identical except model_kwargs={"torch_dtype": torch.float32}.
Usage: python probe_fp32.py NEW_fp32 <model_id> <sha>"""
"""Usage: python probe.py <TAG> <model_id> <sha>  -> scan/<TAG>/<safe_id>.json (+ .npy). Exit 0 always."""
import json, sys, os, time, traceback
TAG, MID, SHA = sys.argv[1:4]; safe = MID.replace("/", "__"); os.makedirs(f"scan/{TAG}", exist_ok=True)
out = {"tag": TAG, "id": MID, "sha": SHA, "ok": False}
SENTS = ["The cat sat on the mat.", "Quantum computing uses qubits to perform calculations.", "How do I reset my router password?",
 "Vaccines train the immune system to recognize pathogens.", "The stock market fell sharply on Monday.", "Photosynthesis converts light into chemical energy.",
 "What is the capital of Australia?", "She plays the violin in a symphony orchestra.", "Climate change increases the frequency of heatwaves.",
 "The recipe calls for two cups of flour.", "Neural networks learn representations from data.", "The train to Boston departs at 9 am.",
 "Insulin regulates blood glucose levels.", "He forgot his umbrella and got soaked.", "The Treaty of Versailles ended World War I.",
 "Python is a popular programming language.", "Bees communicate through a waggle dance.", "The hotel offers free breakfast and parking.",
 "Black holes bend light through gravity.", "Please summarize the attached quarterly report."]
try:
    import numpy as np, torch, transformers, sentence_transformers
    from sentence_transformers import SentenceTransformer
    torch.set_num_threads(1)
    out.update(st=sentence_transformers.__version__, tf=transformers.__version__, torch=torch.__version__)
    t0 = time.time(); m = SentenceTransformer(MID, revision=SHA, device="cpu", trust_remote_code=True, model_kwargs={"torch_dtype": torch.float32}); out["load_s"] = round(time.time()-t0, 2)
    out["dtype"] = str(next(m.parameters()).dtype)
    enc = lambda: m.encode(SENTS, batch_size=20, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
    E = enc(); ts = []
    for _ in range(3):
        t = time.time(); enc(); ts.append(time.time()-t)
    out["encode_s"] = float(np.median(ts)); out["dim"] = int(E.shape[1]); out["ok"] = True
    np.save(f"scan/{TAG}/{safe}.npy", np.asarray(E, dtype=np.float32))
except BaseException as e:
    out["error"] = f"{type(e).__name__}: {str(e)[:500]}"; out["tb_tail"] = traceback.format_exc()[-800:]
json.dump(out, open(f"scan/{TAG}/{safe}.json", "w"), indent=1)
print(TAG, MID, "ok" if out["ok"] else out.get("error", "")[:160], flush=True)
