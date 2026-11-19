"""Citation verification: every quote the model returns must be found in the source text.

- exact:    normalized quote is a substring of the cited chunk
- fuzzy:    rapidfuzz alignment >= FUZZY_MIN against the cited chunk -> replaced with the exact source span
- repaired: quote is real but the chunk_id was wrong -> re-attributed to the chunk that contains it
- dropped:  quote not found anywhere -> removed (counted as a hallucinated citation)
The returned passage is always text copied from the source, never the model's version.
"""
import re

from rapidfuzz import fuzz

from .index import get_index

FUZZY_MIN = 90
_TRANS = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " "})


def norm(s):
    # length-preserving, so indices into norm(text) are valid indices into text
    return s.translate(_TRANS).lower()


def _clean_quote(q):
    return re.sub(r"\s+", " ", q.strip().strip('"').strip("“”").strip())


def _locate(quote, text):
    """Return (kind, exact_span) or None."""
    nq, nt = norm(quote), norm(text)
    pos = nt.find(nq)
    if pos >= 0:
        return "exact", text[pos:pos + len(quote)]
    if len(nq) < 15:
        return None
    al = fuzz.partial_ratio_alignment(nq, nt, score_cutoff=FUZZY_MIN)
    if al is None:
        return None
    s, e = al.dest_start, al.dest_end
    while s > 0 and text[s - 1].isalnum():  # snap to word boundaries
        s -= 1
    while e < len(text) and text[e].isalnum():
        e += 1
    return "fuzzy", text[s:e].strip()


def verify(raw_citations):
    ix = get_index()
    kept, kept_chunks, mapping = [], [], {}
    stats = {"raw": len(raw_citations), "exact": 0, "fuzzy": 0, "repaired": 0, "dropped": 0}
    dropped = []
    for n, c in enumerate(raw_citations, 1):
        quote = _clean_quote(c.get("quote", ""))
        chunk = ix.get(c.get("chunk_id", ""))
        hit = _locate(quote, chunk["text"]) if chunk and quote else None
        if hit is None and quote:
            # wrong chunk id? look for the quote elsewhere (same document first, then the corpus)
            doc = chunk["document"] if chunk else None
            cands = sorted(ix.chunks, key=lambda x: x["document"] != doc)
            for cand in cands:
                h = _locate(quote, cand["text"])
                if h:
                    chunk, hit = cand, ("repaired", h[1])
                    break
        if hit is None:
            stats["dropped"] += 1
            dropped.append(c)
            continue
        stats[hit[0]] += 1
        entry = {"document": chunk["document"], "passage": hit[1]}
        if entry in kept:
            mapping[n] = kept.index(entry) + 1
            continue
        kept.append(entry)
        kept_chunks.append(chunk)
        mapping[n] = len(kept)
    return kept, mapping, stats, dropped, kept_chunks


def renumber(answer, mapping):
    """Rewrite [n] markers to match the verified citation list; remove markers of dropped citations."""
    def sub(m):
        nums = [mapping[int(x)] for x in re.findall(r"\d+", m.group(0)) if int(x) in mapping]
        nums = sorted(set(nums))
        return "[" + ", ".join(map(str, nums)) + "]" if nums else ""
    out = re.sub(r"\[\d+(?:\s*[,\-–]\s*\d+)*\]", sub, answer)
    return re.sub(r"\s+([.,;:])", r"\1", re.sub(r"[ \t]{2,}", " ", out)).strip()
