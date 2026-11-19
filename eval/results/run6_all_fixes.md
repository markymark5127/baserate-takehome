# Eval run `run6_all_fixes`

```json
{
 "label": "run6_all_fixes",
 "n": 25,
 "errors": 0,
 "facts": 1.0,
 "abstain_ok": 1.0,
 "src_recall": 1.0,
 "note_flag": 1.0,
 "cit_valid_raw": 1.0,
 "citations_total": 104,
 "repaired": 0,
 "dropped": 0,
 "answers_with_ungrounded_numbers": 7,
 "claims_checked": 193,
 "claims_removed": 0,
 "citations_added": 71,
 "grounding_errors": 0,
 "repair_rounds": 6,
 "unsupported_before_repair": 6,
 "avg_sec": 9.832,
 "total_cost_usd": 2.0
}
```

| id | cat | facts | abstain_ok | src_recall | note_flag | cites | raw_valid | repaired | dropped | claims | removed | cit_added | ungrounded | sec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 6 | 0 | 2 | - | 7.5 |
| C10 | note_conflict | 1.0 | True | 1.0 | True | 5 | 1.0 | 0 | 0 | 9 | 0 | 3 | - | 14.6 |
| C11 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 9 | 0 | 2 | 30 47 | 7.7 |
| C12 | note_conflict | 1.0 | True | 1.0 | True | 6 | 1.0 | 0 | 0 | 11 | 0 | 4 | 21 22 92.3 | 8.2 |
| C13 | abstain | - | True | - | - | 0 | - | 0 | 0 | 0 | 0 | 0 | - | 4.1 |
| C14 | not_in_docs | 1.0 | True | 1.0 | - | 5 | 1.0 | 0 | 0 | 7 | 0 | 1 | 56.9 | 7.8 |
| C15 | ambiguous | 1.0 | True | - | - | 9 | 1.0 | 0 | 0 | 7 | 0 | 1 | 28 | 25.4 |
| C16 | fiscal_mapping | 1.0 | True | 1.0 | - | 4 | 1.0 | 0 | 0 | 7 | 0 | 4 | - | 11.2 |
| C17 | fact | 1.0 | True | 1.0 | - | 4 | 1.0 | 0 | 0 | 8 | 0 | 2 | - | 15.7 |
| C2 | note_conflict | 1.0 | True | 1.0 | True | 2 | 1.0 | 0 | 0 | 7 | 0 | 5 | - | 5.3 |
| C3 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 5 | 0 | 2 | - | 6.5 |
| C4 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 6 | 0 | 3 | - | 5.9 |
| C5 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 9 | 0 | 4 | - | 6.6 |
| C6 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 8 | 0 | 4 | - | 6.5 |
| C7 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 5 | 0 | 1 | - | 9.7 |
| C8 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 10 | 0 | 5 | 677 73 | 6.2 |
| C9 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 7 | 0 | 4 | - | 6.9 |
| S1 | fact | 1.0 | True | 1.0 | - | 3 | 1.0 | 0 | 0 | 4 | 0 | 1 | - | 8.8 |
| S2 | guidance | 1.0 | True | 1.0 | - | 5 | 1.0 | 0 | 0 | 9 | 0 | 0 | - | 13.4 |
| S3 | fact | 1.0 | True | 1.0 | - | 4 | 1.0 | 0 | 0 | 8 | 0 | 2 | - | 6.8 |
| S4 | multi_period | 1.0 | True | 1.0 | - | 6 | 1.0 | 0 | 0 | 21 | 0 | 10 | 1.5 3.2 | 12.3 |
| S5 | multi_period | 1.0 | True | 1.0 | - | 7 | 1.0 | 0 | 0 | 6 | 0 | 1 | - | 21.0 |
| S6 | abstain | - | True | - | - | 2 | 1.0 | 0 | 0 | 8 | 0 | 3 | - | 9.6 |
| S7 | false_premise | 1.0 | True | 1.0 | True | 6 | 1.0 | 0 | 0 | 9 | 0 | 4 | 2.5 | 7.7 |
| S8 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 7 | 0 | 3 | - | 10.4 |
