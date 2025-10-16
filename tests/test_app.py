# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from unittest.mock import patch

def test_health():
    from app.main import app
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"

@patch('app.main.buscar_web_y_generar')
def test_preguntar_ok(mock_bwyg):
    # Mock the function to return fake data
    mock_bwyg.return_value = {
        "contexto": "fake context",
        "respuesta": "Fake answer",
        "sources": [{"title": "Example", "url": "https://example.com"}],
    }
    
    from app.main import app
    client = TestClient(app)

    r = client.post("/preguntar", json={"query": "test question"})
    assert r.status_code == 200
    data = r.json()
    assert "respuesta" in data and data["respuesta"] == "Fake answer"
    assert isinstance(data.get("sources"), list) and data["sources"]
