# Baserate take-home: question answering over earnings calls and analyst notes

```python
from src.answer import answer
answer("What were JPMorgan's adjusted EPS and ROTCE in 2Q26?")
# {"answer": "... EPS of $6.14 and an ROTCE of 23% [1] ...",
#  "citations": [{"document": "JPM Earnings Call Transcript Q2.pdf",
#                 "passage": "Including (sic) [Excluding] the significant items noted on the page, the Firm delivered net income of $16.9 billion, EPS of $6.14 and an ROTCE of 23%."}]}
```

## 1. Running it from a clean checkout

Requirements: Python 3.10 to 3.13 (tested on 3.12) and internet access on first run, to download a 130 MB embedding model. **Node.js and a separate Claude Code install are not needed**, because `claude-agent-sdk` ships its own Claude Code CLI binary.

```bash
git clone <repo> && cd baserate-takehome
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env            # then put your token in .env:
claude setup-token              # (on any machine with Claude Code) -> paste into CLAUDE_CODE_OAUTH_TOKEN

python -m src.ingest            # optional: builds data/processed/ (~1-2 min). answer() also builds it on first call.
python -m src.answer "How did Netflix's India business perform in 3Q26?"
```

Configuration lives in environment variables, or in `.env`, which is git-ignored:

| variable | default | purpose |
|---|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | *(placeholder)* | your credential from `claude setup-token`. It is passed through to the bundled CLI. |
| `MODEL` | `claude-sonnet-5-5` | any Claude model id |
| `TOP_K` | `8` | passages returned per search call |
| `MAX_TURNS` | `12` | maximum number of agent turns per question |

`answer(question) -> {"answer": str, "citations": [{"document": str, "passage": str}]}` is in `src/answer.py`. It is synchronous, and it also works when called from inside a running event loop, such as Jupyter. `document` is the source PDF's filename. `passage` is always text copied from that document (see §5). `[n]` markers in the answer refer to the citations list. Run the evaluation with `python -m eval.run_eval --label myrun`.

## 2. Requirements and assumptions

What I took the brief to require:
1. **Grounded answers only.** No outside knowledge, even where the model "knows" the company.
2. **Every claim cited** to a specific document and passage. The passage has to really exist in that document, because a made-up quote is worse than no quote.
3. **Explicit abstention** when the corpus can't answer, and partial answers that say what is missing.
4. **Notes are not ground truth.** The brief warns that notes "may not always be accurate". When I checked every quantitative claim in the 12 notes against the transcripts, **about a dozen were wrong**. The errors include wrong numbers (card NCO guidance 3.6% against an actual 3.2%; Copilot seats 50M against 30M; buyback authorization $7B against $27B), wrong direction (a reserve "release" that was a build; bookings "grew 12%" when they fell 12%; expense guide "raised" on 1Q when it was held), and mischaracterizations ("45-day window for all films" when it applies to a handful; "$160B private credit" when that figure is total NBFI exposure). I treat transcripts as authoritative, treat notes as claims, and surface any disagreement between them. For Baserate's users, finding that their own notes are wrong is probably the most valuable output.
5. **The fixed signature** and a clean-checkout run with the evaluator's own credentials.

Assumptions:
- The questions concern this corpus: 3 companies, 2 calls each, 12 notes. The system says so when asked about anything else, such as Apple.
- **Microsoft's fiscal calendar:** FY26 Q4 is Apr–Jun 2026 and FY27 Q1 is Jul–Sep 2026. The "FY27 Q2 guide" was given on the FY27 Q1 call. These mappings are in the manifest, the `list_documents` tool and the prompt, so "calendar Q3 2026 revenue" resolves correctly.
- "Adjusted" for JPM means excluding significant items, which is how management uses the term.
- For an ambiguous question ("what EPS did the company report?"), the system answers for each company and says so, rather than asking a follow-up question. The function is single-turn.
- Latency of about 5–15 seconds per question is acceptable for an analyst tool. Cost per question is about $0.06 with Sonnet.

## 3. System design

```
PDFs ──pypdf──▶ cleaning ──▶ speaker turns ──▶ chunks (586) ──▶ BM25 + bge-small embeddings
                                                                      │
question ──▶ Claude (Agent SDK) ⇄ tools: list_documents · search · get_context
                    │
                    ▼  structured JSON: answer + [{chunk_id, verbatim quote}]
            citation verifier (exact → fuzzy → re-attribute → drop) ──▶ {"answer", "citations"}
```

