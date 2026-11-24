FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:0.13 /uv /bin/uv

# venv вне /app: в compose поверх /app монтируются исходники
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --locked --no-dev --no-cache

COPY backend/ ./

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
