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
git clone https://github.com/markymark5127/baserate-takehome.git && cd baserate-takehome
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env            # then put your token in .env:
claude setup-token              # (on any machine with Claude Code) -> paste into CLAUDE_CODE_OAUTH_TOKEN

python -m src.ingest            # optional: builds data/processed/ (~1-2 min). answer() also builds it on first call.
python -m src.answer "How did Netflix's India business perform in 3Q26?"

python -m ui.server             # optional: chat UI at http://127.0.0.1:8000 (see below)
```

Configuration lives in environment variables, or in `.env`, which is git-ignored:

| variable | default | purpose |
|---|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | *(placeholder)* | your credential from `claude setup-token`. It is passed through to the bundled CLI. While the placeholder is left as-is, the CLI falls back to any existing `claude` login on the machine. An invalid token fails with a clear `401` message. |
| `MODEL` | `claude-sonnet-5-5` | any Claude model id |
| `TOP_K` | `8` | passages returned per search call |
| `MAX_TURNS` | `12` | maximum number of agent turns per question |
| `GROUNDING` | `on` | claim-level grounding check (§3); `off` skips it, saving about 3 seconds |
| `GROUNDING_MODEL` | `claude-haiku-5-5` | the small model that judges each claim |
| `REPAIR` | `on` | one repair round for unsupported claims before any are removed (§3) |

`answer(question) -> {"answer": str, "citations": [{"document": str, "passage": str}]}` is in `src/answer.py`. It is synchronous, and it also works when called from inside a running event loop, such as Jupyter. `document` is the source PDF's filename. `passage` is always text copied from that document (see §5). `[n]` markers in the answer refer to the citations list. Run the evaluation with `python -m eval.run_eval --label myrun`.


### Optional: chat UI

```bash
source .venv/bin/activate
python -m ui.server             # then open http://127.0.0.1:8000   (PORT=8080 to change the port)
```

This is a local web page for asking questions interactively. It calls the same `answer()` function and adds no dependencies, because the server uses only the Python standard library (`ui/server.py` plus a single page, `ui/index.html`). It isn't needed for evaluation.
- **Answers:** each answer has clickable `[n]` markers that scroll to and highlight the cited source.
- **Sources:** each source card shows the document, a TRANSCRIPT or ANALYST NOTE badge, and the exact verified passage. Click a card to expand it.
- **Footer:** each answer shows "n/n quotes verified", "n/n claims supported", latency and the number of agent steps. When the documents can't answer, the card shows a "Not enough information" badge.
- **Clear:** the ↻ Clear button resets the conversation. Each question is answered independently, as `answer()` is single-turn.
- **Look:** a frosted-glass design that follows the system light or dark mode and works at phone width.

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
- Latency of about 5–15 seconds for most questions (13 s on average in the final run; multi-period and ambiguous questions take up to about 30 s) is acceptable for an analyst tool. Cost per question is about $0.06–0.08 with Sonnet (the repair round adds a little when it runs).

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

The S&P cover page of each Netflix transcript holds a consensus-vs-actual table (EPS normalized, revenue). It is the only place Netflix's reported EPS appears, so it is kept as one passage with the role `data`. Its text is verbatim, and an explanation of the columns goes in the passage's title field rather than its text, so quotes from it still verify.

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

### How conflicting information is handled
The corpus has two kinds of conflict: **a note against a transcript** (a factual error in a note), and **one note against another** (the analysts disagree, or one of them is wrong). The system handles them at three layers:
1. **Prompt policy (`src/prompts.py`).**
   - *Hierarchy:* transcripts are authoritative and notes are claims.
   - *Cross-checking:* on every factual question the agent also searches the notes for the same company and period (`doc_type="analyst_note"`), even when the transcript has already answered it.
   - *Reporting:* when a note disagrees, the answer gives the transcript's figure, names the analyst and states what the note claimed. Example: "card NCO guidance was ~3.2% [1]; Sally Barton's note says ~3.6%, which the transcript contradicts [2]".
   - *Note-only claims:* a claim found only in a note is attributed to that analyst ("according to Joe Smith's note…") and marked as unconfirmed.
   - *Opinions:* "my take: positive" is labelled as opinion, never stated as fact.
   - *Disagreeing notes:* when two notes disagree with each other, the transcript settles it, and the answer says which note matches it, if either.
2. **Retrieval.** Search filters by document type, so the agent can deliberately pull the transcript passage that confirms or refutes a note. Analyst *questions* rank lower, so a claim repeated inside an analyst's question isn't mistaken for management confirming it.
3. **Citations.** Both sides of a conflict are cited, the transcript passage and the note passage, and the sources show which is which (by filename, and with a badge in the UI). The reader can therefore see the disagreement in the original text instead of trusting the model's summary.

Results: in the evaluation, 13 of the 25 questions are planted note conflicts. After the prompt fix, the flag rate went from 0.71 to 1.00 in both final runs (see §5). On held-out questions the system also caught two errors I hadn't planted. Joe Smith wrote that Microsoft "has already started issuing debt", while Amy Hood said it hasn't tapped the debt markets yet. Sally Barton called AI token costs "a meaningful line item", while Barnum called them "a trivial number".

### Citation verification (`src/verify.py`)
The model returns a chunk ID and a quote it says is verbatim. It doesn't get to decide what counts as a citation. Each quote goes through these checks in order:
1. **exact:** the normalized quote (curly quotes, dashes, case) is a substring of the cited chunk;
2. **fuzzy:** a `rapidfuzz` partial-ratio alignment of at least 90, in which case the **exact source span replaces the model's wording**;
3. **repaired:** the quote is real but the chunk ID was wrong, so the citation is re-attributed to the chunk that actually contains it;
4. **dropped:** the quote is found nowhere and is logged as a hallucinated citation.

`[n]` markers are renumbered to match the surviving citations. If the model gave an answer but **no** citation survived, the answer is replaced by the standard "documents do not contain enough information" response. As a result, every passage returned is guaranteed to be real text from the named document.

### Claim-level grounding (`src/grounding.py`)
Verified quotes prove that the *sources* are real, but not that the *answer* says what they say. A real quote can still be attached to an overstated claim. So, after verification:
1. **Split into claims.** The answer is split into sentence-level claims, keeping each claim's `[n]` markers and bullet structure.
2. **One judge call.** A single call to a small model (Haiku, configurable) labels every claim as `supported`, `unsupported` or `no_claim`. The judge sees the **quoted passage exactly as returned to the user** (not the surrounding chunk, so a claim only passes if the evidence the reader can see supports it), a **provenance header** for each one (document, company, fiscal period and calendar quarter, speaker, title, section), and the whole answer for context. Simple arithmetic on cited figures counts as support. Outside knowledge does not.
3. **Repair round.** If any claim is unsupported, the agent's session is resumed once with the list of those sentences and the judge's reasons. The agent can search again and cite the claim, correct it, or drop it. The revised answer then goes through quote verification and grounding again from scratch.
4. **Removal, as a last resort.**
   - Claims still `unsupported` after the repair round are **removed** and logged with the judge's reason.
   - If a removed sentence started with a bold label (for example "**Netflix (3Q26):**"), the label stays and reads "Not confirmed in the cited documents", so the answer still shows the topic was addressed.
   - `supported` claims that had no `[n]` marker **get the supporting citation added**, which fixes the under-citation found in run2 and run3. Supported claims whose markers point only at passages that don't support them are re-pointed to the ones that do.
   - When no factual content survives, the answer becomes the standard "not enough information" response.
5. **Safeguards.** Removal is destructive, so it is guarded:
   - *Matching:* verdicts are matched to claims by the claim's echoed opening words, not just by index.
   - *Justification:* a removal must name the missing or contradicted fact; unexplained verdicts keep the claim.
   - *Failures:* if the judge call fails, the answer is returned unchanged. If the repair round fails, the first grounded answer is kept. Both fail open, because the quotes are already verified.

Grounding costs about 3 seconds and roughly $0.004 per question. The repair round runs only when something is flagged (6 of 25 answers in run6) and adds a few seconds to those answers.

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
| fiscal mapping | 1 | "Microsoft's Azure growth in the July–September 2026 quarter" |

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
| run4 | + claim grounding v1 | 0.99 | 1.00 | 1.00 | 1.00 | 1.00 | 0 / 106 | 4 / 25 | 8.8 | $1.22 |
| run5 | + grounding v2 (provenance headers, justified removals) | 0.99 | 1.00 | 1.00 | 1.00 | 1.00 | 0 / 100 | 9 / 25 | 11.1 | $0.88 |
| run6 | + S&P cover table, label-preserving removal, repair round | **1.00** | 1.00 | 1.00 | 1.00 | 1.00 | 0 / 104 | 7 / 25 | 9.8 | $2.00 |
| run7 | repeat of run6 (nondeterminism) | **1.00** | 1.00 | 1.00 | 1.00 | 1.00 | 0 / 113 | 6 / 25 | 10.1 | $1.46 |
| run8 | judge sees the quoted passage, not the whole chunk (final code) | **1.00** | 1.00 | 1.00 | 1.00 | 1.00 | 0 / 135 | 2 / 25 | 13.0 | $2.09 |

Grounding detail:
- **run4** checked 224 claims and removed 45, adding 75 citations.
- **run5** checked 220 claims and removed 9, adding 94 citations, with 0 judge errors.
- **run6** checked 193 claims and added 71 citations. 6 claims were flagged as unsupported, the repair round fixed all 6, and **0 were removed**.
- **run7** checked 226 claims and added 92 citations. 9 claims in 5 answers were flagged, the repair round fixed all 9, and **0 were removed**.
- **run8** checked 220 claims, added 77 citations and re-pointed 1. 43 claims were flagged across 16 answers, the repair round fixed 36, and **7 were removed**.

Full per-question tables and every answer are in `eval/results/`.

**What run1 showed and what changed.** Run1 answered correctly but **didn't mention the wrong notes** when the transcript alone answered the question (S7, C1, C7, C8). For example, it said expense guidance was held at $105B but never mentioned Joe Smith's note claiming a raise. It also took S2's "what the guide depends on" from the prepared remarks only and missed Amy Hood's Q&A caveat about token pricing. Three prompt rules fixed both problems: always cross-check notes, search the Q&A for drivers and caveats, and look up the prior figure behind "now expects". The fix costs one extra search per question, about 20% more cost.

**Hallucination analysis.** Across all runs, **no quote failed verification** (0 dropped, 0 repaired). Sonnet with chunk-ID citations quotes accurately. I read every "ungrounded number" flag from run2 by hand, and none was fabricated:
- *Derived:* "$1.5B increase" (= 96.5 − 95) and "$2.5B" (= 107.5 − 105).
- *Dates:* "Oct 28".
- *True but loosely cited:* operating income +21% is in the cited chunk but outside the quoted sentence; Netflix's 13–14% full-year guide is real but uncited.

So the remaining weakness was **under-citation**, not invention, which led to claim-level grounding.

**Building the grounding check (run4 → run5).** I read every one of the 45 sentences that run4 removed. Most were **true**:
- The judge saw only passage text, so "CFO Jeremy Barnum said…" failed because the passage doesn't contain his name.
- "FY27 Q1 (Jul–Sep 2026)" failed on the calendar mapping.
- "The transcript is authoritative, so the note is wrong" failed as a policy statement.

Three fixes followed: give the judge each passage's provenance header, explicitly allow the transcript-over-notes rule, and require a stated reason for every removal. In run5, **all 9 removals were real problems**:
- *Overgeneralisations:* "both notes give the $95B → $96.5B change" when Sally Barton's note gives only the new level; "both notes describe the 45% guide" when Joe Smith's doesn't mention it.
- *Figures not in the cited passages:* a note's 3.6% claim when that note passage wasn't cited.
- *Figures from documents never cited:* earlier-quarter EPS figures.

The one cost is C15, the deliberately ambiguous EPS question. Netflix's EPS isn't in its transcript (it sits in the S&P cover table, which I was still skipping at that point), and removing that bullet's unsupported sentence also removed its "Netflix" label. That is why facts scores 0.99. In run5, 94 previously uncited true sentences got citations, so answers are both stricter and better cited.

**Closing the last gap (run6).** Three changes fixed C15 at the root rather than in the scorer:
1. *The data gap:* the S&P cover table is ingested, so Netflix's $0.87 EPS against $0.82 consensus is now transcript data. The C15 answer cites it directly.
2. *Removal damage:* removing a sentence keeps its bold label.
3. *Wrong removals:* the agent gets one repair round before anything is removed.

In run6 and run7, every flagged claim was fixed in the repair round: 15 flagged, 15 fixed, 0 removed. Both runs score 1.00 on every metric. The trade-off is cost, about $0.08 per question on average, up from about $0.05, and the flagged answers take a few seconds longer.

**Judging the visible quote (run8, the submitted code).** Up to run7 the judge saw the whole cited chunk, so a claim could pass on text the reader never sees. In run8 it sees only the quoted passage returned in `citations`, which matches the brief's requirement that the cited passage supports the claim. Scores stayed at 1.00 on every metric, and answers with ungrounded numbers fell from 6–7 to 2. The judge is much stricter: 43 claims were flagged (against 9–15 before), 36 were fixed in the repair round and 7 were removed. I read all 7:
- *Real problems (3):* a phrase in quotation marks ("no changes in release strategies") that is in no cited passage; a FY27 Q2 period label the passage doesn't state; a claim tying the $50B to back leverage when the cited quote doesn't mention it.
- *True but not in the quote (4):* a segment name ("Devices and consumer") and film details (title variants, the Fincher film) that sit in the chunk but outside the quoted sentence.

So the cost of this strictness is that some true context is lost, and a removal can leave a sentence that pointed to the removed one reading awkwardly ("Another specialty release…"), or a bold label marked "Not confirmed in the cited documents". The answers stay correct; they are sometimes less complete. I chose strictness, because for this use case an unsupported sentence is worse than a missing one. Run8 is also slower (13 s average) because more answers take the repair round.

**Held-out check.** To guard against tuning the prompt to my own test set, I ran 8 new questions after the prompt was fixed (`eval/results/holdout_run.txt`). Examples: succession timing, AI's effect on expenses, M&A, "which analyst is more bullish and is it supported", and subscriber adds (which correctly abstained). All 8 were correct and grounded, with 47 out of 47 quotes verified exactly. The system also found **an error I hadn't planted:** Joe Smith's note says Microsoft "has already started issuing debt", but Amy Hood said they "haven't yet … tap[ped]" the debt markets. It also flagged Sally Barton's claim that AI token costs are "a meaningful line item" as contradicted by Barnum ("a trivial number").

**Limits of this evaluation.** It uses 25 questions that I wrote, scored by string matching. Key-fact matching can pass an answer that contains the right number in the wrong context, which is why I also read the answers. Note-flag matching is a proxy. The test set is small enough that one question equals 4 points. Removal works sentence by sentence, so it doesn't yet remove later sentences that depend on a removed one.

## 6. Project layout
```
src/config.py      env/.env config (token, model, top_k)      src/tools.py     MCP tools for the agent
src/ingest.py      PDF → clean speaker turns (+ rebuild CLI)   src/prompts.py   system prompt + output schema
src/chunking.py    turn/sentence-aware chunks                  src/verify.py    citation verification
src/index.py       BM25 + embeddings + RRF + role weighting    src/answer.py    answer(question) entry point
src/grounding.py   claim-level grounding judge + repair
data/manifest.json document metadata (hand-written)            eval/            gold set, runner, results
ui/server.py       optional local chat UI server (stdlib)      ui/index.html    chat page (single file)
```

## 7. With another week
1. **Calibrate the grounding judge.** Hand-label a few hundred claims, measure the judge's false-removal and miss rates, and add a deterministic number check alongside it. The repair round currently hides judge mistakes, which is good for users but makes the judge itself harder to evaluate.
2. **A note-audit mode.** Proactively reconcile every claim in a note against its transcript and produce a "your note says X, management said Y" report. This finding is the most valuable thing the system produces, and it fits Baserate's "accurate feedback on your research" goal directly.
3. **A larger, harder test set**, including adversarial and multi-hop questions, questions spanning all three companies, and some written by someone other than me, plus an LLM judge calibrated against my hand labels, a long-context baseline for comparison, and runs on Haiku to compare cost and quality.
4. **Structured extraction** of guidance and KPI tables (metric, period, value, speaker) into a small table the agent can query. This makes comparison questions ("how did guidance change") exact and cheaper.
5. **Scaling the retrieval layer** for real users with thousands of documents: a persistent vector store, incremental ingestion, a cross-encoder reranker, and document-level access control.
6. **Latency and cost:** cache retrieval per question, stream partial answers, and add a "fast path" for simple lookups.
