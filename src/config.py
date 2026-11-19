"""Central configuration. Everything model/credential related comes from env (or .env)."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
MANIFEST = ROOT / "data" / "manifest.json"

MODEL = os.getenv("MODEL", "claude-sonnet-5-5")
TOP_K = int(os.getenv("TOP_K", "8"))
MAX_TURNS = int(os.getenv("MAX_TURNS", "12"))
GROUNDING = os.getenv("GROUNDING", "on").lower() not in ("0", "off", "false", "no")
GROUNDING_MODEL = os.getenv("GROUNDING_MODEL", "claude-haiku-5-5")
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
# Token is read by the bundled Claude Code CLI from the environment; we only pass it through.
OAUTH_TOKEN = os.getenv("CLAUDE_CODE_OAUTH_TOKEN") or None
if OAUTH_TOKEN == "your-token-here":
    # untouched placeholder: don't let the CLI try it; fall back to an existing `claude` login if any
    OAUTH_TOKEN = None
    os.environ.pop("CLAUDE_CODE_OAUTH_TOKEN", None)
