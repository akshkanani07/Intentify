"""Pydantic v2 schemas for the prompt generation API."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class PromptGenerationRequest(BaseModel):
    """Incoming request to generate a master prompt."""

    role: str = Field(
        default="",
        max_length=500,
        description="The professional role or persona (optional; extracted automatically if omitted)",
        examples=["Senior Python Developer"],
    )
    detail: str = Field(
        ...,
        min_length=1,
        max_length=100_000,
        description="Task description, problem statement, or single word input",
        examples=["Build a REST API for managing user authentication with JWT tokens"],
    )
    language: str | None = Field(
        default=None,
        max_length=50,
        description="Preferred response language (e.g. 'English', 'Hindi', 'Gujarati')",
    )
    tone: str | None = Field(
        default=None,
        max_length=50,
        description="Desired tone (e.g. 'professional', 'concise', 'academic')",
    )
    format: str | None = Field(
        default=None,
        max_length=100,
        description="Desired output format (e.g. 'step-by-step', 'table', 'code')",
    )


class PenaltyItem(BaseModel):
    """Structured invariant or rubric penalty item."""

    code: str = Field(..., description="Unique invariant penalty code (e.g. D2_DUPLICATE_SENTENCE, FORBIDDEN_PHRASE)")
    name: str = Field(default="", description="Descriptive penalty name")
    penalty: int = Field(..., description="Deduction points")
    is_hard_check: bool = Field(default=False, description="Whether this violation triggered a hard cap (score <= 70)")
    reason: str = Field(default="", description="Human-readable violation reason")


class QualityBreakdown(BaseModel):
    """Breakdown of quality sub-scores (weights sum to 100)."""

    clarity: float = Field(default=0.0, ge=0, le=20, description="Clarity score (max 20)")
    specificity: float = Field(default=0.0, ge=0, le=20, description="Specificity score (max 20)")
    context: float = Field(default=0.0, ge=0, le=15, description="Context score (max 15)")
    constraints: float = Field(default=0.0, ge=0, le=15, description="Constraints score (max 15)")
    output_format: float = Field(default=0.0, ge=0, le=15, description="Output format score (max 15)")
    ambiguity_handling: float = Field(default=0.0, ge=0, le=15, description="Ambiguity handling score (max 15)")
    total: float = Field(default=0.0, ge=0, le=100, description="Total composite quality score")


class ProcessingMetadata(BaseModel):
    """Execution metadata and cognitive pipeline telemetry."""

    detected_language: str
    detected_intent: str
    detected_domain: str
    processing_time_ms: float
    model_versions: dict[str, str] = Field(default_factory=dict)
    aligned_role: str | None = None
    original_role: str | None = None
    intent_confidence: float | None = None
    target_audience: str | None = None
    experience_level: str | None = None
    deliverable: str | None = None
    task_type: str | None = None
    risk_level: str | None = None
    identified_risks: list[str] = Field(default_factory=list)
    smart_assumptions: list[str] = Field(default_factory=list)
    cognitive_reasoning: dict[str, Any] = Field(default_factory=dict)
    cognitive_quality: dict[str, float] = Field(default_factory=dict)
    dynamic_headings: list[str] = Field(default_factory=list)
    writing_style: str | None = None
    formality_level: str | None = None
    user_emotion: str | None = None
    decision_priorities: list[str] = Field(default_factory=list)
    learned_memories_count: int = 0
    engine_mode: str = Field(default="concept_graph", description="Inference engine execution mode")
    content_source: str = Field(default="concept_graph", description="Source of content: concept_graph | generated | derived")
    reviewed: bool = Field(default=False, description="Whether the content graph has been human-reviewed")
    score_before_cap: float = Field(default=100.0, description="Honest score before hard check caps")
    score_after_cap: float = Field(default=100.0, description="Final quality score after hard check caps")
    penalties: list[PenaltyItem] = Field(default_factory=list, description="List of invariant penalties applied")
    winning_candidate_style: str = Field(default="standard", description="Selected candidate variant style")
    product_name: str | None = Field(default=None, description="Explicit product name extracted from input")
    contract: str | None = Field(default=None, description="Active contract schema (e.g. build_app, learn, debug)")
    subject: str | None = Field(default=None, description="Canonical subject or domain object")
    requester: str | None = Field(default=None, description="Role/identity of the requester")
    audience: str | None = Field(default=None, description="Target end users/audience")
    audience_source: str | None = Field(default=None, description="stated | assumed")
    proficiency: str | None = Field(default=None, description="Audience proficiency level")
    status: str = Field(default="final", description="final | draft (draft if any hard check failed)")
    content_share: dict[str, float] = Field(default_factory=dict, description="Proportion of reviewed, unreviewed, and generated content")
    model_name: str | None = Field(default=None, description="Local inference model name")


class PromptGenerationResponse(BaseModel):
    """Final output response returned to caller."""

    master_prompt: str
    assumptions: list[str] = Field(default_factory=list)
    quality_score: float | str
    improvements: list[str] = Field(default_factory=list)
    metadata: ProcessingMetadata | None = None
    breakdown: QualityBreakdown | None = None


class FeedbackRequest(BaseModel):
    """User feedback and exemplar submission request."""

    prompt_id: str | None = None
    prompt_text: str = Field(..., description="The compiled master prompt text")
    goal: str = Field(default="", description="The user's goal or raw input")
    domain: str = Field(default="", description="The domain of the prompt")
    rating: int = Field(default=5, ge=1, le=5, description="User rating from 1 to 5")
    user_edits: str | None = Field(default=None, description="Optional user-edited prompt")
    comments: str | None = Field(default=None, description="Optional feedback notes")


class FeedbackResponse(BaseModel):
    """Response returned upon feedback ingestion."""

    status: str
    message: str
    admitted_to_learning_store: bool
    quality_score: float


class ModelStatus(BaseModel):
    """Status metadata for an individual local ML model."""

    name: str
    status: str
    type: str
    accuracy: float | None = None
    loss: float | None = None
    samples: int | None = None
    classes: int | None = None


class ModelsHealthResponse(BaseModel):
    """Overall local model registry health and execution mode."""

    status: str
    engine_mode: str
    models: list[ModelStatus]
