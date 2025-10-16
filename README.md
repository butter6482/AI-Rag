# AI RAG Assistant

A minimal RAG demo using FastAPI + Streamlit + DuckDuckGo Search + OpenRouter (Gemma 2 9B).

## Quick Start with Docker

### Using Docker Compose (Recommended)

```bash
# Set environment variables
export OPENROUTER_API_KEY=sk-or-your-key-here

# Start both services
docker compose up --build

# Backend: http://localhost:8080
# Frontend: http://localhost:8501
```

### Using Docker directly

```bash
# Build image
docker build -t ai-rag .

# Run backend
docker run --rm -p 8080:8080 \
  -e OPENROUTER_API_KEY=sk-or-your-key-here \
  ai-rag

# Run frontend (in another terminal)
docker run --rm -p 8501:8501 \
  -e API_URL=http://host.docker.internal:8080 \
  ai-rag streamlit run /app/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
```

## Local Development

1) Install dependencies:
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

2) Set environment variables:
```bash
export OPENROUTER_API_KEY=sk-or-your-key-here
export OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
export LLM_MODEL=google/gemma-2-9b-it
export API_URL=http://127.0.0.1:8080
```

3) Start backend:
```bash
python -m uvicorn app.main:app --reload --port 8080
```

4) Start frontend:
```bash
streamlit run streamlit_app.py
```

## Testing

```bash
# Run tests (no network required)
pytest -q
```

## Features

- Automatic language detection (Spanish/English)
- Web search with source citations
- Single model: google/gemma-2-9b-it via OpenRouter
- Minimal English-only UI
- Production-ready Docker setup
