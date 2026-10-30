"""Run once (any env with `datasets` + `huggingface_hub`). Writes data/ and models.json with pinned SHAs."""
import json, os
from datasets import load_dataset
from huggingface_hub import model_info
os.makedirs("data", exist_ok=True)
c = load_dataset("BeIR/scifact", "corpus", split="corpus")
q = load_dataset("BeIR/scifact", "queries", split="queries")
qr = load_dataset("BeIR/scifact-qrels", split="test")
docs = [{"id": str(r["_id"]), "text": (r["title"] + ". " + r["text"]).strip()} for r in c]
qrels = {}
for r in qr: qrels.setdefault(str(r["query-id"]), {})[str(r["corpus-id"])] = int(r["score"])
queries = [{"id": str(r["_id"]), "text": r["text"]} for r in q if str(r["_id"]) in qrels]
json.dump({"docs": docs, "queries": queries, "qrels": qrels}, open("data/scifact.json", "w"))
print(len(docs), "docs", len(queries), "queries")
M = {  # name: (repo, query_prefix, doc_prefix)
 "MiniLM-L6": ("sentence-transformers/all-MiniLM-L6-v2", "", ""),
 "mpnet-base": ("sentence-transformers/all-mpnet-base-v2", "", ""),
 "multiqa-MiniLM": ("sentence-transformers/multi-qa-MiniLM-L6-cos-v1", "", ""),
 "para-multi-MiniLM": ("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "", ""),
 "bge-small": ("BAAI/bge-small-en-v1.5", "Represent this sentence for searching relevant passages: ", ""),
 "bge-base": ("BAAI/bge-base-en-v1.5", "Represent this sentence for searching relevant passages: ", ""),
 "e5-small-v2": ("intfloat/e5-small-v2", "query: ", "passage: "),
 "e5-base-v2": ("intfloat/e5-base-v2", "query: ", "passage: "),
 "me5-small": ("intfloat/multilingual-e5-small", "query: ", "passage: "),
 "gte-small": ("thenlper/gte-small", "", ""),
 "gte-base": ("thenlper/gte-base", "", ""),
 "nomic-v1.5": ("nomic-ai/nomic-embed-text-v1.5", "search_query: ", "search_document: "),
 "arctic-s": ("Snowflake/snowflake-arctic-embed-s", "Represent this sentence for searching relevant passages: ", ""),
 "mxbai-large": ("mixedbread-ai/mxbai-embed-large-v1", "Represent this sentence for searching relevant passages: ", ""),
 "jina-v2-small": ("jinaai/jina-embeddings-v2-small-en", "", ""),
 "qwen3-0.6b": ("Qwen/Qwen3-Embedding-0.6B", "Instruct: Given a scientific claim, retrieve documents that support or refute the claim\nQuery:", ""),
}
out = {k: {"repo": r, "sha": model_info(r).sha, "qp": qp, "dp": dp} for k, (r, qp, dp) in M.items()}
json.dump(out, open("models.json", "w"), indent=1); print(json.dumps({k: v["sha"][:10] for k, v in out.items()}, indent=0))
