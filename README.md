# 🛡️ SupportProof

**AI Customer-Support Agent Built from Real Twitter Conversations**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](#)
[![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](#)

SupportProof is an end-to-end Machine Learning pipeline and Full-Stack web application that transforms raw Twitter customer-support conversations into a production-grade, **RAG-powered support agent** with strict deterministic safety guardrails.

**👉 For a complete, in-depth technical explanation of the machine learning pipeline, algorithms, intent taxonomy, and safety guardrails, please read [overview.md](./overview.md).**

---

## 🚀 Quick Start (Web Application)

SupportProof is fully deployable and includes a modern React frontend and a FastAPI backend. 

### 1. Setup Environment
```bash
git clone https://github.com/sanjaim25/proof.git
cd proof
pip install -r requirements.txt
cp .env.example .env
```
*Be sure to add your `GROQ_API_KEY` to the `.env` file.*

### 2. Run the Backend (FastAPI)
```bash
python -m uvicorn src.api.server:app --reload --host 127.0.0.1 --port 8000
```

### 3. Run the Frontend (React)
Open a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173/** in your browser to chat with the AI agent!

---

## 🏗️ Project Structure

```text
supportproof/
├── frontend/                           # React + Vite Web UI
├── src/
│   ├── api/                            # FastAPI Backend (server.py)
│   ├── agent/                          # RAG Agent, TF-IDF Retriever, and Guardrails
│   ├── data/                           # Data extraction and cleaning scripts
│   ├── evaluation/                     # LLM-as-a-judge and golden set evaluation
│   └── intent/                         # Unsupervised intent clustering taxonomy
├── data/                               # Processed Kaggle datasets and golden labels
├── Dockerfile                          # Deployment container configuration
├── Procfile                            # PaaS deployment config
├── overview.md                         # Detailed technical deep-dive
└── README.md                           # Quick start guide (You are here)
```

## 🧠 Core Features
- **Retrieval-Augmented Generation (RAG):** Answers are mathematically grounded in real historical human resolutions extracted from a 3-million-tweet Kaggle dataset.
- **Anti-Hallucination Guardrails:** Python scripts deterministically block the AI from inventing fake URLs or granting unauthorized refunds.
- **LLM-as-a-Judge Tested:** Evaluated against a 200-conversation golden set to guarantee empathy, correctness, and safety.
- **Docker & Deploy Ready:** Pre-configured with Docker, dynamic environment variables, and optimized for instant deployment to Render, AWS, or Vercel.

## 📄 License
This project is licensed under the MIT License.
