"""Single entry point:  answer(question) -> {"answer": str, "citations": [{"document": str, "passage": str}]}

Pipeline: Claude (via the Claude Agent SDK, authenticated with CLAUDE_CODE_OAUTH_TOKEN) runs a short
tool-use loop over our retrieval tools, returns structured JSON with chunk_ids + verbatim quotes,
then every quote is verified against the source text before anything is returned.
"""
import asyncio
import json
import os
import sys
import threading

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

from . import config
from .index import get_index
from .prompts import INSUFFICIENT, OUTPUT_SCHEMA, REPAIR_PROMPT, SYSTEM_PROMPT
from .tools import ALLOWED, SERVER, SERVER_NAME
from .grounding import ground, passage_header
from .verify import renumber, verify


def _options(resume=None):
    env = {}
    if config.OAUTH_TOKEN:
        env["CLAUDE_CODE_OAUTH_TOKEN"] = config.OAUTH_TOKEN
    return ClaudeAgentOptions(
        model=config.MODEL,
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={SERVER_NAME: SERVER},
        tools=[],                      # no built-in tools (no Bash/Read/Web): corpus tools only
        allowed_tools=ALLOWED,
        setting_sources=[],            # ignore any local CLAUDE.md / user settings
        max_turns=config.MAX_TURNS,
        output_format={"type": "json_schema", "schema": OUTPUT_SCHEMA},
        env=env,
        cwd=str(config.ROOT),
        stderr=_STDERR.append,         # keep CLI errors so auth/config problems are reported clearly
        resume=resume,                 # repair round continues the same session (keeps its searches)
    )


_STDERR: list[str] = []


async def _run_agent(question, resume=None):
    result = None
    try:
        async for msg in query(prompt=question, options=_options(resume)):
            if isinstance(msg, ResultMessage):
                result = msg
    except Exception as e:
        tail = "".join(_STDERR[-20:]).strip()
        hint = "" if config.OAUTH_TOKEN else " (no CLAUDE_CODE_OAUTH_TOKEN set: put one in .env, see README)"
        raise RuntimeError(f"Claude Agent SDK call failed{hint}: {e}\n{tail}") from e
    if result is None:
        raise RuntimeError("agent returned no result")
    out = result.structured_output
    if out is None and result.result:  # fall back to parsing text output
        txt = result.result.strip()
        out = json.loads(txt[txt.find("{"): txt.rfind("}") + 1])
    if out is None:
        raise RuntimeError(f"agent failed: {result.subtype} {result.errors}")
    return out, {"cost_usd": result.total_cost_usd or 0, "turns": result.num_turns,
                 "duration_ms": result.duration_ms, "session_id": result.session_id}


def _run_sync(coro):
    """asyncio.run, but also safe when called from inside a running loop (e.g. Jupyter)."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    box = {}
    t = threading.Thread(target=lambda: box.update(v=asyncio.run(coro)))
    t.start()
    t.join()
    return box["v"]


def _check(raw):
    """Verify quotes, renumber markers, then claim-level grounding (which removes unsupported sentences)."""
    citations, mapping, stats, dropped, chunks = verify(raw.get("citations") or [])
    text = renumber(raw.get("answer", ""), mapping)
    grounding, removed = {"skipped": True}, []
    if config.GROUNDING and citations:
        try:
            # Judge against the quoted passage the reader actually sees, not the whole chunk:
            # a claim is only grounded if its citation's visible text supports it.
            passages = [(passage_header(ch), cit["passage"]) for cit, ch in zip(citations, chunks)]
            text, grounding, removed = _run_sync(ground(text, passages))
        except Exception as e:  # fail open: quotes are already verified
            grounding = {"error": f"{type(e).__name__}: {e}"}
    return citations, text, stats, dropped, grounding, removed


def answer_with_trace(question: str) -> tuple[dict, dict]:
    get_index()  # build/load index before the agent starts (first run builds it)
    raw, meta = _run_sync(_run_agent(question))
    citations, text, stats, dropped, grounding, removed = _check(raw)
    repair = {"attempted": False}
    if removed and config.REPAIR and meta.get("session_id"):
        # One repair round: show the agent its unsupported sentences, let it search/fix/drop them,
        # then run the full verification + grounding again. Whatever still fails is removed.
        repair = {"attempted": True, "claims": [r["claim"] for r in removed]}
        try:
            claims = "\n".join(f"- {r['claim']}  (reason: {r['reason']})" for r in removed)
            raw2, meta2 = _run_sync(_run_agent(REPAIR_PROMPT.format(claims=claims), resume=meta["session_id"]))
            c2, t2, s2, d2, g2, r2 = _check(raw2)
            if c2 or raw2.get("insufficient"):
                repair.update(first_grounding=grounding, still_unsupported=len(r2))
                raw, citations, text, stats, dropped, grounding, removed = raw2, c2, t2, s2, d2, g2, r2
            meta["cost_usd"] += meta2["cost_usd"]
            meta["duration_ms"] += meta2["duration_ms"]
            meta["turns"] += meta2["turns"]
        except Exception as e:  # keep the first (already grounded) answer
            repair["error"] = f"{type(e).__name__}: {e}"
    if raw.get("insufficient"):
        result = {"answer": text or INSUFFICIENT, "citations": citations}
    elif not citations or not text.strip():
        # The model claimed an answer but nothing it cited could be found in the sources.
        result = {"answer": INSUFFICIENT + " (No verifiable supporting passage was found.)", "citations": []}
    else:
        result = {"answer": text, "citations": citations}
    trace = {"raw": raw, "verify": stats, "dropped": dropped, "grounding": grounding,
             "removed_claims": removed, "repair": repair, **meta}
    return result, trace


def answer(question: str) -> dict:
    return answer_with_trace(question)[0]


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "What were JPMorgan's adjusted EPS and ROTCE in 2Q26?"
    res, tr = answer_with_trace(q)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    if os.getenv("TRACE"):
        print(json.dumps({k: tr[k] for k in ("verify", "dropped", "grounding", "removed_claims", "repair", "turns", "cost_usd", "duration_ms")}, indent=2), file=sys.stderr)
