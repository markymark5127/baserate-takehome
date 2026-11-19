"""Claim-level grounding: is every sentence of the answer supported by the passages it cites?

Citation verification (verify.py) proves each quote is real. It does not prove that the answer's
sentences say what the quotes say. This step closes that gap:

1. Split the answer into sentence-level claims, keeping each one's [n] markers.
2. One call to a small judge model (GROUNDING_MODEL, default Haiku) labels every claim against the
   FULL text of the cited chunks:
     supported   -> kept; if it had no [n] marker, the supporting citation numbers are added
     unsupported -> removed from the answer (logged in the trace)
     no_claim    -> kept (framing such as "Here is what the documents say:")
3. Arithmetic on cited figures (96.5 - 95 = 1.5) counts as supported; outside knowledge does not.

If the judge call fails, the answer is returned unchanged and the error is recorded (fail open:
the quotes are already verified, so a judge outage should not destroy a good answer).
"""
import json
import re

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

from . import config

MARK = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z*\"“(])")
BULLET = re.compile(r"^(\s*(?:[-•*]|\d+\.)\s+)")

JUDGE_PROMPT = """You check whether each claim in an analyst-facing answer is supported by source passages.
For each claim return a verdict:
- "supported": every fact in the claim is stated in, or follows by simple arithmetic from, the passages.
  Attribution claims such as "Sally Barton's note says X" are supported if that note passage says X.
  Each passage has a header giving its document, company, fiscal period and calendar quarter, speaker,
  speaker title and section; facts in the header (who said it, their role, when) count as stated.
  Statements that something is absent or unconfirmed ("the transcript does not give X", "not confirmed
  in the transcript") count as supported unless a passage directly contradicts them.
  Applying the house rule "transcripts are authoritative over analyst notes" is supported: when a note
  and a transcript passage disagree, saying the note is wrong or the transcript figure is correct is fine.
- "unsupported": any fact (number, direction, speaker, period, characterization) is missing from or
  contradicted by the passages.
- "no_claim": framing, navigation, or a description of the search process ("I searched all six
  transcripts...", "Here is what the documents say:").
Only use "unsupported" when you can name the specific fact that is missing or contradicted, and say
which in "reason". If in doubt between supported and unsupported, the claim is supported.
Read each claim in the context of the full answer (resolve "it", "he", "this" from context).
"support" lists the passage numbers that support the claim (empty unless supported).
"start" repeats the first five words of the claim exactly, so verdicts can be matched to claims.
Judge only against the passages. Do not use outside knowledge."""

SCHEMA = {
    "type": "object",
    "properties": {"verdicts": {"type": "array", "items": {
        "type": "object",
        "properties": {"i": {"type": "integer"}, "start": {"type": "string"},
                       "verdict": {"type": "string", "enum": ["supported", "unsupported", "no_claim"]},
                       "support": {"type": "array", "items": {"type": "integer"}},
                       "reason": {"type": "string"}},
        "required": ["i", "start", "verdict", "support", "reason"]}}},
    "required": ["verdicts"],
}


def split_claims(answer):
    """-> list of lines, each a list of [prefix, units]; plus a flat list of (line, unit, text)."""
    lines, flat = [], []
    for li, line in enumerate(answer.split("\n")):
        m = BULLET.match(line)
        prefix = m.group(1) if m else ""
        body = line[len(prefix):]
        units = [u for u in SENT.split(body) if u.strip()] if body.strip() else []
        lines.append([prefix, units])
        for ui, u in enumerate(units):
            flat.append((li, ui, u))
    return lines, flat


