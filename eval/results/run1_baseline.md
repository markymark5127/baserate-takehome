# Eval run `run1_baseline`

```json
{
 "label": "run1_baseline",
 "n": 25,
 "errors": 0,
 "facts": 0.989,
 "abstain_ok": 1.0,
 "src_recall": 1.0,
 "note_flag": 0.714,
 "cit_valid_raw": 1.0,
 "citations_total": 72,
 "repaired": 0,
 "dropped": 0,
 "answers_with_ungrounded_numbers": 24,
 "avg_sec": 6.524,
 "total_cost_usd": 1.269
}
```

| id | cat | facts | abstain_ok | src_recall | note_flag | cites | raw_valid | repaired | dropped | ungrounded | sec |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | note_conflict | 1.0 | True | 1.0 | False | 1 | 1.0 | 0 | 0 | 26 | 4.3 |
| C10 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 26 330 | 7.1 |
| C11 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 26 30 47 | 9.2 |
| C12 | note_conflict | 1.0 | True | 1.0 | True | 5 | 1.0 | 0 | 0 | 19 21 27 92.3 | 6.9 |
| C13 | abstain | - | True | - | - | 0 | - | 0 | 0 | - | 4.0 |
| C14 | not_in_docs | 1.0 | True | 1.0 | - | 4 | 1.0 | 0 | 0 | 26 | 7.4 |
| C15 | ambiguous | 1.0 | True | - | - | 4 | 1.0 | 0 | 0 | 16.9 23 26 27 6.14 | 11.2 |
| C16 | fiscal_mapping | 1.0 | True | 1.0 | - | 2 | 1.0 | 0 | 0 | 27 | 5.9 |
| C17 | fact | 1.0 | True | 1.0 | - | 3 | 1.0 | 0 | 0 | 26 | 5.3 |
| C2 | note_conflict | 1.0 | True | 1.0 | True | 1 | 1.0 | 0 | 0 | 26 | 4.1 |
| C3 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 26 | 4.9 |
| C4 | note_conflict | 1.0 | True | 1.0 | True | 2 | 1.0 | 0 | 0 | 26 | 5.5 |
| C5 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 26 | 6.3 |
| C6 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 26 | 5.1 |
| C7 | note_conflict | 1.0 | True | 1.0 | False | 2 | 1.0 | 0 | 0 | 26 27 | 4.8 |
| C8 | note_conflict | 1.0 | True | 1.0 | False | 2 | 1.0 | 0 | 0 | 27 | 5.3 |
| C9 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 26 | 6.4 |
| S1 | fact | 1.0 | True | 1.0 | - | 1 | 1.0 | 0 | 0 | 26 | 4.5 |
| S2 | guidance | 0.75 | True | 1.0 | - | 2 | 1.0 | 0 | 0 | 27 48 | 6.3 |
| S3 | fact | 1.0 | True | 1.0 | - | 4 | 1.0 | 0 | 0 | 26 | 7.5 |
| S4 | multi_period | 1.0 | True | 1.0 | - | 4 | 1.0 | 0 | 0 | 1.5 150 | 8.9 |
| S5 | multi_period | 1.0 | True | 1.0 | - | 4 | 1.0 | 0 | 0 | 26 27 | 10.3 |
| S6 | abstain | - | True | - | - | 2 | 1.0 | 0 | 0 | 26 27 | 9.4 |
| S7 | false_premise | 1.0 | True | 1.0 | False | 4 | 1.0 | 0 | 0 | 26 | 5.4 |
| S8 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 26 | 7.1 |
