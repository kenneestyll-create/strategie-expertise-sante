#!/bin/bash
# ============================================================
# Startup script — Stratégie & Expertise Santé
# Lance le backend FastAPI + Nginx (frontend + reverse proxy)
# ============================================================

echo "Starting backend (FastAPI)..."
cd /app/backend
uvicorn server:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!

echo "Starting Nginx (frontend + proxy)..."
nginx -g "daemon off;" &
NGINX_PID=$!

echo "Backend PID: $BACKEND_PID | Nginx PID: $NGINX_PID"
echo "Application ready on port 80"

# Wait for either process to exit
wait -n $BACKEND_PID $NGINX_PID
EXIT_CODE=$?
echo "Process exited with code $EXIT_CODE"
kill $BACKEND_PID $NGINX_PID 2>/dev/null
exit $EXIT_CODE
