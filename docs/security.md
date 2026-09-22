# Security and privacy

## Threat model

Source documents, questions, answers, filenames, and report output are untrusted input. A source document may contain prompt-injection text such as “ignore previous instructions.” It is data, not a command to EvidenceBench or to a future model provider.

## Current controls

- Directory traversal is not performed from document contents. Paths come from explicit CLI arguments.
- Symlink files and symlink source roots are rejected to avoid surprising file access.
- Files are bounded by a 10 MiB default limit before extraction.
- Text files must be UTF-8. Unsupported direct file extensions fail rather than being guessed.
- PDF extraction is isolated behind the optional dependency and parser errors become user-facing extraction errors.
- Generated HTML escapes question, answer, claim, rationale, document identifiers, locations, and evidence text. The report has no JavaScript or external resource loading.
- The default pipeline has no telemetry and makes no network calls.
- A future LLM adapter must delimit system instructions, question, answer, and source material. Source material must never be concatenated into an instruction channel without clear boundaries.

## External providers

The core package does not send anything remotely. If an application implements `LLMProvider` or `EmbeddingProvider` with a hosted service, the application is responsible for consent, data minimization, secret storage, provider retention settings, and documenting exactly which fields leave the machine. Never put API keys in source files, reports, fixtures, or issue comments.

## Remaining risks

The lexical baseline is not a security boundary for malicious PDFs; keep dependencies patched and consider sandboxing untrusted PDF parsing in high-risk deployments. Output files can contain sensitive source text by design, so protect report directories. A semantic provider may be vulnerable to prompt injection even when the baseline is not; provider adapters need adversarial tests.

Report suspected vulnerabilities privately to the maintainers rather than opening a public issue with exploit details. See `SECURITY.md` for the project contact policy.
