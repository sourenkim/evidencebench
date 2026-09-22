# Benchmark

The included benchmark is intentionally small, original, and reproducible rather than a claim about general AI quality.

## Contents

- 20 Markdown documents authored for this repository
- 100 JSON cases
- 480 labeled claims
- Four labels: `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, `INSUFFICIENT_EVIDENCE`
- Per-claim ground-truth entries with a source document reference

Each case lists its allowed sources so evaluation does not accidentally retrieve from unrelated documents. The dataset is released under the repository MIT license; it contains no copied third-party material.

## Run

```bash
evidencebench validate benchmark
evidencebench benchmark benchmark
evidencebench benchmark benchmark --format json --output reports/benchmark.json
```

The runner validates the manifest, executes the same default pipeline used by the CLI, and reports actual runtime measurements. It reports status detection recall, false-positive rate, exact case status match, confusion counts, and malformed claim-count cases. It does not claim a score until it has run.

## Interpretation

This benchmark is designed as a regression sanity check for the deterministic baseline. Its synthetic language is intentionally close to the source text, so high performance would not establish semantic robustness. A change that improves this dataset can still harm paraphrases, real PDFs, or domain-specific claims. Add diverse, legally redistributable cases before using results to compare systems.
