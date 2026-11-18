"""Retrieval tools exposed to the agent through an in-process MCP server.

Tool output is compact plain text (not JSON) to keep context/token usage low, and every
passage is labelled with its chunk_id so the model can cite it."""
import json
from collections import defaultdict

from claude_agent_sdk import create_sdk_mcp_server, tool

from .config import MANIFEST, TOP_K
from .index import get_index

SERVER_NAME = "docs"


def fmt(c):
    who = f"{c['speaker']} ({c['role']}, {c['section']})"
    return (f"[{c['id']}] {c['company']} {c['period']} {c['doc_type']} | {who}\n{c['text']}")


def _text(s):
    return {"content": [{"type": "text", "text": s}]}


@tool("list_documents", "List every available document with company, period, type, author and date. "
      "Call this when unsure which companies/periods exist.", {})
async def list_documents(args):
    m = json.loads(MANIFEST.read_text())
    groups = defaultdict(list)
    for d in m:
        groups[(d["company"], d["period"], d["calendar_quarter"])].append(
            d["doc_type"] + (f" by {d['author']}" if d["author"] else "") + f" ({d['date']})")
    lines = [f"{c} {p} [calendar {cq}]: " + "; ".join(v) for (c, p, cq), v in groups.items()]
    lines.append("Only these 3 companies and periods exist. Microsoft's fiscal year ends June 30 "
                 "(FY26 Q4 = Apr-Jun 2026, FY27 Q1 = Jul-Sep 2026, FY27 Q2 = Oct-Dec 2026).")
    return _text("\n".join(lines))


@tool("search", "Hybrid keyword+semantic search over transcript and analyst-note passages. "
      "Optional filters: company (JPMorgan|Microsoft|Netflix), period (e.g. 1Q26, 2Q26, 3Q26, FY26 Q4, FY27 Q1), "
      "doc_type (transcript|analyst_note). Returns passages labelled with chunk_id.",
      {"type": "object",
       "properties": {"query": {"type": "string"},
                      "company": {"type": "string"},
                      "period": {"type": "string"},
                      "doc_type": {"type": "string", "enum": ["transcript", "analyst_note"]},
                      "k": {"type": "integer", "minimum": 1, "maximum": 15}},
       "required": ["query"]})
async def search(args):
    hits = get_index().search(args["query"], company=args.get("company"), period=args.get("period"),
                              doc_type=args.get("doc_type"), k=int(args.get("k") or TOP_K))
    if not hits:
        return _text("No passages matched (check the filters).")
    return _text("\n\n".join(fmt(c) for c in hits))


@tool("get_context", "Return the passages immediately before/after a chunk in the same document "
      "(e.g. the analyst question preceding an answer, or the rest of a long answer).",
      {"type": "object",
       "properties": {"chunk_id": {"type": "string"}, "window": {"type": "integer", "minimum": 1, "maximum": 3}},
       "required": ["chunk_id"]})
async def get_context(args):
    ctx = get_index().context(args["chunk_id"], int(args.get("window") or 1))
    return _text("\n\n".join(fmt(c) for c in ctx) if ctx else "Unknown chunk_id.")


TOOLS = [list_documents, search, get_context]
SERVER = create_sdk_mcp_server(name=SERVER_NAME, tools=TOOLS)
ALLOWED = [f"mcp__{SERVER_NAME}__{t.name}" for t in TOOLS]
