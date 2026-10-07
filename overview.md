# SupportProof: Complete Project Overview

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

## 3. How it Works: The Architecture

The project is broken down into a backend AI pipeline and a modern frontend UI. Here is the step-by-step flow of what happens when a customer types a message:

### Step 1: Retrieval (Finding Evidence)
Using **TF-IDF Vector Search**, the system scans thousands of past Amazon customer service threads. If a customer says *"my parcel is missing"*, the system retrieves the top 5 historical conversations where human agents successfully solved missing parcel complaints.

### Step 2: Generation (The LLM)
The system connects to an LLM provider (like Groq, OpenAI, or Gemini). It sends the LLM a strict prompt: *"Here is the customer's problem. Here are 5 historical examples of how we solved this. Figure out the customer's intent, and draft a reply using ONLY the provided examples."*

### Step 3: Safety Guardrails (The "Proof")
Before the drafted reply is ever shown to the customer, it goes through strict Python-based deterministic checks. 
- **URL Check:** If the AI includes an `http://` link that wasn't in the historical evidence, the message is instantly blocked.
- **Action Check:** If the AI promises a refund or replacement, the system checks if it is confident enough to do so.
If a safety check fails, the system overrides the AI and **Escalates** the ticket to a human agent instead.

---

## 4. The 11-Stage ML Pipeline

To build this from scratch, the project repository (`src/`) contains 11 distinct data science and engineering stages:

1. **Data Processing (Stages 1-3):** Analyzed a 3-million-tweet CSV file, extracted Amazon's data, and stitched disconnected tweets into readable conversational threads.
2. **Intent Discovery (Stage 4):** Used unsupervised machine learning to group thousands of messages into 11 distinct "Intents" (e.g., `delivery_delay`, `refund_request`).
3. **Retrieval & Agent Core (Stages 5-7):** Built the search engine and the safety rules.
4. **Rigorous Evaluation (Stages 8-11):** 
   - Created a **Golden Set** of 200 human-labeled test questions.
   - Built an **LLM Judge** that uses a second AI to grade the primary AI on Empathy, Correctness, and Safety.
   - Handled API Rate Limits automatically by saving progress to checkpoints.

---

## 5. The Full Stack Application

This project isn't just a Python script—it's a fully deployed application:

- **The Backend:** A **FastAPI** server (`src/api/server.py`) that wraps the Python agent logic and exposes it as a REST API endpoint (`http://localhost:8000/chat`).
- **The Frontend:** A **React + Vite** web application (`frontend/`) featuring a modern, glassmorphism dark-mode UI. It connects to the API and renders the chat interface, typing indicators, and Escalation Warning badges in real-time.

**In summary:** SupportProof is a production-ready, RAG-based AI support agent with strict anti-hallucination guardrails, a full evaluation suite, and a modern web interface.