### Ingestion and cleaning (`src/ingest.py`)
The three transcript sources use three different layouts:
- **JPM:** speaker name and title on separate lines between dotted rules. The name and title **repeat after every page break, in the middle of a sentence**.
- **Microsoft:** `AMY HOOD:` inline, with no page furniture.
- **Netflix (S&P):** name and title lines, with copyright, URL and page-number lines on every page.

The parser drops page furniture, removes JPM's repeated headers so that split sentences join back up, rejoins hyphenated words broken across lines, and splits the text into speaker turns. Each turn is tagged with its **section** (prepared remarks or Q&A) and a **role** (management, analyst, IR host or operator). Speakers are detected structurally (a short title-case line followed by a line containing a job title), not from hard-coded names, so other S&P- or JPM-style transcripts should parse too. The metadata (company, period, calendar quarter, document type, author, date) is in a hand-written `data/manifest.json`. With 18 files, writing it by hand is quicker and more reliable than parsing filenames, such as "MSFT … Q1", which is really FY27.

I used `pypdf` instead of `pdftotext` or `pymupdf` because it is pure Python and needs no system packages, which matters for a clean checkout.

### Chunking (`src/chunking.py`)
- **One chunk per speaker turn**, because a turn is the natural unit of meaning in a call: a question, or a full answer to it. Turns longer than about 220 words are split **on sentence boundaries** with a one-sentence overlap. Amy Hood's prepared remarks, at roughly 2,600 words, are a single paragraph in the PDF, so splitting on paragraphs wouldn't work.
- **Notes are split by paragraph.** Notes are about 300 words and each paragraph covers one topic (results, guidance, capital, "my take").
- Every chunk keeps its provenance (document, company, period, speaker, role, section and turn number), and the chunk ID is readable, for example `JPM_2Q26_tx_004` or `MSFT_FY27Q1_note_SB_002`. That gives the model useful context and makes traces easy to debug.
- For indexing, a **provenance header** such as "JPMorgan 2Q26 transcript Jeremy Barnum:" is prepended to each chunk, so period and company words in a query match even when the passage itself doesn't name them.

### Embeddings and indexing (`src/index.py`)
- **BM25** (`rank-bm25`) handles exact metric names, tickers and numbers ("NII ex-Markets", "3.2%", "E7"), which dense models handle poorly.
- **Dense vectors** come from `BAAI/bge-small-en-v1.5` via `fastembed`. It runs on ONNX with no PyTorch, so the install is small and runs on a CPU, and it handles paraphrases ("India business" → "view hours in India grew 24%"). Vectors are stored in a NumPy file and searched by brute-force cosine similarity. A vector database isn't justified for 586 chunks.
- The two rankings are combined with **reciprocal rank fusion** (k = 60), which needs no score calibration.
- **Role weighting:** after fusion, analyst questions are weighted 0.7, IR hosts 0.8 and operators 0.3, so management's answer outranks the question that contains the same words. This also handles the "China tariffs" trap, where the only "China" mentions are an analyst's firm (China Securities) and "ex China" market sizing.
- Search can be filtered by company, period and document type. If `fastembed` can't load (for example, offline), search falls back to BM25 only instead of failing.

### Tools (`src/tools.py`) and agent (`src/answer.py`, `src/prompts.py`)
Three tools run on an in-process MCP server through the Claude Agent SDK:
| tool | why it exists |
|---|---|
| `list_documents()` | lists the companies, periods and fiscal-to-calendar mapping, so the model can resolve "FY27 Q2" or "last quarter" and knows what *isn't* covered |
| `search(query, company?, period?, doc_type?, k?)` | hybrid search. The filters allow "search the 1Q26 call, then the 2Q26 call" and "check the notes against the transcript" |
| `get_context(chunk_id, window)` | returns neighbouring chunks: the analyst question before an answer, or the rest of a long answer |

Tool output is compact text with chunk IDs, not JSON, to keep token use down. Built-in Claude Code tools (Bash, Read, web) are disabled with `tools=[]`, and local settings and CLAUDE.md files are ignored with `setting_sources=[]`, so the agent can only see the corpus. The final answer uses the SDK's **structured output** (`output_format`, a JSON schema) with the fields `answer`, `insufficient` and `citations: [{chunk_id, quote}]`.

The system prompt sets these research rules:
- search several times, and search each period separately when comparing calls;
- when management says "now expects", find the prior figure;
- for "why" or "depends on" questions, also search the Q&A;
- **always cross-check the analyst notes and flag any disagreement, naming the analyst**;
- note-only claims are attributed to their author and marked as unconfirmed;
- check the question's premise;
- handle Microsoft's fiscal calendar;
- answer partially, or abstain explicitly, when the evidence is missing.

