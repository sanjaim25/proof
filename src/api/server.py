from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.agent.agent import SupportProofAgent
from src.agent.schemas import AgentRequest
from dotenv import load_dotenv
import os

# Load API keys from .env
load_dotenv(override=True)

app = FastAPI(title="SupportProof API")

# Allow dynamic production URL or default localhost
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Add CORS middleware to allow the React frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent and load the retrieval dataset into memory
print("Initializing SupportProof Agent (loading retrieval corpus)...")
agent = SupportProofAgent(k=5, sim_threshold=0.55)
agent.retriever.fit()
print("Agent ready.")

@app.get("/")
async def health():
    return {"status": "ok", "service": "SupportProof API"}

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    # Process the message through the real RAG agent
    agent_req = AgentRequest(customer_message=req.message)
    res = agent.process(agent_req)
    
    # Return exactly the format the React UI expects
    return {
        "reply": res["reply"],
        "escalate": res["escalate"],
        "escalateReason": res["escalation_reason"]
    }
