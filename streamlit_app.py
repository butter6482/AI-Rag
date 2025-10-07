import streamlit as st
from app.rag_utils import buscar_web, generar_respuesta


st.set_page_config(page_title="AI-RAG Demo", page_icon="🧠", layout="centered")
st.title("🧠 AI-RAG Demo")
st.caption("Busca en la web y genera respuestas con contexto")

with st.sidebar:
    st.subheader("Opciones")
    max_results = st.slider("Resultados web", 1, 10, 3)
    show_context = st.checkbox("Mostrar contexto", value=False)

query = st.text_input("Pregunta", placeholder="¿Qué es el aprendizaje por refuerzo?")

col1, col2 = st.columns([1, 1])
with col1:
    go = st.button("Preguntar", type="primary")
with col2:
    clear = st.button("Limpiar")

if clear:
    st.rerun()

if go:
    if not query.strip():
        st.warning("Escribe una pregunta antes de continuar.")
    else:
        try:
            with st.spinner("Buscando en la web..."):
                contexto = buscar_web(query, max_results=max_results)

            if show_context:
                with st.expander("Contexto web"):
                    st.write(contexto if contexto else "(Sin resultados)")

            with st.spinner("Generando respuesta..."):
                respuesta = generar_respuesta(query, contexto)

            st.success("Respuesta")
            st.write(respuesta)
        except Exception as e:
            st.error(f"Error: {e}")

