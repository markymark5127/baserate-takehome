"""Speaker-turn-aware chunking.

- Transcripts: one chunk per speaker turn; long turns are split on sentence boundaries into
  ~MAX_WORDS windows with a one-sentence overlap so a number and its explanation stay together.
- Analyst notes: one chunk per paragraph (notes are ~300 words; paragraphs are topical).
Each chunk keeps provenance (document, company, period, speaker, role, section).
"""
import json
import re

from .config import PROCESSED_DIR

MAX_WORDS = 220
OVERLAP_SENTENCES = 1
TICKER = {"JPMorgan": "JPM", "Microsoft": "MSFT", "Netflix": "NFLX"}
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z$\"“(])")


def split_long(text):
    sents = SENT_SPLIT.split(text)
    out, cur = [], []
    for s in sents:
        if cur and sum(len(x.split()) for x in cur) + len(s.split()) > MAX_WORDS:
            out.append(" ".join(cur))
            cur = cur[-OVERLAP_SENTENCES:] if OVERLAP_SENTENCES else []
        cur.append(s)
    if cur:
        out.append(" ".join(cur))
    return out


def build_chunks(turns):
    chunks, counters = [], {}
    for t in turns:
        if t["doc_type"] == "analyst_note":
            initials = "".join(w[0] for w in t["speaker"].split())
            prefix = f"{TICKER[t['company']]}_{t['period'].replace(' ', '')}_note_{initials}"
            pieces = t["paragraphs"]
        else:
            prefix = f"{TICKER[t['company']]}_{t['period'].replace(' ', '')}_tx"
            pieces = split_long(" ".join(t["paragraphs"]))
        for p in pieces:
            n = counters.get(prefix, 0)
            counters[prefix] = n + 1
            chunks.append({
                "id": f"{prefix}_{n:03d}",
                "document": t["document"],
                "company": t["company"],
                "period": t["period"],
                "calendar_quarter": t["calendar_quarter"],
                "doc_type": t["doc_type"],
                "date": t["date"],
                "speaker": t["speaker"],
                "title": t["title"],
                "role": t["role"],
                "section": t["section"],
                "turn": t["turn"],
                "text": p,
            })
    with open(PROCESSED_DIR / "chunks.jsonl", "w") as f:
        for c in chunks:
            f.write(json.dumps(c) + "\n")
    return chunks
