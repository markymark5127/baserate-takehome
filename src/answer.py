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
from .prompts import INSUFFICIENT, OUTPUT_SCHEMA, SYSTEM_PROMPT
from .tools import ALLOWED, SERVER, SERVER_NAME
from .verify import renumber, verify


def _options():
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
    )


_STDERR: list[str] = []


async def _run_agent(question):
    result = None
    try:
        async for msg in query(prompt=question, options=_options()):
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
    return out, {"cost_usd": result.total_cost_usd, "turns": result.num_turns,
                 "duration_ms": result.duration_ms, "usage": result.usage}


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


def answer_with_trace(question: str) -> tuple[dict, dict]:
    get_index()  # build/load index before the agent starts (first run builds it)
    raw, meta = _run_sync(_run_agent(question))
    citations, mapping, stats, dropped = verify(raw.get("citations") or [])
    text = renumber(raw.get("answer", ""), mapping)
    if raw.get("insufficient"):
        result = {"answer": text or INSUFFICIENT, "citations": citations}
    elif not citations:
        # The model claimed an answer but nothing it cited could be found in the sources.
        result = {"answer": INSUFFICIENT + " (No verifiable supporting passage was found.)", "citations": []}
    else:
        result = {"answer": text, "citations": citations}
    trace = {"raw": raw, "verify": stats, "dropped": dropped, **meta}
    return result, trace


def answer(question: str) -> dict:
    return answer_with_trace(question)[0]


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "What were JPMorgan's adjusted EPS and ROTCE in 2Q26?"
    res, tr = answer_with_trace(q)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    if os.getenv("TRACE"):
        print(json.dumps({k: tr[k] for k in ("verify", "dropped", "turns", "cost_usd", "duration_ms")}, indent=2), file=sys.stderr)
