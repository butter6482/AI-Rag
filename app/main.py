from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.rag_utils import buscar_web, generar_respuesta

app = FastAPI()


class Pregunta(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/preguntar")
def preguntar(data: Pregunta):
    try:
        contexto = buscar_web(data.query)
        respuesta = generar_respuesta(data.query, contexto)
        return {"respuesta": respuesta}
    except Exception as e:
        # Surface a concise error while hiding internals
        raise HTTPException(status_code=500, detail=f"Error generando respuesta: {e}")
