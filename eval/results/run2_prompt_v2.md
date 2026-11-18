# Eval run `run2_prompt_v2`

```json
{
 "label": "run2_prompt_v2",
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
 "avg_sec": 8.06,
 "total_cost_usd": 1.526
}
```

| id | cat | facts | abstain_ok | src_recall | note_flag | cites | raw_valid | repaired | dropped | ungrounded | sec |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | - | 6.7 |
| C10 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 330 | 7.1 |
| C11 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | - | 9.6 |
| C12 | note_conflict | 1.0 | True | 1.0 | True | 6 | 1.0 | 0 | 0 | 21 22 92.3 | 10.1 |
| C13 | abstain | - | True | - | - | 0 | - | 0 | 0 | - | 5.7 |
| C14 | not_in_docs | 1.0 | True | 1.0 | - | 5 | 1.0 | 0 | 0 | 12 | 7.2 |
| C15 | ambiguous | 1.0 | True | - | - | 4 | 1.0 | 0 | 0 | - | 10.8 |
| C16 | fiscal_mapping | 1.0 | True | 1.0 | - | 4 | 1.0 | 0 | 0 | - | 8.9 |
| C17 | fact | 1.0 | True | 1.0 | - | 3 | 1.0 | 0 | 0 | - | 6.7 |
| C2 | note_conflict | 1.0 | True | 1.0 | True | 2 | 1.0 | 0 | 0 | - | 5.6 |
| C3 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | - | 6.0 |
| C4 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | - | 6.3 |
| C5 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | - | 6.8 |
| C6 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | - | 6.6 |
| C7 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | - | 6.7 |
| C8 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | - | 7.0 |
| C9 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | - | 7.0 |
| S1 | fact | 1.0 | True | 1.0 | - | 3 | 1.0 | 0 | 0 | - | 7.0 |
| S2 | guidance | 1.0 | True | 1.0 | - | 5 | 1.0 | 0 | 0 | 28 | 11.4 |
| S3 | fact | 1.0 | True | 1.0 | - | 5 | 1.0 | 0 | 0 | - | 7.6 |
| S4 | multi_period | 1.0 | True | 1.0 | - | 6 | 1.0 | 0 | 0 | 1.5 3.2 3.6 | 13.6 |
| S5 | multi_period | 1.0 | True | 1.0 | - | 7 | 1.0 | 0 | 0 | - | 12.3 |
| S6 | abstain | - | True | - | - | 2 | 1.0 | 0 | 0 | - | 8.3 |
| S7 | false_premise | 1.0 | True | 1.0 | True | 6 | 1.0 | 0 | 0 | 2.5 | 9.2 |
| S8 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 13 14 | 7.3 |
