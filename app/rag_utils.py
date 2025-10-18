# -*- coding: utf-8 -*-
import os, json, requests, logging
from typing import List, Dict, Tuple
from ddgs import DDGS
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def search_web(query: str, max_results: int = 5) -> List[Dict]:
    """
    Real web search using ddgs library
    """
    results = []
    try:
        logger.info(f"Searching web for: {query}")
        with DDGS() as ddgs:
            # text() devuelve generador; conviértelo a lista
            for r in ddgs.text(query, max_results=max_results):
                # r típicamente tiene 'title', 'href', 'body'
                title = r.get("title") or ""
                href = r.get("href") or ""
                body = r.get("body") or ""
                if href and (title or body):
                    results.append({"title": title, "href": href, "body": body})
        
        logger.info(f"Found {len(results)} search results")
        if results:
            logger.info(f"First result URL: {results[0]['href']}")
        return results
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return []

def build_prompt(query: str, search_results: List[Dict]) -> str:
    """
    Build RAG prompt with real search results
    """
    bullets = []
    for i, r in enumerate(search_results, start=1):
        bullets.append(f"[{i}] {r['title']}\n{r['body']}\nURL: {r['href']}")
    sources_block = "\n\n".join(bullets) if bullets else "No sources found."
    return (
        "Answer concisely using ONLY the sources below. Cite like [1], [2] and include URLs.\n\n"
        f"SOURCES:\n{sources_block}\n\n"
        f"QUESTION: {query}\n"
        "ANSWER:"
    )

def _search_web(query: str, max_results: int) -> Tuple[str, List[Dict[str, str]]]:
    """
    Web search that returns context and sources
    """
    logger.info(f"[RAG] Searching for: {query}")
    search_results = search_web(query, max_results)
    
    if not search_results:
        logger.warning("No search results found")
        return "", []
    
    # Build context from search results
    context_parts = []
    sources = []
    
    for i, result in enumerate(search_results, 1):
        context_parts.append(f"[{i}] {result['title']}\n{result['body']}")
        sources.append({
            "title": result['title'],
            "url": result['href']
        })
    
    context = "\n\n".join(context_parts)
    logger.info(f"[RAG] Generated context with {len(sources)} sources, length: {len(context)}")
    return context, sources

def buscar_web(query: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Web search with real results
    """
    ctx, src = _search_web(query, max_results=5)
    return ctx, src

def generar_respuesta_directa(query: str, system: str, user: str, model: str | None = None) -> str:
    """
    Generate an answer directly without web context.
    """
    model_id = _resolve_model(model)
    
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
        logger.info(f"[RAG] Searching for: {query}")
        contexto, sources = buscar_web(query)
        logger.info(f"[RAG] Found {len(sources)} sources, context length: {len(contexto)}")
        
        lang = _detect_lang(query)
        logger.info(f"[RAG] Detected language: {lang}")
        
        # If no web context found, generate answer without web search
        if not contexto or len(contexto.strip()) < 20:
            logger.warning(f"[RAG] No web context found, generating answer without web search")
            if lang == "es":
                system = (
                    "Eres un asistente útil que responde en español. "
                    "Responde de manera clara y concisa basándote en tu conocimiento. "
                    "Si no tienes información actualizada, menciona que la información puede haber cambiado."
                )
                user = f"Pregunta: {query}\n\nResponde en español de manera útil y clara."
            else:
                system = (
                    "You are a helpful assistant that answers in English. "
                    "Respond clearly and concisely based on your knowledge. "
                    "If you don't have current information, mention that information may have changed."
                )
                user = f"Question: {query}\n\nAnswer in English in a helpful and clear way."
            
            # Generate answer without web context
            answer = generar_respuesta_directa(query, system, user, model)
            return {
                "contexto": "No se pudo obtener contexto web actualizado.",
                "respuesta": answer,
                "sources": []
            }
        
        answer = generar_respuesta(query, contexto, lang_hint=lang, model=model)
        return {"contexto": contexto, "respuesta": answer, "sources": sources}
    except Exception as e:
        logger.error(f"[RAG] Error: {e}")
        # Return a safe fallback response
        return {
            "contexto": "No se pudo obtener contexto web debido a un error técnico.",
            "respuesta": f"Lo siento, hubo un error procesando tu pregunta: {str(e)}. Por favor intenta con una pregunta diferente.",
            "sources": []
        }