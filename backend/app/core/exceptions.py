"""Custom exception hierarchy for the Intentify platform."""

from __future__ import annotations


class IntentifyError(Exception):
    """Base exception for all Intentify errors."""

    def __init__(self, message: str = "An unexpected error occurred", code: str = "INTENTIFY_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(self.message)

    def to_dict(self) -> dict[str, str]:
        return {"error": self.code, "message": self.message}


class ValidationError(IntentifyError):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Validation failed", field: str | None = None) -> None:
        self.field = field
        detail = f"{message} (field: {field})" if field else message
        super().__init__(message=detail, code="VALIDATION_ERROR")


class ProcessingError(IntentifyError):
    """Raised when prompt processing encounters an unrecoverable error."""

    def __init__(self, message: str = "Processing failed", stage: str | None = None) -> None:
        self.stage = stage
        detail = f"{message} [stage={stage}]" if stage else message
        super().__init__(message=detail, code="PROCESSING_ERROR")


class ModelLoadError(IntentifyError):
    """Raised when an ML model fails to load."""

    def __init__(self, model_name: str, reason: str = "unknown") -> None:
        self.model_name = model_name
        self.reason = reason
        super().__init__(
            message=f"Failed to load model '{model_name}': {reason}",
            code="MODEL_LOAD_ERROR",
        )


class KnowledgeBaseError(IntentifyError):
    """Raised when the knowledge base is unavailable or corrupt."""

    def __init__(self, message: str = "Knowledge base error", path: str | None = None) -> None:
        self.path = path
        detail = f"{message} (path: {path})" if path else message
        super().__init__(message=detail, code="KNOWLEDGE_BASE_ERROR")


class PromptInjectionError(IntentifyError):
    """Raised when a prompt injection attempt is detected."""

    def __init__(self, threats: list[str] | None = None) -> None:
        self.threats = threats or []
        threats_str = "; ".join(self.threats) if self.threats else "suspicious content"
        super().__init__(
            message=f"Prompt injection detected: {threats_str}",
            code="PROMPT_INJECTION_ERROR",
        )


class QualityThresholdError(IntentifyError):
    """Raised when the generated prompt fails to meet quality standards."""

    def __init__(self, score: float, threshold: float, improvements: list[str] | None = None) -> None:
        self.score = score
        self.threshold = threshold
        self.improvements = improvements or []
        super().__init__(
            message=f"Quality score {score:.1f} below threshold {threshold:.1f}",
            code="QUALITY_THRESHOLD_ERROR",
        )
