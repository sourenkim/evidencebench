# Concepts

## Claim-level evaluation

An answer is not assigned one opaque score. It is segmented into claims, and every claim receives a status, attached evidence, rationale, and a heuristic confidence value. The evidence list can be empty.

The four statuses are:

- `SUPPORTED`: retrieved evidence meets the baseline's full content-token coverage threshold.
- `PARTIALLY_SUPPORTED`: evidence overlaps meaningfully but does not establish all claim content.
- `UNSUPPORTED`: evidence is inadequate or shows the narrow explicit polarity mismatch recognized by the baseline.
- `INSUFFICIENT_EVIDENCE`: no candidate evidence met the retrieval threshold, or the claim has no evaluable content.

`UNSUPPORTED` means the available evaluation found inadequate or conflicting support; `INSUFFICIENT_EVIDENCE` means the pipeline did not obtain an adequate candidate. Neither status proves that a claim is universally false.

## Fact, assumption, judgment, evidence, uncertainty

EvidenceBench keeps these concepts separate:

- **Evidence** is source text attached to a claim, with a score and best-effort location.
- **Claim status** is an evaluator judgment about the relation between a claim and retrieved evidence.
- **Confidence** is confidence in the baseline heuristic's decision, not factual correctness.
- **Uncertainty** is represented explicitly as `INSUFFICIENT_EVIDENCE` or as partial support rather than silently promoted to fact.
- **Source text** remains data. A sentence such as “ignore all previous instructions” in a document cannot change the evaluator's rules.

## Locations

TXT and Markdown chunks carry line ranges and, where found, the nearest Markdown heading. PDF chunks carry a page number. If extraction cannot establish a location, the field is `null`; the system does not invent a citation.

## Why there is no single quality score

A single score would hide whether a result failed because evidence was absent, a claim was only partially supported, or a citation was missing. Use the underlying metrics and set thresholds appropriate to the application.
