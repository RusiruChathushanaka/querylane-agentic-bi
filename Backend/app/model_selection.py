"""Pinned text model choices; per-analysis context never mutates shared settings."""

from contextvars import ContextVar

from app.errors import AppError

TEXT_MODELS = (
    {
        "id": "gemini-3.8-flash",
        "name": "Gemini 3.8 Flash",
        "description": "For complex questions and cross-source analysis.",
    },
    {
        "id": "gemini-3.5-flash-lite",
        "name": "Gemini 3.5 Flash-Lite",
        "description": "For quick, lightweight questions with lower model cost.",
    },
)
active_text_model: ContextVar[str | None] = ContextVar("active_text_model", default=None)


def resolve_text_model(settings, requested: str | None = None) -> str:
    if requested is None:
        return settings.text_model
    if requested not in {model["id"] for model in TEXT_MODELS}:
        raise AppError("Choose a supported analysis model in Settings.", 400, "unsupported_model")
    return requested


def model_evidence(settings) -> dict:
    selected = active_text_model.get() or settings.text_model
    return {
        "backend": settings.ai_backend,
        "text_model": selected if settings.ai_backend == "gemini" else None,
        "selected_text_model": selected,
    }
