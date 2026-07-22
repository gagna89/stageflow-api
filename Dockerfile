# ---- Stage 1 : Build des dépendances ----
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --target=/packages -r requirements.txt

# ---- Stage 2 : Image de production (légère) ----
FROM python:3.11-slim AS production

# Sécurité : utilisateur non-root (exigé par le sujet)
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Copier les dépendances compilées
COPY --from=builder /packages /usr/local/lib/python3.11/site-packages

# IMPORTANT : rendre les scripts (uvicorn, alembic...) exécutables et trouvables
ENV PATH="/usr/local/lib/python3.11/site-packages/bin:$PATH"
ENV PYTHONPATH="/usr/local/lib/python3.11/site-packages:$PYTHONPATH"

# Copier le code de l'application
COPY --chown=appuser:appgroup app/ ./app/
COPY --chown=appuser:appgroup alembic/ ./alembic/
COPY --chown=appuser:appgroup alembic.ini .

USER appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

EXPOSE $PORT

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT"]