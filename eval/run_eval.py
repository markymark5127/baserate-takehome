"""Run the gold question set through answer() and score it.

    python -m eval.run_eval [--label NAME] [--workers 4] [--only S1,C3]

Metrics per question (all deterministic, no LLM judge -> cheap and reproducible):
  facts       share of must_include items present in the answer ("a|b" = any alternative)
  abstain_ok  abstained iff it should have (for should_abstain questions / answerable questions)
  src_recall  share of expected documents among the cited documents
  note_flag   for note-conflict questions: did the answer surface the note's wrong claim / author
  cit_valid   raw citation validity before verification = (exact+fuzzy)/raw quotes from the model
  dropped     citations whose quote was not found anywhere (hallucinated quotes)
  ungrounded  numbers in the answer that appear in none of the returned passages
"""
import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.answer import answer_with_trace  # noqa: E402
from src.prompts import INSUFFICIENT  # noqa: E402

ABSTAIN_PAT = re.compile(r"(do(es)? not (contain|mention|discuss|include|address|cover)|no (mention|discussion|information)"
                         r"|not (discussed|mentioned|covered|addressed)|insufficient|not enough information|"
                         r"none of the (provided )?documents)", re.I)
NUM_PAT = re.compile(r"\d+(?:[.,]\d+)?")


def norm(s):
    return s.lower().replace(",", "").replace("’", "'")


def has(text, alt):
    return any(a.strip() and a.strip() in text for a in norm(alt).split("|"))


def ungrounded_numbers(ans, citations):
    body = norm(" ".join(c["passage"] for c in citations))
    ans = re.sub(r"\[\d+(?:,\s*\d+)*\]", "", ans)  # citation markers
    ans = re.sub(r"(?i)\b(FY\s?\d{2}|[1-4]Q\d{2}|Q[1-4](\s?FY\d{2})?|H[12])\b", "", ans)  # period labels
    nums = {n.replace(",", "") for n in NUM_PAT.findall(ans)}
    # ignore tiny integers (counts, list numbering) and period labels like 2026 / 26 / Q2
    nums = {n for n in nums if not (n.isdigit() and (int(n) < 10 or 2020 <= int(n) <= 2030))}
    return sorted(n for n in nums if n not in body)


def score(item, res, trace):
    ans = norm(res["answer"])
    out = {"id": item["id"], "category": item["category"]}
    must = item["must_include"]
    out["facts"] = round(sum(has(ans, m) for m in must) / len(must), 2) if must else None
    abstained = bool(trace["raw"].get("insufficient")) or res["answer"].startswith(INSUFFICIENT) or (
        not res["citations"] and bool(ABSTAIN_PAT.search(res["answer"])))
    out["abstained"] = abstained
    if item["should_abstain"]:
        out["abstain_ok"] = abstained or bool(ABSTAIN_PAT.search(res["answer"]))
    else:
        out["abstain_ok"] = not abstained
    docs = {c["document"] for c in res["citations"]}
    exp = item["expected_docs"]
    out["src_recall"] = round(sum(d in docs for d in exp) / len(exp), 2) if exp else None
    out["note_flag"] = has(ans, item["note_flag"]) if item.get("note_flag") else None
    v = trace["verify"]
    out["n_cit"] = len(res["citations"])
    out["cit_valid"] = round((v["exact"] + v["fuzzy"]) / v["raw"], 2) if v["raw"] else None
    out["repaired"], out["dropped"] = v["repaired"], v["dropped"]
    out["ungrounded"] = ungrounded_numbers(res["answer"], res["citations"])
    g = trace.get("grounding") or {}
    out["claims"], out["removed"] = g.get("claims", 0), g.get("unsupported", 0)
    out["cit_added"], out["g_error"] = g.get("citations_added", 0), g.get("error")
    rp = trace.get("repair") or {}
    out["repaired_round"] = bool(rp.get("attempted"))
    out["first_unsupported"] = len(rp.get("claims", []))
    out["sec"] = round(trace["duration_ms"] / 1000, 1)
    out["cost"] = round(trace["cost_usd"] or 0, 4)
    return out


