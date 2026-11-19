"""Hybrid retrieval: BM25 (exact terms, numbers, tickers) + dense embeddings (paraphrase),
fused with reciprocal rank fusion, then down-weighted by speaker role so management answers
outrank analyst questions and operator boilerplate."""
import json
import re
import sys
from functools import lru_cache

import numpy as np
from rank_bm25 import BM25Okapi

from .config import EMBED_MODEL, PROCESSED_DIR

RRF_K = 60
ROLE_WEIGHT = {"data": 1.0, "management": 1.0, "analyst_note": 1.0, "ir": 0.8, "analyst": 0.7, "operator": 0.3}
STOP = set("the a an and or of to in on for with at by from is are was were be been it its this that as "
           "what did does do how which who why when about their they we our you your".split())


def tokenize(text):
    toks = re.findall(r"[a-z0-9$%][a-z0-9$%.]*", text.lower())
    return [t.rstrip(".-") for t in toks if t.rstrip(".-") and t not in STOP]


def doc_text(c):
    """Text used for indexing: a provenance header + the passage (helps 'Microsoft FY27 Q1 ...' queries)."""
    return f"{c['company']} {c['period']} {c['doc_type'].replace('_', ' ')} {c['speaker']}: {c['text']}"


def _embedder():
    try:
        from fastembed import TextEmbedding
        return TextEmbedding(EMBED_MODEL)
    except Exception as e:  # offline / install problem -> BM25-only, still works
        print(f"[index] embeddings unavailable ({e!r}); falling back to BM25 only", file=sys.stderr)
        return None


def build_index(chunks):
    emb = _embedder()
    if emb is not None:
        vecs = np.array(list(emb.passage_embed([doc_text(c) for c in chunks])), dtype=np.float32)
        vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
        np.save(PROCESSED_DIR / "embeddings.npy", vecs)


class Index:
    def __init__(self):
        path = PROCESSED_DIR / "chunks.jsonl"
        if not path.exists():
            from .ingest import main as rebuild
            rebuild()
        self.chunks = [json.loads(line) for line in open(path)]
        self.by_id = {c["id"]: i for i, c in enumerate(self.chunks)}
        self.bm25 = BM25Okapi([tokenize(doc_text(c)) for c in self.chunks])
        vec_path = PROCESSED_DIR / "embeddings.npy"
        self.vecs = np.load(vec_path) if vec_path.exists() else None
        self.emb = _embedder() if self.vecs is not None else None

    def _mask(self, company=None, period=None, doc_type=None):
        def ok(c):
            return ((not company or company.lower() in c["company"].lower())
                    and (not period or period.replace(" ", "").lower() == c["period"].replace(" ", "").lower())
                    and (not doc_type or doc_type == c["doc_type"]))
        return np.array([ok(c) for c in self.chunks])

    def search(self, query, company=None, period=None, doc_type=None, k=8):
        mask = self._mask(company, period, doc_type)
        if not mask.any():
            return []
        rankings = []
        bm = np.where(mask, self.bm25.get_scores(tokenize(query)), -np.inf)
        rankings.append(np.argsort(-bm))
        if self.emb is not None:
            q = np.array(list(self.emb.query_embed([query]))[0], dtype=np.float32)
            dense = np.where(mask, self.vecs @ (q / np.linalg.norm(q)), -np.inf)
            rankings.append(np.argsort(-dense))
        n_valid = int(mask.sum())
        fused = {}
        for order in rankings:
            for rank, i in enumerate(order[:n_valid]):
                fused[i] = fused.get(i, 0.0) + 1.0 / (RRF_K + rank + 1)
        scored = sorted(((s * ROLE_WEIGHT.get(self.chunks[i]["role"], 1.0), i) for i, s in fused.items()),
                        reverse=True)
        return [self.chunks[i] for _, i in scored[:k]]

    def context(self, chunk_id, window=1):
        """Neighbouring chunks in the same document (e.g. the question before an answer)."""
        i = self.by_id.get(chunk_id)
        if i is None:
            return []
        doc = self.chunks[i]["document"]
        lo, hi = max(0, i - window), min(len(self.chunks), i + window + 1)
        return [c for c in self.chunks[lo:hi] if c["document"] == doc]

    def get(self, chunk_id):
        i = self.by_id.get(chunk_id)
        return None if i is None else self.chunks[i]


@lru_cache(maxsize=1)
def get_index():
    return Index()
