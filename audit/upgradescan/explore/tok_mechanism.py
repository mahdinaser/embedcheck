"""EXPLORATORY (Cloud Claude msg #55): what tokenizer files does gmunkhtur ship, and what does each env build?
Usage: python tok_mechanism.py <TAG>  -> explore/tokmech_<TAG>.json"""
import json, sys
import transformers
from huggingface_hub import HfApi, hf_hub_download
from transformers import AutoTokenizer

TAG = sys.argv[1]
MID = "gmunkhtur/paraphrase-multilingual-minilm-l12-v3-mn"
SHA = next(m["sha"] for m in json.load(open("scan_models.json")) if m["id"] == MID)
files = [s.rfilename for s in (HfApi().model_info(MID, revision=SHA).siblings or [])]
tok_files = [f for f in files if any(k in f for k in ("tokenizer", "vocab", "sentencepiece", "spiece", ".model", "special_tokens", "merges"))]
cfg = json.load(open(hf_hub_download(MID, "tokenizer_config.json", revision=SHA))) if "tokenizer_config.json" in files else None
tok = AutoTokenizer.from_pretrained(MID, revision=SHA)
bt = getattr(tok, "backend_tokenizer", None) or getattr(tok, "_tokenizer", None)
bj = json.loads(bt.to_str()) if bt is not None else {}
out = {"tag": TAG, "tf": transformers.__version__, "files": tok_files,
       "tokenizer_config": {k: cfg.get(k) for k in ("tokenizer_class", "do_lower_case", "model_max_length", "tokenize_chinese_chars", "strip_accents")} if cfg else None,
       "class": type(tok).__name__, "is_fast": tok.is_fast,
       "backend_model": (bj.get("model") or {}).get("type"),
       "normalizer": (bj.get("normalizer") or {}).get("type"),
       "pre_tokenizer": (bj.get("pre_tokenizer") or {}).get("type"),
       "example": tok.tokenize("Climate change increases the frequency of heatwaves.")}
json.dump(out, open(f"explore/tokmech_{TAG}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
