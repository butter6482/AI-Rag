import os
from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
from ddgs import DDGS
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Cargar variables del entorno
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

class Pregunta(BaseModel):
    query: str

# Buscar información en la web
def buscar_web(pregunta: str) -> str:
    with DDGS() as ddgs:
        results = ddgs.text(pregunta, max_results=3)
        textos = []
        for r in results:
            soup = BeautifulSoup(r.get("body", ""), "html.parser")
            textos.append(soup.get_text())
        return "\n\n".join(textos)

# Endpoint de la API
@app.post("/preguntar")
def preguntar(data: Pregunta):
    contexto = buscar_web(data.query)

    completion = client.chat.completions.create(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    messages=[
        {"role": "system", "content": "Eres un asistente experto que responde usando la información del contexto web si es útil."},
       {"role": "user", "content": f"{data.query}\n\nBasándote únicamente en la siguiente información encontrada en la web, responde con precisión y sin usar conocimientos previos:\n{contexto}"}

    ]
)

    return {"respuesta": completion.choices[0].message.content}
