# Eval run `run8_quoted_passage`

```json
{
 "label": "run8_quoted_passage",
 "n": 25,
 "errors": 0,
 "facts": 1.0,
 "abstain_ok": 1.0,
 "src_recall": 1.0,
 "note_flag": 1.0,
 "cit_valid_raw": 1.0,
 "citations_total": 135,
 "repaired": 0,
 "dropped": 0,
 "answers_with_ungrounded_numbers": 2,
 "claims_checked": 220,
 "claims_removed": 7,
 "citations_added": 77,
 "citations_fixed": 1,
 "grounding_errors": 0,
 "repair_rounds": 16,
 "unsupported_before_repair": 43,
 "avg_sec": 12.984,
 "total_cost_usd": 2.094
}
```

| id | cat | facts | abstain_ok | src_recall | note_flag | cites | raw_valid | repaired | dropped | claims | removed | cit_added | ungrounded | sec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 7 | 0 | 2 | - | 13.4 |
| C10 | note_conflict | 1.0 | True | 1.0 | True | 5 | 1.0 | 0 | 0 | 8 | 1 | 3 | - | 14.6 |
| C11 | note_conflict | 1.0 | True | 1.0 | True | 8 | 1.0 | 0 | 0 | 13 | 3 | 3 | - | 21.7 |
| C12 | note_conflict | 1.0 | True | 1.0 | True | 8 | 1.0 | 0 | 0 | 13 | 1 | 5 | - | 17.8 |
| C13 | abstain | - | True | - | - | 0 | - | 0 | 0 | 0 | 0 | 0 | - | 4.3 |
| C14 | not_in_docs | 1.0 | True | 1.0 | - | 5 | 1.0 | 0 | 0 | 9 | 0 | 4 | - | 16.5 |
| C15 | ambiguous | 1.0 | True | - | - | 13 | 1.0 | 0 | 0 | 16 | 0 | 3 | - | 30.7 |
| C16 | fiscal_mapping | 1.0 | True | 1.0 | - | 4 | 1.0 | 0 | 0 | 5 | 0 | 2 | - | 5.9 |
| C17 | fact | 1.0 | True | 1.0 | - | 4 | 1.0 | 0 | 0 | 7 | 0 | 2 | - | 7.1 |
| C2 | note_conflict | 1.0 | True | 1.0 | True | 2 | 1.0 | 0 | 0 | 6 | 0 | 4 | - | 9.8 |
| C3 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 4 | 0 | 1 | - | 5.9 |
| C4 | note_conflict | 1.0 | True | 1.0 | True | 3 | 1.0 | 0 | 0 | 7 | 0 | 4 | - | 6.0 |
| C5 | note_conflict | 1.0 | True | 1.0 | True | 6 | 1.0 | 0 | 0 | 8 | 1 | 1 | - | 10.5 |
| C6 | note_conflict | 1.0 | True | 1.0 | True | 5 | 1.0 | 0 | 0 | 8 | 0 | 3 | - | 6.9 |
| C7 | note_conflict | 1.0 | True | 1.0 | True | 5 | 1.0 | 0 | 0 | 7 | 0 | 2 | - | 10.6 |
| C8 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 9 | 1 | 5 | - | 10.5 |
| C9 | note_conflict | 1.0 | True | 1.0 | True | 5 | 1.0 | 0 | 0 | 10 | 0 | 5 | - | 12.1 |
| S1 | fact | 1.0 | True | 1.0 | - | 3 | 1.0 | 0 | 0 | 3 | 0 | 1 | - | 6.0 |
| S2 | guidance | 1.0 | True | 1.0 | - | 7 | 1.0 | 0 | 0 | 17 | 0 | 7 | - | 19.7 |
| S3 | fact | 1.0 | True | 1.0 | - | 6 | 1.0 | 0 | 0 | 11 | 0 | 5 | - | 13.1 |
| S4 | multi_period | 1.0 | True | 1.0 | - | 12 | 1.0 | 0 | 0 | 15 | 0 | 5 | 1.5 | 27.2 |
| S5 | multi_period | 1.0 | True | 1.0 | - | 10 | 1.0 | 0 | 0 | 10 | 0 | 2 | - | 28.1 |
| S6 | abstain | - | True | - | - | 3 | 1.0 | 0 | 0 | 10 | 0 | 1 | - | 7.9 |
| S7 | false_premise | 1.0 | True | 1.0 | True | 6 | 1.0 | 0 | 0 | 10 | 0 | 4 | 2.5 | 11.7 |
| S8 | note_conflict | 1.0 | True | 1.0 | True | 4 | 1.0 | 0 | 0 | 7 | 0 | 3 | - | 6.6 |
