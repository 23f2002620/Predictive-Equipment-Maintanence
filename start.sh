set -e

echo "🏥 MediWatch — Predictive Equipment Maintenance"
echo "================================================"

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "▶ Starting FastAPI backend on :8000 ..."
cd "$ROOT_DIR/backend"
pip install -r requirements.txt -q
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID"

echo ""
echo "▶ Starting Vue frontend on :5173 ..."
cd "$ROOT_DIR/frontend"
npm install --silent
npm run dev &
FRONTEND_PID=$!
echo "  Frontend PID: $FRONTEND_PID"

echo ""
echo "Both servers running."
echo "   Frontend (dev):  http://localhost:5173"
echo "   Backend (API):   http://localhost:8000"
echo "   API docs:        http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" EXIT
wait
