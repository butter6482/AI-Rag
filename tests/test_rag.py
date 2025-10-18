import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Set test environment
os.environ["PYTEST_CURRENT_TEST"] = "true"
os.environ["OPENROUTER_API_KEY"] = "test-key-for-pytest"

from app.main import app

client = TestClient(app)

def test_preguntar_includes_sources(monkeypatch):
    """Test that the /preguntar endpoint returns real sources with URLs"""
    
    def fake_search_web(query: str, max_results: int = 5):
        """Mock search_web to return controlled results"""
        return [
            {
                "title": "Documentación oficial de RAG", 
                "href": "https://docs.example.com/rag", 
                "body": "RAG (Retrieval-Augmented Generation) es una técnica que combina búsqueda de información con generación de texto."
            },
            {
                "title": "Guía completa de RAG en español", 
                "href": "https://tutorial.example.com/rag-guide", 
                "body": "RAG permite a los modelos de IA acceder a información actualizada mediante búsqueda web."
            },
            {
                "title": "Implementación práctica de RAG", 
                "href": "https://github.com/example/rag-implementation", 
                "body": "Ejemplos de código para implementar RAG con diferentes modelos de lenguaje."
            }
        ]
    
    def fake_generar_respuesta(query: str, contexto: str, lang_hint: str = None, model: str = None):
        """Mock generar_respuesta to return a controlled response"""
        return "RAG es una técnica que combina búsqueda de información con generación de texto. [1] [2] [3]"
    
    # Mock the search_web function
    from app import rag_utils
    monkeypatch.setattr(rag_utils, "search_web", fake_search_web)
    monkeypatch.setattr(rag_utils, "generar_respuesta", fake_generar_respuesta)
    
    # Test the endpoint
    resp = client.post("/preguntar", json={"query": "¿Qué es RAG?"})
    assert resp.status_code == 200
    
    data = resp.json()
    assert "sources" in data
    assert len(data["sources"]) >= 2
    assert data["sources"][0]["url"].startswith("http")
    assert "title" in data["sources"][0]
    assert "url" in data["sources"][0]
    
    # Verify sources have real URLs
    for source in data["sources"]:
        assert source["url"].startswith("http")
        assert len(source["title"]) > 0

def test_build_prompt_includes_sources():
    """Test that build_prompt correctly formats search results"""
    from app.rag_utils import build_prompt
    
    search_results = [
        {
            "title": "Test Document 1",
            "href": "https://example.com/doc1",
            "body": "This is the content of document 1"
        },
        {
            "title": "Test Document 2", 
            "href": "https://example.com/doc2",
            "body": "This is the content of document 2"
        }
    ]
    
    query = "What is testing?"
    prompt = build_prompt(query, search_results)
    
    assert "[1]" in prompt
    assert "[2]" in prompt
    assert "https://example.com/doc1" in prompt
    assert "https://example.com/doc2" in prompt
    assert "Test Document 1" in prompt
    assert "Test Document 2" in prompt
    assert "What is testing?" in prompt

def test_search_web_returns_real_results():
    """Test that search_web returns real search results"""
    from app.rag_utils import search_web
    
    # This test will make a real web search
    results = search_web("artificial intelligence", max_results=3)
    
    assert isinstance(results, list)
    if results:  # Only test if we got results
        for result in results:
            assert "title" in result
            assert "href" in result
            assert "body" in result
            assert result["href"].startswith("http")

def test_health_endpoint():
    """Test that health endpoint works"""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

def test_root_endpoint():
    """Test that root endpoint works"""
    resp = client.get("/")
    assert resp.status_code == 200
    assert "message" in resp.json()

def test_preguntar_empty_query():
    """Test that empty query returns error"""
    resp = client.post("/preguntar", json={"query": ""})
    assert resp.status_code == 400

def test_preguntar_missing_query():
    """Test that missing query field returns error"""
    resp = client.post("/preguntar", json={})
    assert resp.status_code == 422  # Validation error
