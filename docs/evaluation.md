# Evaluation pipeline

The default flow is:

1. **Ingest**: read supported local documents; reject oversized or malformed direct inputs.
2. **Normalize**: normalize line endings and harmless Unicode variation.
3. **Chunk**: create stable bounded chunks with source locations where available.
4. **Read question and answer**: these are UTF-8 files supplied by the caller.
5. **Extract claims**: split bullets, non-empty lines, and sentence boundaries using the deterministic segmenter.
6. **Retrieve evidence**: rank chunks by normalized content-token overlap and keep the top three above `0.15` by default.
7. **Evaluate**: apply the documented lexical coverage thresholds and narrow negation check.
8. **Calculate metrics**: derive counts and rates from statuses.
9. **Report**: serialize the same result to terminal, JSON, or static HTML.

## A minimal library use

```python
from evidencebench.chunking import chunk_documents
from evidencebench.evaluation import evaluate_answer
from evidencebench.ingestion import load_documents

sources = load_documents("docs")
chunks = chunk_documents(sources)
result = evaluate_answer(
    "What does the document recommend?",
    "The document recommends regular inspection.",
    chunks,
)
print(result.metrics.to_dict())
```

## Choosing a stronger evaluator

The deterministic baseline is useful for regression and reproducibility but cannot reliably handle paraphrase, anaphora, tables, or nuanced contradictions. A model-backed evaluator should return the same claim/evidence structure, include a rationale, preserve `INSUFFICIENT_EVIDENCE`, and delimit system instructions, question, answer, and source material. It should also record the provider and whether text leaves the machine.
