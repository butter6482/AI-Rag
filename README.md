# 🧠 AI-RAG (Retrieval-Augmented Generation Assistant)

AI-RAG is a web-based AI assistant that combines **real-time web search** with **LLM reasoning**.  
It uses **FastAPI** for the backend, **OpenRouter API** for responses, and **DuckDuckGo Search (DDGS)** to retrieve up-to-date information from the web.  
An optional **Streamlit app** provides a simple user interface.

---

## 🚀 Main Features

- 🔍 **Web-augmented answers** using RAG (Retrieval-Augmented Generation).  
- ⚡ **FastAPI backend** — lightweight and easy to deploy.  
- 🤖 **OpenRouter LLM** for AI responses (Llama 3, Mistral, etc).  
- 💬 **Optional Streamlit front-end** for testing locally.  
- 🔒 **Secure configuration** with `.env` file for API keys.

---

## 🧰 Tech Stack

- **Backend:** FastAPI  
- **AI Model:** OpenRouter API  
- **Web Search:** DuckDuckGo Search (ddgs)  
- **Frontend (optional):** Streamlit  
- **Environment:** Python 3.10+  
- **Parsing:** BeautifulSoup  

---

## ⚙️ Quick Setup

```bash
git clone git@github.com:butter6482/AI-Rag.git
cd AI-Rag
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
v
