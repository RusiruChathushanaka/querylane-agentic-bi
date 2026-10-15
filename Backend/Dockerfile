FROM python:3.12-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.12-slim
RUN useradd --create-home --uid 10001 appuser
WORKDIR /app
COPY --from=build --chown=appuser:appuser /app/.venv /app/.venv
COPY --chown=appuser:appuser app ./app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
USER appuser
EXPOSE 8080
CMD ["python", "-m", "app.serve"]
