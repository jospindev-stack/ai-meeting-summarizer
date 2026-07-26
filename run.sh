#!/bin/bash
set -e

if [ ! -f .env ]; then
    echo "[ERROR] .env not found. Copy .env.example to .env and fill in GROQ_API_KEY."
    exit 1
fi

echo "[1/2] Starting FastAPI backend on http://localhost:8000 ..."
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 2

echo "[2/2] Starting Streamlit frontend on http://localhost:8501 ..."
streamlit run frontend/app.py --server.port 8501 --server.maxUploadSize 25 &
FRONTEND_PID=$!

echo ""
echo "Services running:"
echo "  Backend  : http://localhost:8000  (Swagger: http://localhost:8000/docs)"
echo "  Frontend : http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait
