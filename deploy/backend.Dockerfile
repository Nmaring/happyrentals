# Backend image
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend/ /app/

EXPOSE 8000

# Persist sqlite db in /data and symlink to /app/saas.db (matches your current code)
CMD ["sh","-c","mkdir -p /data && ln -sf /data/saas.db /app/saas.db && uvicorn app.saas_main:app --host 0.0.0.0 --port 8000"]
