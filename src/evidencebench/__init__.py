"""EvidenceBench: deterministic, local-first evaluation of AI answer grounding."""

__version__ = "0.1.0"

from .models import ClaimStatus, EvaluationResult

__all__ = ["ClaimStatus", "EvaluationResult", "__version__"]
