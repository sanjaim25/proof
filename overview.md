# SupportProof: Complete Project Overview & Pipeline Deep-Dive

## 1. The Problem: Why does this project exist?

Modern AI and Large Language Models (LLMs) are incredibly good at talking to humans, which makes them perfect for Customer Support. However, businesses have a massive problem deploying them: **Hallucinations**.

If you connect a standard ChatGPT-like bot to your customer support system, it might:
- Hallucinate a fake return policy.
- Promise a customer a $100 refund that doesn't exist.
- Invent fake "Help Center" URLs that lead to 404 error pages.

**The Goal:** We need an AI customer support agent that sounds natural and helpful, but is **mathematically forced** to only use real historical solutions, and strictly guarded against making up fake promises. 

---

## 2. The Solution: What is SupportProof?

SupportProof is an **end-to-end Machine Learning pipeline and web application** that solves the hallucination problem. 

Instead of letting the AI guess the answer, SupportProof uses **Retrieval-Augmented Generation (RAG)**. It looks at a database of millions of real, historical customer support conversations (taken from a real Kaggle Twitter dataset of `@AmazonHelp`). 

When a new customer asks a question, the system finds how human agents solved that exact problem in the past, and forces the AI to base its answer *only* on that historical evidence.

---

## 3. The Complete 11-Stage Pipeline (How it was built)

To build this from scratch, we didn't just write a chat script. We built a rigorous 11-stage Data Science and Machine Learning pipeline. Here is exactly what happens in each stage:

### Phase A: Data Processing (Stages 1-3)
*Goal: Turn messy, raw data into clean, structured conversations.*

* **Stage 1: Explore & Inspect** (`src/data/inspect_dataset.py`)
  We started with a massive 3-million row CSV of raw tweets from Kaggle. This stage analyzed the data size, columns, and overall structure to understand what we were working with.
* **Stage 2: Brand Selection** (`src/data/analyze_brands.py`)
  The dataset contained tweets from Apple, Uber, Spotify, etc. This stage analyzed which brand had the most complete, high-quality back-and-forth conversations. **@AmazonHelp** won because they have excellent, detailed support threads.
* **Stage 3: Conversation Reconstruction** (`src/data/extract_brand.py`)
  Twitter data is chaotic. A customer tweets, the brand replies, the customer replies again. This stage stitched those individual, disconnected tweets together into chronological "Threads" so the AI can read them like a normal chat log.

### Phase B: Understanding the Customer (Stage 4)
*Goal: Teach the AI what customers actually want.*

* **Stage 4: Intent Taxonomy Discovery** (`src/intent/`)
  We didn't want to manually guess what customers ask Amazon. Instead, we used Unsupervised Machine Learning (TF-IDF Clustering and LLM analysis) to group thousands of messages together automatically. Through 3 iterations (v1, v2, v3), the system automatically discovered **11 distinct categories** of problems (e.g., `missing_delivery`, `refund_request`, `technical_issue`). 

### Phase C: Building the AI Agent (Stages 5-7)
*Goal: Build the brain and the safety guardrails.*

* **Stage 5: Data Splitting** (`src/evaluation/split_data.py`)
  To properly test the AI, we split the data into a "Development Set" (for the AI to search through) and a "Golden Set" (a secret exam the AI has never seen before).
* **Stage 6: The Retriever** (`src/agent/retriever.py`)
  We built a search engine using **TF-IDF Vector Search**. When a user types a message, this engine instantly scans the Development Set and returns the Top 5 most mathematically similar historical conversations.
* **Stage 7: The RAG Agent & Safety Rules** (`src/agent/agent.py`)
  This is the core brain. It sends the customer message and the Top 5 historical examples to the LLM (Groq) to draft a reply. Crucially, it applies **Deterministic Safety Checks**:
  - *No URLs:* If the AI outputs a link not found in the evidence, block it.
  - *No Hallucinated Refunds:* If the AI promises a refund it shouldn't, block it.
  If a rule is broken, the AI is overridden, and the ticket is escalated to a human.

### Phase D: Rigorous Testing & Evaluation (Stages 8-11)
*Goal: Mathematically prove the agent works and doesn't hallucinate.*

* **Stage 8: The Golden Set** (`src/evaluation/build_golden.py`)
  We randomly sampled 200 conversations and built a web UI to manually, humanly annotate what the "perfect" answer and intent should be for each one.
* **Stage 9: Baselines & Agent Evaluation** (`src/evaluation/run_agent.py`)
  We ran the AI against all 200 Golden questions to see how well it performed. It handles API rate limits by saving "checkpoints" so it never loses progress if the server crashes. We also compared it to "dumb" baselines (like guessing the most common intent every time) to prove the AI is actually smart.
* **Stage 10: LLM-as-a-Judge** (`src/evaluation/llm_judge.py`)
  Numbers (like F1-scores) don't tell the whole story for chat bots. We used a second, separate AI to read every single reply our agent generated, and graded it on a scale of 1-5 for Empathy, Correctness, and Safety.
* **Stage 11: Error Analysis** (`reports/`)
  We analyzed the failures to figure out *why* the agent made mistakes, documenting them in detailed Markdown reports to guide future improvements.

---

## 4. The Full Stack Application (Deployment)

This project isn't just a Python script—it is packaged as a fully deployable enterprise application:

- **The Backend (FastAPI):** We wrapped the Python agent logic in a REST API (`src/api/server.py`). It is containerized using a `Dockerfile`, meaning it can be instantly deployed to cloud servers like AWS, Google Cloud, or Render.
- **The Frontend (React + Vite):** A modern, responsive web application (`frontend/`) featuring a glassmorphism dark-mode UI. It connects to the API and renders the chat interface, typing indicators, and Escalation Warning badges in real-time.

**In summary:** SupportProof is a production-ready, RAG-based AI support agent with strict anti-hallucination guardrails, a full evaluation suite, and a modern web interface.
