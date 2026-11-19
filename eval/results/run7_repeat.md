# Eval run `run7_repeat`

```json
{
 "label": "run7_repeat",
 "n": 25,
 "errors": 0,
 "facts": 1.0,
 "abstain_ok": 1.0,
 "src_recall": 1.0,
 "note_flag": 1.0,
 "cit_valid_raw": 1.0,
 "citations_total": 113,
 "repaired": 0,
 "dropped": 0,
 "answers_with_ungrounded_numbers": 6,
 "claims_checked": 226,
 "claims_removed": 0,
 "citations_added": 92,
 "grounding_errors": 0,
 "repair_rounds": 5,
 "unsupported_before_repair": 9,
 "avg_sec": 10.084,
 "total_cost_usd": 1.464
}
```

| id | cat | facts | abstain_ok | src_recall | note_flag | cites | raw_valid | repaired | dropped | claims | removed | cit_added | ungrounded | sec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 7 | 0 | 3 | - | 7.0 |
| C10 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 10 | 0 | 5 | 330 | 6.6 |
| C11 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 14 | 0 | 6 | 47 | 8.8 |
| C12 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 9 | 0 | 4 | 21 22 92.3 | 11.8 |
| C13 | abstain | - | True | - | - | 0 | - | 0 | 0 | 0 | 0 | 0 | - | 4.3 |
| C14 | not_in_docs | 1.0 | True | 1.0 | - | 6 | 1.0 | 0 | 0 | 11 | 0 | 4 | 56.9 | 13.3 |
| C15 | ambiguous | 1.0 | True | - | - | 9 | 1.0 | 0 | 0 | 13 | 0 | 3 | - | 18.5 |
| C16 | fiscal_mapping | 1.0 | True | 1.0 | - | 4 | 1.0 | 0 | 0 | 5 | 0 | 2 | - | 8.2 |
| C17 | fact | 1.0 | True | 1.0 | - | 4 | 1.0 | 0 | 0 | 8 | 0 | 2 | - | 7.6 |
| C2 | note_conflict | 1.0 | True | 1.0 | True | 2 | 1.0 | 0 | 0 | 7 | 0 | 5 | - | 5.6 |
| C3 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 5 | 0 | 2 | - | 6.2 |
| C4 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 7 | 0 | 3 | - | 5.7 |
| C5 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 9 | 0 | 4 | - | 6.7 |
| C6 | note_conflict | 1.0 | True | 1.0 | True | 5 | 1.0 | 0 | 0 | 7 | 0 | 2 | - | 6.6 |
| C7 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 7 | 0 | 2 | - | 6.3 |
| C8 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 9 | 0 | 6 | - | 6.7 |
| C9 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 7 | 0 | 4 | - | 6.9 |
| S1 | fact | 1.0 | True | 1.0 | - | 4 | 1.0 | 0 | 0 | 11 | 0 | 7 | - | 12.2 |
| S2 | guidance | 1.0 | True | 1.0 | - | 8 | 1.0 | 0 | 0 | 12 | 0 | 1 | - | 29.0 |
| S3 | fact | 1.0 | True | 1.0 | - | 5 | 1.0 | 0 | 0 | 11 | 0 | 5 | - | 7.8 |
| S4 | multi_period | 1.0 | True | 1.0 | - | 8 | 1.0 | 0 | 0 | 15 | 0 | 5 | 1.5 150 3.6 | 10.8 |
| S5 | multi_period | 1.0 | True | 1.0 | - | 7 | 1.0 | 0 | 0 | 10 | 0 | 3 | - | 13.2 |
| S6 | abstain | - | True | - | - | 4 | 1.0 | 0 | 0 | 11 | 0 | 5 | - | 18.2 |
| S7 | false_premise | 1.0 | True | 1.0 | True | 7 | 1.0 | 0 | 0 | 11 | 0 | 5 | - | 11.5 |
| S8 | note_conflict | 1.0 | True | 1.0 | True | 5 | 1.0 | 0 | 0 | 10 | 0 | 4 | 12 | 12.6 |
