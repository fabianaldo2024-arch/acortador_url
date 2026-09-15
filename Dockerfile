# Etapa 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Variables de entorno para asegurar que Poetry no cree entornos virtuales y evite interactividad
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==1.8.2

COPY pyproject.toml ./

# Instalación directa de dependencias principales desde pyproject.toml
RUN poetry install --no-root --only main

# Etapa 2: Runner
FROM python:3.12-slim AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

# Copiar bibliotecas de Python instaladas desde la etapa builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