def run_one(item):
    t = time.time()
    try:
        res, trace = answer_with_trace(item["question"])
        return item, res, trace, None
    except Exception as e:  # keep going; an error counts as a failure
        return item, None, None, f"{type(e).__name__}: {e} after {time.time() - t:.0f}s"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default=time.strftime("%Y%m%d-%H%M%S"))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    gold = json.loads((ROOT / "eval" / "gold_questions.json").read_text())
    if args.only:
        keep = set(args.only.split(","))
        gold = [g for g in gold if g["id"] in keep]
    outdir = ROOT / "eval" / "results"
    outdir.mkdir(exist_ok=True)
    rows, raw = [], []
    with ThreadPoolExecutor(args.workers) as ex:
        for item, res, trace, err in ex.map(run_one, gold):
            if err:
                rows.append({"id": item["id"], "category": item["category"], "error": err})
                print(f"{item['id']}: ERROR {err}", flush=True)
                continue
            s = score(item, res, trace)
            rows.append(s)
            raw.append({"id": item["id"], "question": item["question"], "expected": item["expected"],
                        "result": res, "verify": trace["verify"], "dropped": trace["dropped"],
                        "grounding": trace.get("grounding"), "removed_claims": trace.get("removed_claims"),
                        "repair": trace.get("repair")})
            print(json.dumps(s), flush=True)
    rows.sort(key=lambda r: r["id"])

    def mean(key):
        vals = [r[key] for r in rows if r.get(key) is not None and not isinstance(r.get(key), list)]
        return round(sum(vals) / len(vals), 3) if vals else None

    ok = [r for r in rows if "error" not in r]
    summary = {
        "label": args.label, "n": len(rows), "errors": len(rows) - len(ok),
        "facts": mean("facts"), "abstain_ok": mean("abstain_ok"), "src_recall": mean("src_recall"),
        "note_flag": mean("note_flag"), "cit_valid_raw": mean("cit_valid"),
        "citations_total": sum(r["n_cit"] for r in ok), "repaired": sum(r["repaired"] for r in ok),
        "dropped": sum(r["dropped"] for r in ok),
        "answers_with_ungrounded_numbers": sum(bool(r["ungrounded"]) for r in ok),
        "claims_checked": sum(r["claims"] for r in ok), "claims_removed": sum(r["removed"] for r in ok),
        "citations_added": sum(r["cit_added"] for r in ok), "grounding_errors": sum(bool(r["g_error"]) for r in ok),
        "repair_rounds": sum(r["repaired_round"] for r in ok),
        "unsupported_before_repair": sum(r["first_unsupported"] for r in ok),
        "avg_sec": mean("sec"), "total_cost_usd": round(sum(r["cost"] for r in ok), 3),
    }
    lines = [f"# Eval run `{args.label}`", "", "```json", json.dumps(summary, indent=1), "```", "",
             "| id | cat | facts | abstain_ok | src_recall | note_flag | cites | raw_valid | repaired | dropped | claims | removed | cit_added | ungrounded | sec |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if "error" in r:
            lines.append(f"| {r['id']} | {r['category']} | ERROR: {r['error'][:80]} |||||||||| |")
            continue
        lines.append("| " + " | ".join(str(r[k]) if r[k] is not None else "-" for k in
                     ("id", "category", "facts", "abstain_ok", "src_recall", "note_flag", "n_cit", "cit_valid",
                      "repaired", "dropped", "claims", "removed", "cit_added"))
                     + f" | {' '.join(r['ungrounded']) or '-'} | {r['sec']} |")
    (outdir / f"{args.label}.md").write_text("\n".join(lines) + "\n")
    with open(outdir / f"{args.label}.answers.jsonl", "w") as f:
        for r in sorted(raw, key=lambda x: x["id"]):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
