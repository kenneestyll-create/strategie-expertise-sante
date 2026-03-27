#!/bin/bash
# Install OCR dependencies if missing
if ! command -v tesseract &> /dev/null; then
    apt-get update -qq && apt-get install -y -qq tesseract-ocr tesseract-ocr-fra poppler-utils 2>/dev/null
fi
exec /root/.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1 --reload
