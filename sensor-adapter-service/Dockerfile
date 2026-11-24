FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:0.13 /uv /bin/uv

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/code

WORKDIR /code

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-cache

COPY . .

CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host ${APP_HOST} --port ${APP_PORT} --reload"]
