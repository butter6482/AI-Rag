# Ejemplo de uso con CURL

## Prueba del endpoint `/preguntar`

```bash
curl -X POST http://127.0.0.1:8000/preguntar \
  -H "Content-Type: application/json" \
  -d '{"query":"Diferencias entre GPT-4 y Claude 3"}'
```

## Ejemplo de respuesta esperada:

```json
{
  "contexto": "[1] Comparación entre Claude 3 y GPT-4 · LobeHub\nMar 6, 2024 · Este artículo te proporciona una comparación detallada entre Claude3 y GPT-4...",
  "respuesta": "Basado en las fuentes proporcionadas:\n\nClaude 3 y GPT-4 son dos de los modelos de IA más avanzados [1][2]. Las principales diferencias incluyen:\n\n- **Capacidades multimodales**: Ambos pueden procesar texto e imágenes [1]\n- **Ventana de contexto**: Claude 3 ofrece una ventana de contexto más amplia [1]\n- **Rendimiento**: Según las evaluaciones, ambos tienen fortalezas en diferentes áreas [2]\n- **Casos de uso**: GPT-4 es más versátil mientras que Claude 3 destaca en razonamiento y análisis [3]\n\nFuentes:\n[1] https://lobehub.com/es/blog/claude-3-vs-gpt-4\n[2] https://textcortex.com/es/post/claude-3-vs-gpt-4\n[3] https://tactiq.io/es/aprende/comparacion-chatgpt-vs-claude",
  "sources": [
    {
      "title": "Comparación entre Claude 3 y GPT-4 · LobeHub",
      "url": "https://lobehub.com/es/blog/claude-3-vs-gpt-4"
    },
    {
      "title": "Claude 3 de Anthropic vs GPT 4 - ¿Qué modelo es mejor?",
      "url": "https://textcortex.com/es/post/claude-3-vs-gpt-4"
    },
    {
      "title": "ChatGPT vs Claude: principales diferencias y ventajas",
      "url": "https://tactiq.io/es/aprende/comparacion-chatgpt-vs-claude"
    }
  ],
  "status": "success"
}
```

## Verificación de búsqueda web real

Como puedes ver en la respuesta:
- ✅ Las fuentes tienen **URLs reales** (no example.com)
- ✅ Los títulos son **específicos y relevantes**
- ✅ El contenido incluye **snippets reales** de las páginas web
- ✅ La respuesta incluye **citas [1], [2], [3]** que referencian las fuentes

## Prueba con otra consulta

```bash
curl -X POST http://127.0.0.1:8000/preguntar \
  -H "Content-Type: application/json" \
  -d '{"query":"What is RAG in AI?"}'
```

Esto devolverá fuentes en inglés con URLs reales y contenido actualizado de la web.

