"""Domain errors with user-facing messages."""


class EvidenceBenchError(Exception):
    """Base error for expected input and evaluation failures."""


class InputError(EvidenceBenchError):
    """Raised when a user-provided file or option is invalid."""


class UnsupportedFormatError(InputError):
    """Raised for a file type not supported by this installation."""


class ExtractionError(InputError):
    """Raised when a document cannot be safely extracted."""
