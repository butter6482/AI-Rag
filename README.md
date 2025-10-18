# 🤖 AI RAG Assistant

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-ai--rag--1.onrender.com-blue?style=for-the-badge)](https://ai-rag-1.onrender.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-0db7ed?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-FF6C37?style=for-the-badge)](https://openrouter.ai/)

A **Retrieval-Augmented Generation (RAG)** web app that performs **real-time web searches** and generates concise, cited answers powered by **FastAPI**, **Streamlit**, **DuckDuckGo Search**, and **OpenRouter (Gemma 2 9B)**.  
Deployed live on **Render** → 🌐 [ai-rag-1.onrender.com](https://ai-rag-1.onrender.com)

---

## ✨ Features

- 🌍 **Live web search** using `ddgs` (DuckDuckGo Search)  
- 🧠 **RAG pipeline** combining search results with LLM reasoning  
- 🗣️ **Automatic language detection** (English / Spanish)  
- 🧾 **Source citations** for each answer  
- ⚙️ **FastAPI backend** + **Streamlit frontend**  
- 🐳 **Dockerized setup** for easy deployment  
- 🚀 **CI/CD ready** via GitHub Actions

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | Streamlit |
| **Backend** | FastAPI |
| **Search** | DuckDuckGo Search (`ddgs`) |
| **Model API** | OpenRouter – *Gemma 2 9B* |
| **Infra** | Docker + Render |
| **CI/CD** | GitHub Actions |

---

## ⚡ Quick Start

### 🐳 Using Docker Compose (Recommended)
```bash
# Set environment variables
export OPENROUTER_API_KEY=sk-or-your-key-here

# Start both services
docker compose up --build

# Backend: http://localhost:8080
# Frontend: http://localhost:8501
