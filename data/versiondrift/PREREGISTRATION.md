# VersionDrift kill test: pre-registration (frozen 2026-10-26, before any run)

**Question.** If you keep the same embedding model, pinned to the same Hugging Face commit, but upgrade the Python libraries, do the embeddings change enough to hurt retrieval for an index that is already built?

**Environments.** Same Python, same torch, same device. Only the libraries change.
- OLD: sentence-transformers 3.4.1 + transformers 4.48.3
- MID: sentence-transformers 4.1.0 + transformers 4.51.3 (needed for Qwen3)
- NEW: the latest sentence-transformers + transformers (ST 6.x / TF 5.x on 2026-10-26), versions recorded at run time

**Models.** 16 models. Each is pinned to the commit SHA resolved once in prep and passed as `revision=`, so hub-side changes are ruled out.
- MiniLM-L6, mpnet-base, multi-qa-MiniLM, paraphrase-multilingual-MiniLM-L12
- bge-small, bge-base, e5-small-v2, e5-base-v2, multilingual-e5-small
- gte-small, gte-base, nomic-embed-text-v1.5, arctic-embed-s, mxbai-embed-large
- jina-v2-small, Qwen3-Embedding-0.6B

**Data.** BEIR SciFact: 5,183 documents, 300 test queries, with the official qrels.
- Each model's documented prefixes are added by hand, identically in every environment.
- `normalize_embeddings=True`, float32.

**Primary contrast.** OLD vs NEW, over models that load in both environments.
- Secondary: MID vs NEW. Qwen3 only appears in MID vs NEW.
- A model that loads in OLD but fails in NEW is counted as a BREAK and reported separately.

**Metrics, per model.**
- Same-text cosine between versions: median, 1st percentile and minimum, over documents and queries.
- nDCG@10 for each of: OLD index with OLD queries, NEW with NEW, and OLD index with NEW queries (cross).
- Top-10 overlap between the OLD and NEW rankings.

**A model counts as DRIFTED if either:**
- median same-text cosine < 0.99, or
- |nDCG@10(cross) − nDCG@10(OLD/OLD)| ≥ 1.0 point.

**Decision.**
- **GO** if at least 20% of the models compared OLD vs NEW are DRIFTED, or at least 2 models BREAK.
- **KILL** otherwise, meaning the libraries are numerically stable and there is no paper.
- **Note only:** if drift appears only at cosine 0.999 levels with zero ranking change, that is a KILL.
