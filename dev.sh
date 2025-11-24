#!/bin/bash

# Start both backend and frontend for development

echo "Starting SkinIntel development servers..."

# Start backend
echo "Starting backend on http://localhost:8000"
python main.py &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend on http://localhost:5173"
cd client && npm run dev &
FRONTEND_PID=$!

# Handle shutdown
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM

echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

wait
