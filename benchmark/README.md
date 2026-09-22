# EvidenceBench benchmark dataset

This is a small, original, synthetic dataset generated for EvidenceBench 0.1.0. It contains 20 Markdown documents and 100 labeled question/answer cases (480 labeled claims). The documents and claims were authored for this repository; they are not copied from a third-party work. They are released under the repository MIT license.

Each case restricts retrieval to its listed source document and contains `ground_truth` labels for the four supported statuses. Run `evidencebench validate benchmark` before using it and `evidencebench benchmark benchmark` to measure the current implementation. Benchmark values are generated at runtime and are intentionally not hard-coded here.
