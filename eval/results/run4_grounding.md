# Eval run `run4_grounding`

```json
{
 "label": "run4_grounding",
 "n": 25,
 "errors": 0,
 "facts": 0.986,
 "abstain_ok": 1.0,
 "src_recall": 1.0,
 "note_flag": 1.0,
 "cit_valid_raw": 1.0,
 "citations_total": 106,
 "repaired": 0,
 "dropped": 0,
 "answers_with_ungrounded_numbers": 4,
 "claims_checked": 224,
 "claims_removed": 45,
 "citations_added": 75,
 "grounding_errors": 0,
 "avg_sec": 8.756,
 "total_cost_usd": 1.215
}
```

| id | cat | facts | abstain_ok | src_recall | note_flag | cites | raw_valid | repaired | dropped | claims | removed | cit_added | ungrounded | sec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 8 | 1 | 3 | - | 8.1 |
| C10 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 10 | 1 | 5 | 330 | 7.2 |
| C11 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 13 | 3 | 4 | 30 47 | 8.5 |
| C12 | note_conflict | 1.0 | True | 1.0 | True | 6 | 1.0 | 0 | 0 | 9 | 3 | 2 | - | 8.5 |
| C13 | abstain | - | True | - | - | 0 | - | 0 | 0 | 0 | 0 | 0 | - | 4.5 |
| C14 | not_in_docs | 1.0 | True | 1.0 | - | 5 | 1.0 | 0 | 0 | 8 | 2 | 2 | - | 7.6 |
| C15 | ambiguous | 0.67 | True | - | - | 8 | 1.0 | 0 | 0 | 12 | 3 | 2 | - | 16.6 |
| C16 | fiscal_mapping | 1.0 | True | 1.0 | - | 7 | 1.0 | 0 | 0 | 10 | 2 | 2 | - | 12.6 |
| C17 | fact | 1.0 | True | 1.0 | - | 4 | 1.0 | 0 | 0 | 8 | 1 | 2 | - | 7.1 |
| C2 | note_conflict | 1.0 | True | 1.0 | True | 2 | 1.0 | 0 | 0 | 5 | 1 | 3 | - | 5.4 |
| C3 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 5 | 2 | 1 | - | 5.9 |
| C4 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 6 | 1 | 3 | - | 8.0 |
| C5 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 9 | 0 | 4 | - | 6.9 |
| C6 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 9 | 3 | 4 | - | 6.7 |
| C7 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 7 | 4 | 0 | - | 7.7 |
| C8 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 8 | 1 | 4 | - | 6.9 |
| C9 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 8 | 1 | 2 | - | 7.3 |
| S1 | fact | 1.0 | True | 1.0 | - | 3 | 1.0 | 0 | 0 | 8 | 2 | 1 | - | 8.2 |
| S2 | guidance | 1.0 | True | 1.0 | - | 4 | 1.0 | 0 | 0 | 12 | 1 | 4 | - | 9.7 |
| S3 | fact | 1.0 | True | 1.0 | - | 5 | 1.0 | 0 | 0 | 11 | 2 | 5 | - | 8.3 |
| S4 | multi_period | 1.0 | True | 1.0 | - | 6 | 1.0 | 0 | 0 | 22 | 4 | 9 | 1.5 3.2 | 11.4 |
| S5 | multi_period | 1.0 | True | 1.0 | - | 8 | 1.0 | 0 | 0 | 10 | 2 | 3 | - | 14.3 |
| S6 | abstain | - | True | - | - | 2 | 1.0 | 0 | 0 | 8 | 3 | 4 | - | 14.1 |
| S7 | false_premise | 1.0 | True | 1.0 | True | 6 | 1.0 | 0 | 0 | 11 | 1 | 5 | 2.5 | 9.6 |
| S8 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 7 | 1 | 1 | - | 7.8 |
