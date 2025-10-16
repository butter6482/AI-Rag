# -*- coding: utf-8 -*-
import os, requests, streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8080")

st.set_page_config(page_title="AI RAG Assistant", page_icon=None, layout="centered")

st.title("AI RAG Assistant")
st.caption("Ask a question. The system will search the web and answer concisely, citing sources.")

question = st.text_input("Your question", placeholder="Who won Best Picture in 2024?")
ask = st.button("Ask", type="primary", use_container_width=False)

if ask:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching the web and generating an answer..."):
            try:
                payload = {"query": question}
                r = requests.post(f"{API_URL}/preguntar", json=payload, timeout=120)
                if r.status_code == 200:
                    data = r.json()
                    st.subheader("Answer")
                    st.write(data.get("respuesta", "(no answer)"))

                    src = data.get("sources") or []
                    if src:
                        with st.expander("Sources"):
                            for item in src:
                                title = item.get("title", "").strip() or "(untitled)"
                                url = item.get("url", "").strip()
                                if url:
                                    st.markdown(f"- [{title}]({url})")
                                else:
                                    st.markdown(f"- {title}")
                else:
                    st.error(f"Backend error {r.status_code}")
                    try:
                        st.code(r.json())
                    except Exception:
                        st.code(r.text)
            except Exception as e:
                st.error(f"Network error: {e}")