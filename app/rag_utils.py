# -*- coding: utf-8 -*-
import os, json, requests
from typing import List, Dict, Tuple
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = (os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1") or "").rstrip("/")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "google/gemma-2-9b-it")

if not OPENROUTER_API_KEY:
    # Allow running without API key for testing
    if os.getenv("PYTEST_CURRENT_TEST"):
        OPENROUTER_API_KEY = "test-key-for-pytest"
    else:
        raise RuntimeError("OPENROUTER_API_KEY is required")

VALID_MODELS = {"google/gemma-2-9b-it"}

def _resolve_model(model: str | None) -> str:
    """Return a safe model id. Never return 'string'."""
    m = (model or DEFAULT_MODEL or "").strip()
    if not m or m.lower() == "string" or m not in VALID_MODELS:
        return "google/gemma-2-9b-it"
    return m

def _truncate(text: str, max_chars: int) -> str:
    return text if len(text) <= max_chars else text[:max_chars]

def _detect_lang(text: str) -> str:
    """Simple language detection based on common Spanish words and characters"""
    text_lower = text.lower().strip()
    
    # Spanish indicators
    spanish_indicators = [
        '¿', 'á', 'é', 'í', 'ó', 'ú', 'ñ', 'ü',
        'que', 'qué', 'como', 'cómo', 'donde', 'dónde',
        'cuando', 'cuándo', 'porque', 'por qué', 'para',
        'con', 'sin', 'sobre', 'entre', 'durante',
        'español', 'españa', 'mexico', 'argentina'
    ]
    
    # Count Spanish indicators
    spanish_count = sum(1 for indicator in spanish_indicators if indicator in text_lower)
    
    # If we find Spanish indicators, likely Spanish
    if spanish_count > 0:
        return "es"
    
    # Default to English
    return "en"

def _search_web(query: str, max_results: int) -> Tuple[str, List[Dict[str, str]]]:
    """
    Return (context_text, sources). Sources is a list of {title, url}.
    We extract the snippet body and keep titles/urls for citation.
    """
    textos: List[str] = []
    sources: List[Dict[str, str]] = []

    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                title = (r.get("title") or "").strip()
                url = (r.get("href") or "").strip()
                body_html = r.get("body") or ""
                
                # Skip if body contains JavaScript or is empty
                if not body_html or "javascript" in body_html.lower() or "d.js" in body_html:
                    continue
                    
                snippet = BeautifulSoup(body_html, "html.parser").get_text().strip()
                
                # Only add if we have meaningful content
                if snippet and len(snippet) > 10:
                    textos.append(snippet)
                    
                if title and url and not url.startswith("javascript:"):
                    sources.append({"title": title, "url": url})
                    
    except Exception as e:
        print(f"Search error: {e}")
        # Return empty results instead of crashing
        pass

    context_text = _truncate("\n\n".join(textos), 7500)
    return context_text, sources

def buscar_web(query: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Adaptive search: start with 6 results; if short, fetch up to 10.
    """
    ctx, src = _search_web(query, max_results=6)
    if len(ctx) < 800:
        more_ctx, more_src = _search_web(query, max_results=10)
        # override only if better
        if len(more_ctx) > len(ctx):
            ctx, src = more_ctx, more_src
    if not ctx:
        ctx = "No relevant results were found on the web."
    return ctx, src

def generar_respuesta(query: str, contexto: str, lang_hint: str | None = None, model: str | None = None) -> str:
    """
    Generate an answer using OpenRouter chat/completions.
    Answer in Spanish if the question is Spanish; English otherwise.
    """
    model_id = _resolve_model(model)
    lang = lang_hint or _detect_lang(query)

    if lang == "es":
        system = (
            "Eres un asistente que responde en español. Usa el contexto web dado cuando sea útil. "
            "Si el contexto contiene ruido, ignóralo. Responde de manera breve y clara. "
            "Si afirmas un dato (por ejemplo, ganadores de premios), da el nombre exacto y el año."
        )
        user = (
            f"Pregunta: {query}\n\n"
            f"Contexto web (puede contener ruido):\n{_truncate(contexto, 6000)}\n\n"
            f"Responde en español y, si corresponde, cita brevemente las fuentes proporcionadas."
        )
    else:
        system = (
            "You are an assistant that answers in English. Use the provided web context when helpful. "
            "If the context contains noise, ignore it. Answer briefly and clearly. "
            "If stating a fact (e.g., award winners), provide the exact name and year."
        )
        user = (
            f"Question: {query}\n\n"
            f"Web context (may include noise):\n{_truncate(contexto, 6000)}\n\n"
            f"Answer in English and, where appropriate, briefly cite the provided sources."
        )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8080",
        "X-Title": "AI-RAG Assistant",
    }
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.3,
        "max_tokens": 800,
    }

    try:
        resp = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            try:
                err = resp.json()
            except Exception:
                err = {"raw": resp.text}
            return f"OpenRouter error ({resp.status_code}): {json.dumps(err, ensure_ascii=False)}"
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Generation error: {e}"

def buscar_web_y_generar(query: str, model: str | None = None):
    try:
        contexto, sources = buscar_web(query)
        lang = _detect_lang(query)
        answer = generar_respuesta(query, contexto, lang_hint=lang, model=model)
        return {"contexto": contexto, "respuesta": answer, "sources": sources}
    except Exception as e:
        # Return a safe fallback response
        return {
            "contexto": "No se pudo obtener contexto web debido a un error técnico.",
            "respuesta": f"Lo siento, hubo un error procesando tu pregunta: {str(e)}. Por favor intenta con una pregunta diferente.",
            "sources": []
        }