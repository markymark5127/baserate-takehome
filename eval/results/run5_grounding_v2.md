# Eval run `run5_grounding_v2`

```json
{
 "label": "run5_grounding_v2",
 "n": 25,
 "errors": 0,
 "facts": 0.986,
 "abstain_ok": 1.0,
 "src_recall": 1.0,
 "note_flag": 1.0,
 "cit_valid_raw": 1.0,
 "citations_total": 100,
 "repaired": 0,
 "dropped": 0,
 "answers_with_ungrounded_numbers": 9,
 "claims_checked": 220,
 "claims_removed": 9,
 "citations_added": 94,
 "grounding_errors": 0,
 "avg_sec": 11.148,
 "total_cost_usd": 0.876
}
```

| id | cat | facts | abstain_ok | src_recall | note_flag | cites | raw_valid | repaired | dropped | claims | removed | cit_added | ungrounded | sec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 8 | 0 | 4 | 20 | 7.8 |
| C10 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 8 | 0 | 5 | 330 | 7.8 |
| C11 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 12 | 0 | 5 | 30 47 | 20.4 |
| C12 | note_conflict | 1.0 | True | 1.0 | True | 5 | 1.0 | 0 | 0 | 12 | 0 | 5 | 21 22 92.3 | 19.3 |
| C13 | abstain | - | True | - | - | 0 | - | 0 | 0 | 0 | 0 | 0 | - | 21.1 |
| C14 | not_in_docs | 1.0 | True | 1.0 | - | 5 | 1.0 | 0 | 0 | 6 | 0 | 2 | - | 25.9 |
| C15 | ambiguous | 0.67 | True | - | - | 4 | 1.0 | 0 | 0 | 11 | 4 | 2 | 28 | 21.0 |
| C16 | fiscal_mapping | 1.0 | True | 1.0 | - | 6 | 1.0 | 0 | 0 | 8 | 2 | 2 | - | 16.5 |
| C17 | fact | 1.0 | True | 1.0 | - | 3 | 1.0 | 0 | 0 | 7 | 0 | 2 | - | 7.0 |
| C2 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 8 | 1 | 4 | - | 6.3 |
| C3 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 5 | 0 | 2 | - | 6.4 |
| C4 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 6 | 0 | 2 | - | 7.3 |
| C5 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 10 | 0 | 4 | - | 8.0 |
| C6 | note_conflict | 1.0 | True | 1.0 | True | 5 | 1.0 | 0 | 0 | 9 | 0 | 4 | - | 7.3 |
| C7 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 7 | 0 | 3 | - | 6.1 |
| C8 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 11 | 0 | 6 | 677 73 | 7.0 |
| C9 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 11 | 0 | 6 | - | 7.8 |
| S1 | fact | 1.0 | True | 1.0 | - | 3 | 1.0 | 0 | 0 | 7 | 0 | 3 | - | 6.5 |
| S2 | guidance | 1.0 | True | 1.0 | - | 6 | 1.0 | 0 | 0 | 13 | 0 | 5 | - | 10.9 |
| S3 | fact | 1.0 | True | 1.0 | - | 5 | 1.0 | 0 | 0 | 10 | 0 | 5 | - | 7.6 |
| S4 | multi_period | 1.0 | True | 1.0 | - | 6 | 1.0 | 0 | 0 | 16 | 1 | 6 | 1.5 3.2 3.6 | 13.8 |
| S5 | multi_period | 1.0 | True | 1.0 | - | 5 | 1.0 | 0 | 0 | 3 | 1 | 1 | - | 11.6 |
| S6 | abstain | - | True | - | - | 2 | 1.0 | 0 | 0 | 8 | 0 | 3 | - | 9.4 |
| S7 | false_premise | 1.0 | True | 1.0 | True | 6 | 1.0 | 0 | 0 | 13 | 0 | 7 | 2.5 | 8.6 |
| S8 | note_conflict | 1.0 | True | 1.0 | True | 5 | 1.0 | 0 | 0 | 11 | 0 | 6 | 12 | 7.3 |
