#!/bin/bash

# Start backend in background
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend on the port Render expects
streamlit run streamlit_app.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true

# Kill backend when frontend stops
kill $BACKEND_PID
