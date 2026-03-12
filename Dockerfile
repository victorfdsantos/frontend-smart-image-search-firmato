# =============================================================================
# Build stage — instala dependências Python e Node
# =============================================================================
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt


# =============================================================================
# Runtime stage
# =============================================================================
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FRONTEND_PORT=3000 \
    BACKEND_PORT=8001 \
    API_BASE=http://api:8000 \
    REFLEX_DIR=/app/.reflex \
    HOME=/app

WORKDIR /app

# Node.js + unzip (exigido pelo Reflex para descompactar dependências Node)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copia pacotes Python instalados no build stage
COPY --from=builder /install /usr/local

# Copia o código-fonte do app
COPY app/ ./app/

# assets/ fica na raiz do projeto (logo, favicon, etc.)
# Se não tiver essa pasta, remova esta linha
COPY assets/ ./assets/

COPY rxconfig.py ./

RUN useradd --no-create-home --shell /bin/false --home-dir /app appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 3000 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

CMD ["reflex", "run", \
     "--env", "prod", \
     "--frontend-port", "3000", \
     "--backend-port", "8001", \
     "--loglevel", "info"]