### Citation verification (`src/verify.py`)
The model returns a chunk ID and a quote it says is verbatim. It doesn't get to decide what counts as a citation. Each quote goes through these checks in order:
1. **exact:** the normalized quote (curly quotes, dashes, case) is a substring of the cited chunk;
2. **fuzzy:** a `rapidfuzz` partial-ratio alignment of at least 90, in which case the **exact source span replaces the model's wording**;
3. **repaired:** the quote is real but the chunk ID was wrong, so the citation is re-attributed to the chunk that actually contains it;
4. **dropped:** the quote is found nowhere and is logged as a hallucinated citation.

`[n]` markers are renumbered to match the surviving citations. If the model gave an answer but **no** citation survived, the answer is replaced by the standard "documents do not contain enough information" response. As a result, every passage returned is guaranteed to be real text from the named document.

## 4. Alternatives considered

| option | decision and reason |
|---|---|
| **Long context: put all ~85k tokens in every prompt** | Simpler, and it would probably score well on this corpus. I rejected it because every question would cost about 85k input tokens (more than 10x the cost of the agent), quotes are harder to tie to a document and passage, and it doesn't scale to Baserate's real setting, where users have thousands of notes. With more time I'd run it as a baseline (see §7). |
| **Single-shot RAG** (retrieve top-k once, answer) | Cheaper, but it fails on comparison questions ("1Q vs 2Q"), on cross-checking notes against transcripts, and on follow-ups ("what was the prior guide?"). An agent loop with filtered search handles these naturally and averages only 3–5 tool calls. |
| Fixed-size token chunks | These split a question from its answer and mix speakers. Speaker-turn chunks keep who said it, which matters a great deal when an analyst's question contains the very claim being asked about. |
| Embeddings only, or BM25 only | Each fails in a different way: numbers and acronyms for embeddings, paraphrases for BM25. Hybrid search with RRF is cheap and robust. |
| Bigger embedding model, a reranker, or a vector DB | Unnecessary at 586 chunks. The agent can reformulate queries, which works as a reranker. These are the first things I'd add at scale. |
| Asking the model for JSON in plain text | Structured output (a JSON schema) removes parsing failures. A plain-text JSON fallback is still there. |
| Trusting the model's citations | No. Programmatic verification is cheap and turns "hopefully grounded" into "provably quoted". |
| `pdftotext`, OCR | System dependencies. The PDFs have a text layer, so `pypdf` is enough. |

## 5. Evaluation

### Test set (`eval/gold_questions.json`)
There are 25 questions: the 8 samples plus 17 of my own, each labelled with a category. I verified every expected answer by hand against the transcript text.
| category | n | examples |
|---|---|---|
| fact / guidance | 4 | EPS and ROTCE; Azure guide and its dependencies; India; GSIB surcharge path |
| multi-period | 2 | NII ex-Markets 1Q → 2Q; Azure actual vs prior guide |
| **note conflict** | 13 | each plants a question where one note is wrong (card NCO 3.6% vs 3.2%, reserve "release", $7B vs $27B authorization, content expense 14% vs 10%, season-2 drop-off, Copilot 50M vs 30M seats, Azure 48% vs 43%, bookings grew vs fell, U.S. churn, private credit, theatrical window, operating margin 45% vs 50%, ads 100% vs 80%) |
| false premise | 1 | "Did JPM raise expense guidance on 1Q26?" (no; one note says it did) |
| abstention | 2 | China tariffs (only distractor mentions); Apple |
| not in docs | 1 | Netflix 2027 guidance (deferred to January) |
| ambiguous | 1 | "What EPS did the company report?" |
| fiscal mapping | 1 | "Microsoft revenue in July–September 2026" |

### Scoring (`eval/run_eval.py`, deterministic, no LLM judge)
- **facts:** share of `must_include` key facts present in the answer (alternatives allowed, e.g. `decrease|declin`).
- **abstain_ok:** abstained if and only if it should have.
- **src_recall:** share of the expected source documents among the cited ones.
- **note_flag:** on conflict questions, does the answer surface the wrong note claim or name its author?
- **raw citation validity:** the share of the model's quotes that matched the cited chunk *before* any repair. This is the model's raw citation-hallucination rate. **repaired** and **dropped** counts are reported separately.
- **ungrounded numbers:** numbers in the answer text that appear in none of the returned passages. This is a cheap check for hallucinated claims (as opposed to hallucinated citations), and it is what I inspect by hand.

