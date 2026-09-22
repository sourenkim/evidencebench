# Metrics

All metrics are calculated from claim statuses and attached evidence. With zero claims, rates are `0.0` rather than `NaN`.

| Metric | Formula | Interpretation | Limitation |
|---|---|---|---|
| Evidence coverage | `SUPPORTED / total claims` | Share of claims fully supported by the configured evaluator | Strict and evaluator-dependent; partial support does not count as full coverage |
| Unsupported claim rate | `UNSUPPORTED / total claims` | Share needing review because available evidence is inadequate or conflicting | Not the probability that claims are false |
| Partial support rate | `PARTIALLY_SUPPORTED / total claims` | Share for which the evidence covers only part of the claim | Token overlap can misjudge semantics |
| Citation coverage | `claims with >= 1 evidence item / total claims` | Share with an attached retrieved source reference | A citation can be relevant without entailing a claim |
| Evidence retrieval rate | `claims with >= 1 retrieved candidate / total claims` | Whether retrieval found any candidate above its threshold | It measures retrieval, not adequacy or truth |

The default lexical evaluator uses normalized content-token overlap. A score of at least `0.80` is `SUPPORTED`; at least `0.35` is `PARTIALLY_SUPPORTED`; lower overlap with a retrieved candidate is `UNSUPPORTED`; no candidate is `INSUFFICIENT_EVIDENCE`. These thresholds are implementation details of the 0.1 baseline, not universal standards.

## Thresholds

`evidencebench assert` supports:

- `--minimum-evidence-coverage 0.90`
- `--maximum-unsupported-rate 0.05`
- `--maximum-partial-rate 0.10`

A minimum fails when actual coverage is lower. A maximum fails when actual rate is higher. Threshold failures return exit code 1; malformed inputs return exit code 2.

## Confidence warning

The `confidence` field is a bounded heuristic overlap value. It is not a model's probability, does not measure factual correctness, and must not be used as a substitute for human review or a calibrated evaluation study.
