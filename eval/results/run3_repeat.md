# Eval run `run3_repeat`

```json
{
 "label": "run3_repeat",
 "n": 25,
 "errors": 0,
 "facts": 1.0,
 "abstain_ok": 1.0,
 "src_recall": 1.0,
 "note_flag": 1.0,
 "cit_valid_raw": 1.0,
 "citations_total": 99,
 "repaired": 0,
 "dropped": 0,
 "answers_with_ungrounded_numbers": 7,
 "avg_sec": 7.628,
 "total_cost_usd": 1.163
}
```

| id | cat | facts | abstain_ok | src_recall | note_flag | cites | raw_valid | repaired | dropped | ungrounded | sec |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | - | 6.7 |
| C10 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 330 | 7.4 |
| C11 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 30 | 7.3 |
| C12 | note_conflict | 1.0 | True | 1.0 | True | 6 | 1.0 | 0 | 0 | 21 22 92.3 | 8.2 |
| C13 | abstain | - | True | - | - | 0 | - | 0 | 0 | - | 3.9 |
| C14 | not_in_docs | 1.0 | True | 1.0 | - | 5 | 1.0 | 0 | 0 | - | 6.9 |
| C15 | ambiguous | 1.0 | True | - | - | 6 | 1.0 | 0 | 0 | - | 16.2 |
| C16 | fiscal_mapping | 1.0 | True | 1.0 | - | 4 | 1.0 | 0 | 0 | - | 6.7 |
| C17 | fact | 1.0 | True | 1.0 | - | 3 | 1.0 | 0 | 0 | - | 5.9 |
| C2 | note_conflict | 1.0 | True | 1.0 | True | 2 | 1.0 | 0 | 0 | - | 5.6 |
| C3 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | - | 5.5 |
| C4 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | - | 6.1 |
| C5 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | - | 6.4 |
| C6 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | - | 6.7 |
| C7 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | - | 6.4 |
| C8 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 677 73 | 7.3 |
| C9 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | - | 6.4 |
| S1 | fact | 1.0 | True | 1.0 | - | 3 | 1.0 | 0 | 0 | - | 6.1 |
| S2 | guidance | 1.0 | True | 1.0 | - | 6 | 1.0 | 0 | 0 | 28 | 11.2 |
| S3 | fact | 1.0 | True | 1.0 | - | 5 | 1.0 | 0 | 0 | - | 7.4 |
| S4 | multi_period | 1.0 | True | 1.0 | - | 8 | 1.0 | 0 | 0 | 1.5 150 3.2 | 13.6 |
| S5 | multi_period | 1.0 | True | 1.0 | - | 4 | 1.0 | 0 | 0 | - | 10.5 |
| S6 | abstain | - | True | - | - | 2 | 1.0 | 0 | 0 | - | 7.7 |
| S7 | false_premise | 1.0 | True | 1.0 | True | 5 | 1.0 | 0 | 0 | 2.5 | 7.4 |
| S8 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | - | 7.2 |
