#!/bin/bash

# Start backend in background
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0

# Kill backend when frontend stops
kill $BACKEND_PID