async def _judge(answer, claims, passages):
    blocks = "\n\n".join(f"[{n}] {header}\n{text}" for n, (header, text) in enumerate(passages, 1))
    items = "\n".join(f"{i}. {c}" for i, c in enumerate(claims, 1))
    prompt = (f"PASSAGES\n{blocks}\n\nFULL ANSWER (context)\n{answer}\n\nCLAIMS\n{items}\n\n"
              "Return one verdict per claim number (1-based).")
    opts = ClaudeAgentOptions(model=config.GROUNDING_MODEL, system_prompt=JUDGE_PROMPT, tools=[],
                              allowed_tools=[], setting_sources=[], max_turns=3,
                              output_format={"type": "json_schema", "schema": SCHEMA},
                              cwd=str(config.ROOT))
    result = None
    async for msg in query(prompt=prompt, options=opts):
        if isinstance(msg, ResultMessage):
            result = msg
    out = result.structured_output if result else None
    if out is None and result and result.result:
        t = result.result
        out = json.loads(t[t.find("{"): t.rfind("}") + 1])
    if out is None:
        raise RuntimeError("judge returned no verdicts")
    return out["verdicts"], (result.total_cost_usd or 0)


def passage_header(c):
    """Provenance shown to the judge, so speaker/role/period attributions can be checked."""
    who = f"speaker: {c['speaker']}" + (f", {c['title']}" if c.get("title") else "")
    return (f"{c['document']} | {c['company']} {c['period']} (calendar {c['calendar_quarter']}, "
            f"call/note date {c['date']}) | {c['doc_type']} | {who} | section: {c['section']}")


def _key(s):
    return re.sub(r"[^a-z0-9]+", " ", MARK.sub("", s).lower()).split()[:4]


def _align(verdicts, claims):
    """Map each verdict to a claim index by its echoed opening words, not by trusting its number.
    A verdict that can't be matched is ignored, so that claim is kept (fail open)."""
    keys = [_key(c) for c in claims]
    out = {}
    for v in verdicts:
        k = _key(v.get("start", ""))
        guess = v.get("i", 0) - 1
        if 0 <= guess < len(claims) and k and keys[guess][:len(k)] == k:
            out[guess] = v
            continue
        for j, kj in enumerate(keys):
            if k and j not in out and kj[:len(k)] == k:
                out[j] = v
                break
    return out


async def ground(answer, passages):
    """passages: list of (header, full chunk text), aligned with the citation numbers 1..n."""
    lines, flat = split_claims(answer)
    stats = {"claims": len(flat), "supported": 0, "unsupported": 0, "no_claim": 0, "unmatched": 0,
             "citations_added": 0}
    if not flat or not passages:
        return answer, stats, []
    claims = [u for _, _, u in flat]
    verdicts, cost = await _judge(answer, claims, passages)
    stats["judge_cost_usd"] = cost
    by_i = _align(verdicts, claims)
    removed = []
    for i, (li, ui, text) in enumerate(flat):
        v = by_i.get(i, {"verdict": "unmatched", "support": []})  # no verdict -> keep (fail open)
        kind = v["verdict"]
        stats[kind] = stats.get(kind, 0) + 1
        if kind == "unsupported" and not v.get("reason", "").strip():
            kind = "supported"  # a removal must be justified; unexplained verdicts keep the claim
            stats["unsupported"] -= 1
            stats["supported"] += 1
        if kind == "unsupported":
            removed.append({"claim": text, "reason": v.get("reason", "")})
            lines[li][1][ui] = None
        elif kind == "supported" and not MARK.search(text):
            nums = sorted({n for n in v.get("support", []) if 1 <= n <= len(passages)})
            if nums:
                stats["citations_added"] += 1
                stripped = text.rstrip()
                end = stripped[-1] if stripped[-1:] in ".!?" else ""
                body = stripped[:-1] if end else stripped
                lines[li][1][ui] = f"{body} [{', '.join(map(str, nums))}]{end}"
    out = []
    for prefix, units in lines:
        kept = [u for u in units if u is not None]
        if units and not kept:
            continue  # every sentence on this line was removed
        out.append(prefix + " ".join(kept) if kept else "")
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()
    return text, stats, removed
