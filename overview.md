# SupportProof: Complete Project Overview & Pipeline Deep-Dive

## 1. The Problem: Why does this project exist?

Modern AI and Large Language Models (LLMs) are incredibly good at talking to humans, which makes them perfect for Customer Support. However, businesses have a massive problem deploying them: **Hallucinations**.

If you connect a standard ChatGPT-like bot to your customer support system, it might:
- Hallucinate a fake return policy.
- Promise a customer a $100 refund that doesn't exist.
- Invent fake "Help Center" URLs that lead to 404 error pages.
- Give advice that legally binds the company to a false claim.

**The Goal:** We need an AI customer support agent that sounds natural and helpful, but is **mathematically forced** to only use real historical solutions, and strictly guarded against making up fake promises. SupportProof acts as a bridge between the fluid conversational abilities of modern LLMs and the strict, inflexible policy requirements of enterprise customer service.

---

## 2. The Solution: What is SupportProof?

SupportProof is an **end-to-end Machine Learning pipeline and web application** that solves the hallucination problem. 

Instead of letting the AI guess the answer from its pre-trained weights, SupportProof uses **Retrieval-Augmented Generation (RAG)**. It looks at a database of millions of real, historical customer support conversations (taken from a real Kaggle Twitter dataset of `@AmazonHelp`). 

When a new customer asks a question, the system finds how human agents solved that exact problem in the past, and forces the AI to base its answer *only* on that historical evidence. If the AI deviates from this evidence, hardcoded guardrails intercept the message and escalate the issue to a human.

---

## 3. The Complete 11-Stage Pipeline (How it was built)

To build this from scratch, we didn't just write a chat script. We built a rigorous 11-stage Data Science and Machine Learning pipeline. Here is exactly what happens in each stage:

### Phase A: Data Processing & Cleaning (Stages 1-3)
*Goal: Turn messy, unstructured social media data into clean, chronological conversations.*

* **Stage 1: Explore & Inspect** (`src/data/inspect_dataset.py`)
  We started with a massive 3-million row CSV of raw tweets from Kaggle. This stage analyzed the data size, columns, and overall structure. Social media data is notoriously dirty, containing emojis, broken links, and fragmented replies.
* **Stage 2: Brand Selection** (`src/data/analyze_brands.py`)
  The dataset contained tweets from Apple, Uber, Spotify, etc. This stage analyzed which brand had the most complete, high-quality back-and-forth conversations. **@AmazonHelp** won because they have excellent, detailed support threads that span multiple turns of conversation.
* **Stage 3: Conversation Reconstruction** (`src/data/extract_brand.py`)
  Twitter data is chaotic. A customer tweets, the brand replies, the customer replies again. This stage used graph-like traversal (matching `in_reply_to_status_id`) to stitch those individual, disconnected tweets together into chronological "Threads" so the AI can read them like a normal chat log. 

### Phase B: Understanding the Customer (Stage 4)
*Goal: Teach the AI what customers actually want without manual human guessing.*

