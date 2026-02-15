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

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt \
    && pip install --no-cache-dir psycopg2-binary boto3 alembic

COPY backend/ /app/backend/

# Put built frontend into backend/static
RUN rm -rf /app/backend/static
COPY --from=frontend /app/frontend/dist /app/backend/static

EXPOSE 8000
CMD ["python","-m","uvicorn","app.saas_main:app","--host","0.0.0.0","--port","8000"]