### Results
| run | change | facts | abstain | src recall | note flag | raw cite validity | dropped | answers w/ ungrounded nums | avg s | cost |
|---|---|---|---|---|---|---|---|---|---|---|
| run1 | baseline prompt | 0.989 | 1.00 | 1.00 | **0.71** | 1.00 | 0 / 72 | (metric bug) | 6.5 | $1.27 |
| run2 | prompt v2 | **1.00** | 1.00 | 1.00 | **1.00** | 1.00 | 0 / 99 | 7 / 25 | 8.1 | $1.53 |
| run3 | repeat of run2 (nondeterminism) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0 / 99 | 7 / 25 | 7.6 | $1.16 |

Full per-question tables and every answer are in `eval/results/`.

**What run1 showed and what changed.** Run1 answered correctly but **didn't mention the wrong notes** when the transcript alone answered the question (S7, C1, C7, C8). For example, it said expense guidance was held at $105B but never mentioned Joe Smith's note claiming a raise. It also took S2's "what the guide depends on" from the prepared remarks only and missed Amy Hood's Q&A caveat about token pricing. Three prompt rules fixed both problems: always cross-check notes, search the Q&A for drivers and caveats, and look up the prior figure behind "now expects". The fix costs one extra search per question, about 20% more cost.

**Hallucination analysis.** Across all runs, **no quote failed verification** (0 dropped, 0 repaired). Sonnet with chunk-ID citations quotes accurately. I read every "ungrounded number" flag from run2 by hand, and none was fabricated:
- *Derived:* "$1.5B increase" (= 96.5 − 95) and "$2.5B" (= 107.5 − 105).
- *Dates:* "Oct 28".
- *True but loosely cited:* operating income +21% is in the cited chunk but outside the quoted sentence; Netflix's 13–14% full-year guide is real but uncited.

So the remaining weakness is **under-citation**, not invention (see §7).

**Held-out check.** To guard against tuning the prompt to my own test set, I ran 8 new questions after the prompt was fixed (`eval/results/holdout_run.txt`). Examples: succession timing, AI's effect on expenses, M&A, "which analyst is more bullish and is it supported", and subscriber adds (which correctly abstained). All 8 were correct and grounded, with 47 out of 47 quotes verified exactly. The system also found **an error I hadn't planted:** Joe Smith's note says Microsoft "has already started issuing debt", but Amy Hood said they "haven't yet … tap[ped]" the debt markets. It also flagged Sally Barton's claim that AI token costs are "a meaningful line item" as contradicted by Barnum ("a trivial number").

**Limits of this evaluation.** It uses 25 questions that I wrote, scored by string matching. Key-fact matching can pass an answer that contains the right number in the wrong context, which is why I also read the answers. Note-flag matching is a proxy. The test set is small enough that one question equals 4 points.

## 6. Project layout
```
src/config.py      env/.env config (token, model, top_k)      src/tools.py     MCP tools for the agent
src/ingest.py      PDF → clean speaker turns (+ rebuild CLI)   src/prompts.py   system prompt + output schema
src/chunking.py    turn/sentence-aware chunks                  src/verify.py    citation verification
src/index.py       BM25 + embeddings + RRF + role weighting    src/answer.py    answer(question) entry point
data/manifest.json document metadata (hand-written)            eval/            gold set, runner, results
```

## 7. With another week
1. **Claim-level grounding.** Split the answer into atomic claims and check that each one is entailed by its cited passage: numbers deterministically, everything else with a cheap Haiku judge. Repair or remove unsupported sentences. This targets the one weakness the evaluation found, under-cited true claims, and catches the dangerous case of a real quote supporting a wrong claim.
2. **A note-audit mode.** Proactively reconcile every claim in a note against its transcript and produce a "your note says X, management said Y" report. This finding is the most valuable thing the system produces, and it fits Baserate's "accurate feedback on your research" goal directly.
3. **A larger, harder test set**, including adversarial and multi-hop questions, questions spanning all three companies, and some written by someone other than me, plus an LLM judge calibrated against my hand labels, a long-context baseline for comparison, and runs on Haiku to compare cost and quality.
4. **Structured extraction** of guidance and KPI tables (metric, period, value, speaker) into a small table the agent can query. This makes comparison questions ("how did guidance change") exact and cheaper.
5. **Scaling the retrieval layer** for real users with thousands of documents: a persistent vector store, incremental ingestion, a cross-encoder reranker, document-level access control, and including the S&P cover table (where Netflix's reported EPS lives, currently skipped as page furniture).
6. **Latency and cost:** cache retrieval per question, stream partial answers, and add a "fast path" for simple lookups.
