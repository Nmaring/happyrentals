# ---- build frontend ----
FROM node:20 AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- backend runtime ----
FROM python:3.11-slim
WORKDIR /app

# System deps (psycopg2 needs libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && rm -rf /var/lib/apt/lists/*

# Install backend deps
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt \
    && pip install --no-cache-dir psycopg2-binary boto3 alembic

# Copy backend code
COPY backend/ /app/backend/

# Copy built frontend into backend static
RUN rm -rf /app/backend/static
COPY --from=frontend /app/frontend/dist /app/backend/static

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Run SaaS app
CMD ["python","-m","uvicorn","app.saas_main:app","--host","0.0.0.0","--port","8000"]
