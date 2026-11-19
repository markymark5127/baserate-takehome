"""PDF -> cleaned text -> speaker turns (transcripts) / paragraphs (notes) -> chunks -> index.

Run `python -m src.ingest` to (re)build everything under data/processed/.
"""
import json
import re

from pypdf import PdfReader

from .config import MANIFEST, PROCESSED_DIR, RAW_DIR

DOTS = re.compile(r"^\s*\.{20,}\s*$")
PAGE_NUM = re.compile(r"^\s*\d{1,3}\s*$")
# Page furniture to drop (S&P/Netflix headers, JPM cover page).
JUNK = [
    re.compile(p, re.I)
    for p in [
        r"^NETFLIX, INC\. FQ\d",
        r"^Copyright ©",
        r"^COPYRIGHT ©",
        r"^spglobal\.com/marketintelligence",
        r"^© 20\d\d S&P Global",
        r"^\s*FEBRUARY 2026\s*$",
    ]
]
TITLE_WORDS = re.compile(
    r"(Officer|President|Director|Analyst|Relations|Chairman|Chief|CEO|CFO|Head of|Executive|Corporate)"
)
INLINE_SPEAKER = re.compile(r"^(Operator|[A-Z][A-Z .'’\-]{2,40}):\s*(.*)$")  # "Operator: ..." / "AMY HOOD: ..."
QA_MARKERS = re.compile(r"^(QUESTION AND ANSWER SECTION|Question and Answer)\s*$")
MD_MARKERS = re.compile(r"^(MANAGEMENT DISCUSSION SECTION|Presentation)\s*$")


def pdf_lines(path):
    text = "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
    return [ln.rstrip() for ln in text.splitlines()]


def is_name_line(line):
    s = line.strip()
    words = s.split()
    return (
        0 < len(words) <= 5
        and len(s) < 45
        and not s.endswith((".", ",", "?", ":", "!"))
        and all(w[0].isupper() for w in words if w[0].isalpha())
        and not TITLE_WORDS.search(s)
    )


def is_title_line(line):
    s = line.strip()
    return 0 < len(s) < 110 and bool(TITLE_WORDS.search(s)) and not s.endswith((".", "?"))


def join_lines(lines):
    """Join wrapped PDF lines into paragraphs; blank lines are paragraph breaks."""
    paras, cur = [], ""
    for ln in lines:
        s = ln.strip()
        if not s:
            if cur:
                paras.append(cur)
                cur = ""
            continue
        if cur.endswith("-") and not cur.endswith(" -"):
            cur = cur + s  # re-join hyphenation split across lines ("year-over-\nyear")
        else:
            cur = f"{cur} {s}" if cur else s
    if cur:
        paras.append(cur)
    return [re.sub(r"\s{2,}", " ", p) for p in paras]


def role_for(speaker, title, company):
    sp, t = speaker.lower(), (title or "").lower()
    if sp == "operator":
        return "operator"
    if "analyst" in t:
        return "analyst"
    if "investor relations" in t or sp in {"jonathan neilson", "spencer wang"}:
        return "ir"  # IR hosts; on Netflix they read analysts' questions aloud
    if company == "Microsoft" and sp not in {"satya nadella", "amy hood"}:
        return "analyst"
    return "management"


def cover_table(lines):
    """S&P transcripts open with a consensus-vs-actual table (EPS normalized, revenue). It is real data
    (e.g. Netflix's reported EPS is only stated here), so keep it as one passage, text verbatim."""
    start = next((i for i, ln in enumerate(lines) if "Market Intelligence Estimates" in ln), None)
    if start is None:
        return []
    end = next((i for i in range(start, len(lines)) if lines[i].strip() in ("Contents", "Table of Contents")),
               min(start + 30, len(lines)))
    return [{"speaker": "S&P Global Market Intelligence", "role": "data", "section": "cover",
             "title": "Consensus estimates vs. actuals table from the transcript cover page. In the "
                      "'EPS NORMALIZED' history rows the columns are: quarter, consensus, actual, surprise %.",
             "lines": lines[start:end]}]