* **Stage 4: Intent Taxonomy Discovery** (`src/intent/`)
  We didn't want to manually guess what customers ask Amazon. Instead, we used Unsupervised Machine Learning. 
  - First, we extracted the root verbs and nouns from customer complaints.
  - Second, we applied clustering algorithms to group thousands of messages together automatically. 
  - Finally, through 3 iterative passes (v1, v2, v3), the system automatically discovered **11 distinct categories** of problems. 
  
  **The Discovered Intents:**
  1. `delivery_delay` (Package is late)
  2. `missing_delivery` (Package says delivered but isn't there)
  3. `refund_request` (Customer wants their money back)
  4. `cancellation` (Customer wants to cancel an order)
  5. `account_issue` (Login or payment method problems)
  6. `prime_subscription` (Issues specific to Amazon Prime)
  7. `damaged_item` (Item arrived broken)
  8. `wrong_item` (Received the incorrect product)
  9. `technical_issue` (Website or Kindle/Echo problems)
  10. `feedback_complaint` (General anger or feedback)
  11. `other_or_unclear` (Fallback for vague queries)

### Phase C: Building the AI Agent & Guardrails (Stages 5-7)
*Goal: Build the brain and the safety guardrails.*

* **Stage 5: Data Splitting & Leakage Prevention** (`src/evaluation/split_data.py`)
  To properly test the AI, we split the data into a "Development Set" (for the AI to search through) and a "Golden Set" (a secret exam the AI has never seen before). A strict anti-leakage script guarantees no overlap.
* **Stage 6: The RAG Retriever** (`src/agent/retriever.py`)
  We built a custom search engine using **TF-IDF Vector Search and Cosine Similarity**. When a user types a message, this engine converts their text into a mathematical vector, compares it against thousands of historical vectors, and instantly returns the Top 5 most mathematically similar historical conversations.
* **Stage 7: The Agent Core & Safety Rules** (`src/agent/agent.py`)
  This is the core brain. It sends the customer message and the Top 5 historical examples to the LLM (Groq API) to draft a reply. Crucially, it applies **Deterministic Safety Checks**:
  - *No URLs:* If the AI outputs a link (`http://` or `https://`) that was not explicitly present in the historical evidence, the system blocks it.
  - *No Hallucinated Refunds:* If the AI promises a refund it shouldn't, block it.
  - *No Account Actions:* If the AI claims it has "updated your account", block it.
  If a rule is broken, the AI is overridden, and the ticket is safely escalated to a human.

### Phase D: Rigorous Testing & Evaluation (Stages 8-11)
*Goal: Mathematically prove the agent works and doesn't hallucinate.*

* **Stage 8: The Golden Set** (`src/evaluation/build_golden.py`)
  We randomly sampled 200 conversations and built a web UI to manually, humanly annotate what the "perfect" answer and intent should be for each one.
* **Stage 9: Baselines & Agent Evaluation** (`src/evaluation/run_agent.py`)
  We ran the AI against all 200 Golden questions to see how well it performed. We engineered it to handle API rate limits by saving "checkpoints" to disk, so if the LLM server crashes on example 150, the script resumes at 151 without losing data. 
* **Stage 10: LLM-as-a-Judge** (`src/evaluation/llm_judge.py`)
  Numbers (like F1-scores) don't tell the whole story for chat bots. We used an advanced prompt engineering technique where a second, separate AI reads every single reply our agent generated, and grades it on a scale of 1-5 for Empathy, Correctness, and Safety.
* **Stage 11: Error Analysis** (`reports/`)
  We analyzed the failures to figure out *why* the agent made mistakes, documenting them in detailed Markdown reports to guide future improvements.

---

## 4. The Full Stack Architecture & Deployment

This project isn't just a Python script—it is packaged as a fully deployable enterprise application using modern DevOps practices.

### Backend: FastAPI & Python
- **RESTful API:** We wrapped the Python agent logic in a REST API (`src/api/server.py`). 
- **Dockerized:** The entire backend is containerized using a custom `Dockerfile` and `.dockerignore`. This ensures environment consistency and means it can be instantly deployed to cloud servers like AWS ECS, Google Cloud Run, or Render.
- **Dynamic Configuration:** It utilizes environment variables (`.env`) for API keys and dynamic CORS origins to securely accept traffic from the frontend.

### Frontend: React & Vite
- **Modern UI/UX:** A responsive web application (`frontend/`) featuring a glassmorphism dark-mode UI built with React.
- **Real-time Feedback:** It connects to the FastAPI backend and renders the chat interface, realistic typing indicators, and distinct Escalation Warning badges in real-time.
- **Deploy Ready:** Configured to read backend URLs via `import.meta.env`, making it ready for instant deployment on Vercel or Netlify.

---

## 5. Key Technical Takeaways

For software engineers and data scientists reviewing this project, the major highlights are:
1. **Production-Minded AI:** Prioritizing safety, grounding, and deterministic validation over flashy but unreliable generative outputs.
2. **Resilient Data Engineering:** Checkpointing logic for rate limits, zero-leakage data splits, and automated evaluation suites.
3. **End-to-End Delivery:** Owning the lifecycle from messy Kaggle CSVs, to Unsupervised NLP clustering, to RAG prompt engineering, all the way to a containerized React/FastAPI web deployment.
