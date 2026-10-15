"""Local-only Gemini preview on synthetic fixtures, using the operator's gcloud identity.

Run: python -m uvicorn app.cloud_preview:app --host 127.0.0.1 --port 8000
Credentials remain in memory and expire; restart after the operator token expires.
"""

from app.admin import operator_credentials
from app.config import Settings
from app.main import create_app

app = create_app(
    Settings(environment="local", ai_backend="gemini", data_backend="fixture", storage_backend="memory"),
    credentials=operator_credentials(),
)