def parse_transcript(path, company):
    raw = pdf_lines(path)
    lines = [ln for ln in raw if not any(j.search(ln) for j in JUNK)]
    turns, cur, section = cover_table(lines), None, "prepared_remarks"
    started = company == "Microsoft"  # MSFT has no cover page / table of contents
    prev_dots = False
    i = 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if MD_MARKERS.match(s):
            started, section = True, "prepared_remarks"
            i += 1
            continue
        if QA_MARKERS.match(s) and started:
            section = "qa"
            i += 1
            continue
        if not started:
            i += 1
            continue
        if DOTS.match(ln):
            prev_dots = True
            if cur is not None:
                cur["lines"].append("")
            i += 1
            continue
        if PAGE_NUM.match(ln):
            # JPM repeats "Name / Title" after a page break mid-turn; drop it so sentences rejoin.
            if i + 2 < len(lines) and is_name_line(lines[i + 1]) and is_title_line(lines[i + 2]) and cur \
                    and cur["speaker"] == lines[i + 1].strip():
                i += 3
            else:
                i += 1
            continue
        new_speaker = None
        if is_name_line(s) and is_title_line(nxt) and (prev_dots or company == "Netflix" or cur is None):
            title = re.sub(r"\s+[QA]$", "", nxt)
            new_speaker, rest, skip = s, "", 2
        else:
            m = INLINE_SPEAKER.match(s)
            if m and (company == "Microsoft" or m.group(1) == "Operator"):
                new_speaker, title, rest, skip = m.group(1).title(), "", m.group(2), 1
        if new_speaker:
            if company == "Microsoft" and new_speaker.lower() == "operator":
                section = "qa"
            cur = {"speaker": new_speaker, "title": title, "section": section, "lines": [rest] if rest else []}
            turns.append(cur)
            i += skip
            prev_dots = False
            continue
        prev_dots = False
        if cur is not None:
            cur["lines"].append(ln)
        i += 1
    out = []
    for t in turns:
        paras = join_lines(t.pop("lines"))
        if not paras:
            continue
        t["role"] = t.get("role") or role_for(t["speaker"], t["title"], company)
        t["paragraphs"] = paras
        out.append(t)
    return out


def parse_note(path):
    lines = pdf_lines(path)
    author = lines[0].strip()
    byline = lines[1].strip()
    body = lines[2:]
    # Notes have no blank lines between paragraphs; a short line ending a sentence ends a paragraph.
    paras, cur = [], []
    for ln in body:
        cur.append(ln)
        if ln.strip().endswith((".", "?", "!")) and len(ln.strip()) < 85:
            paras.append(" ".join(x.strip() for x in cur))
            cur = []
    if cur:
        paras.append(" ".join(x.strip() for x in cur))
    paras = [re.sub(r"\s{2,}", " ", re.sub(r"(\w)- (\w)", r"\1-\2", p)) for p in paras if p.strip()]
    return {"speaker": author, "title": byline, "role": "analyst_note", "section": "note", "paragraphs": paras}


def build_turns():
    manifest = json.loads(MANIFEST.read_text())
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    for doc in manifest:
        path = RAW_DIR / doc["file"]
        if doc["doc_type"] == "transcript":
            turns = parse_transcript(path, doc["company"])
        else:
            turns = [parse_note(path)]
        for n, t in enumerate(turns):
            records.append({"document": doc["file"], "turn": n, **{k: doc[k] for k in
                            ("company", "period", "doc_type", "date", "calendar_quarter")}, **t})
    with open(PROCESSED_DIR / "turns.jsonl", "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    return records


def main():
    from .chunking import build_chunks
    from .index import build_index

    turns = build_turns()
    chunks = build_chunks(turns)
    build_index(chunks)
    print(f"{len(turns)} turns -> {len(chunks)} chunks -> index written to {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
