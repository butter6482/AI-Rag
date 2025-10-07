import os
from ddgs import DDGS
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


# Prefer OPENROUTER_API_KEY, fall back to OPENAI_API_KEY
_api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
if not _api_key:
    raise RuntimeError(
        "Missing API key. Set OPENROUTER_API_KEY (preferred) or OPENAI_API_KEY in your environment or .env file."
    )

_base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
client = OpenAI(base_url=_base_url, api_key=_api_key)


def _truncate(text: str, max_chars: int = 8000) -> str:
    return text if len(text) <= max_chars else text[:max_chars]


def buscar_web(query: str, max_results=3) -> str:
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=max_results)
        textos = []
        for r in results:
            soup = BeautifulSoup(r.get("body", ""), "html.parser")
            textos.append(soup.get_text())
        return _truncate("\n\n".join(textos))

def generar_respuesta(query: str, contexto: str) -> str:
    completion = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers using web context if relevant."},
            {"role": "user", "content": f"Question: {query}\n\nUse the following web context to answer accurately:\n{contexto}"}
        ]
    )
    return completion.choices[0].message.content
