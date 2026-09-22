# EvidenceBench Architecture

This file is a short orientation document. The detailed design is in [`docs/architecture.md`](docs/architecture.md).

```text
sources + question + answer
            |
     document ingestion
            |
 normalization + chunking
            |
 claim extraction ----> retrieval protocol ----> evaluation protocol
            |                                      |
            +---------------- result -------------+
                             |
                 deterministic metrics / reports
```

The default vertical slice is deliberately deterministic:

- `ingestion`: reads local TXT, Markdown, and optionally PDF files and preserves locations.
- `chunking`: makes stable, bounded chunks with source metadata.
- `claims`: turns answer bullets and sentences into near-atomic claims.
- `retrieval`: ranks chunks using normalized token overlap.
- `evaluation`: applies documented lexical heuristics; it can return unknown/insufficient evidence.
- `metrics`: calculates counts and rates without model calls.
- `reports`: serializes the same result to terminal, JSON, or standalone HTML.
- `providers`: protocols for replacing model-dependent stages without coupling the core to one vendor.
- `cli`: orchestration, input validation, exit codes, and CI thresholds.

The core passes typed dataclasses between stages. Reporters consume an evaluation result; they do not re-evaluate claims. This keeps calculations testable and makes the output reproducible.
