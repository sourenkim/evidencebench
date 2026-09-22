# Providers

EvidenceBench's core has no vendor SDK dependencies and no required API key. The `evidencebench.providers` module defines two protocols:

- `LLMProvider.extract_claims(question, answer)` for model-backed segmentation.
- `LLMProvider.evaluate_claim(question, claim, evidence)` for model-backed verification.
- `EmbeddingProvider.embed(texts)` and `similarity(query, candidate)` for semantic retrieval.

Adapters can live in an application or a separate package. The default CLI does not discover or call them automatically.

## Adapter requirements

A provider adapter should:

1. Preserve claim text and stable identifiers.
2. Return one of the four supported statuses, including `INSUFFICIENT_EVIDENCE` when evidence is ambiguous or absent.
3. Attach the exact evidence snippets supplied to the model and never fabricate locations.
4. Delimit system instructions, question, answer, and source material in the prompt.
5. Treat all source material as untrusted data, not instructions.
6. Record provider name, model, and whether user content leaves the machine.
7. Provide a fake implementation for tests so CI stays offline.

The core does not claim to implement Anthropic, OpenAI, local-model, or embedding adapters in 0.1.0; these are extension points only.
