#!/usr/bin/env bash
# Startup script for Mastercard AI Defense Lab (Backend + Frontend)

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "================================================================="
echo "  MASTERCARD AI DEFENSE LAB - PAYMENT SECURITY (GFF 2026)"
echo "================================================================="

# Check virtual environment
if [ -d ".venv" ]; then
    echo " Activating Python virtual environment (.venv)..."
    source .venv/bin/activate
else
    echo "❌ Python virtual environment (.venv) not found. Please run:"
    echo "   python3.11 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

echo " Starting FastAPI Backend on http://127.0.0.1:8000 ..."
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo " Starting Next.js Web Dashboard on http://localhost:3000 ..."
cd "$PROJECT_ROOT/web"
npm run dev &
FRONTEND_PID=$!

trap "echo ' Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT TERM EXIT

echo ""
echo "🚀 SYSTEM ACTIVE:"
echo "   - Web Dashboard:     http://localhost:3000"
echo "   - Backend API Docs:  http://127.0.0.1:8000/docs"
echo "   - WebSocket Stream:  ws://127.0.0.1:8000/ws/transactions"
echo ""
echo "Press Ctrl+C to stop all services."

wait
