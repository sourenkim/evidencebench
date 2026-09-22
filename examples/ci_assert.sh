#!/usr/bin/env bash
set -euo pipefail

# This deliberately fails if the example answer contains too many unsupported claims.
python -m evidencebench assert \
  --sources examples/docs \
  --question examples/question.txt \
  --answer examples/answer.txt \
  --minimum-evidence-coverage 0.60 \
  --maximum-unsupported-rate 0.40
