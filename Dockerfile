# ============================================================
# Dockerfile — Stratégie & Expertise Santé
# Build multi-stage : Backend (FastAPI) + Frontend (React)
# ============================================================

# --- Stage 1 : Build Frontend ---
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/yarn.lock* ./
RUN yarn install --frozen-lockfile --production=false
COPY frontend/ .
RUN yarn build

# --- Stage 2 : Backend + Serve Frontend ---
FROM python:3.11-slim

# Dépendances système pour OCR (Tesseract) et PDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-fra \
    poppler-utils \
    libmagic1 \
    fonts-liberation \
    nginx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Backend source
COPY backend/ ./backend/

# Frontend build from stage 1
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Nginx config to serve frontend + proxy API
COPY nginx.conf /etc/nginx/nginx.conf

# Startup script
COPY start.sh ./
RUN chmod +x start.sh

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8001/api/health || exit 1

CMD ["./start.sh"]
