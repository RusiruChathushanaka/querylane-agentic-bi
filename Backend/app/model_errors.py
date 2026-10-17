"""Public model failures and one bounded retry policy, never a tool replay policy."""

import random

import httpx
from google.genai.errors import APIError

from app.errors import AppError

TRANSIENT_MODEL_CODES = frozenset({"model_timeout", "model_transient", "model_rate_limited"})
PERMANENT_MODEL_CODES = frozenset({"model_unavailable", "model_error"})


def model_failure(error, selected_model=None):
    if isinstance(error, AppError):
        return error
    if isinstance(error, (TimeoutError, httpx.TimeoutException)):
        return AppError("The model timed out. Try a more focused question.", 504, "model_timeout")
    if isinstance(error, (httpx.NetworkError, httpx.RemoteProtocolError, ConnectionError)):
        return AppError("The model connection was interrupted. Try again shortly.", 503, "model_transient")
    # The installed GenAI async transport may use aiohttp instead of httpx.
    try:
        from aiohttp import ClientConnectionError

        if isinstance(error, ClientConnectionError):
            return AppError(
                "The model connection was interrupted. Try again shortly.", 503, "model_transient"
            )
    except ImportError:
        pass
    code = error.code if isinstance(error, APIError) else error
    if not isinstance(code, (str, int)):
        return None
    code = str(code).upper()
    if code in {"401", "403", "404", "UNAUTHENTICATED", "PERMISSION_DENIED", "NOT_FOUND"}:
        message = (
            f"The selected analysis model ({selected_model}) is unavailable in this project or location. Choose another model in Settings or check model access."
            if selected_model
            else "The live voice model is unavailable in this project or location. Use text chat or the manual skill editor; check model access before reconnecting."
        )
        return AppError(message, 502, "model_unavailable")
    if code in {"429", "RESOURCE_EXHAUSTED"}:
        return AppError(
            "The model is busy or its quota is exhausted. Try again later.", 503, "model_rate_limited"
        )
    if code in {
        "408",
        "499",
        "500",
        "502",
        "503",
        "504",
        "CANCELLED",
        "INTERNAL",
        "UNAVAILABLE",
        "DEADLINE_EXCEEDED",
    }:
        return AppError("The model is temporarily unavailable. Try again shortly.", 503, "model_transient")
    return AppError("The model could not complete this request. Try a narrower question.", 502, "model_error")


def model_retry_delay(error):
    """Respect a short Retry-After; don't retry earlier than a long provider delay."""
    response = getattr(error, "response", None)
    value = getattr(response, "headers", {}).get("Retry-After") if response is not None else None
    if value is not None:
        try:
            delay = float(value)
        except (TypeError, ValueError):
            return None
        return delay if 0 <= delay <= 5 else None
    return random.uniform(1, 2)
