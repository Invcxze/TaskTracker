FROM python:3.12-slim
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /app
COPY backend/pyproject.toml backend/uv.lock ./
RUN pip install uv && \
    uv sync --active

COPY backend .

ENV DJANGO_SETTINGS_MODULE=config.settings.base

CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000"]