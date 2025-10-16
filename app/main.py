# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn, traceback

from app.rag_utils import buscar_web_y_generar

app = FastAPI(title="AI-RAG API", description="Web search + OpenRouter (Gemma 2 9B)", version="2.0.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

class Pregunta(BaseModel):
    query: str
    model: Optional[str] = None  # unused by UI, but allowed

class Respuesta(BaseModel):
    contexto: str
    respuesta: str
    sources: List[Dict[str, str]]
    status: str = "success"

@app.get("/")
def root():
    return {"message": "AI-RAG API OK"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/preguntar", response_model=Respuesta)
def preguntar(p: Pregunta):
    try:
        if not p.query or not p.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        data = buscar_web_y_generar(query=p.query.strip(), model=p.model)
        return Respuesta(**data)
    except HTTPException:
        raise
    except Exception as e:
        detail = f"Processing error: {e}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=detail)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)