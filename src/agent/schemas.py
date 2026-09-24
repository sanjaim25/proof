from pydantic import BaseModel, Field
from typing import List, Optional

class Turn(BaseModel):
    speaker: str = Field(description="Must be 'customer' or 'brand'")
    text: str = Field(description="The text of the message")

class AgentRequest(BaseModel):
    customer_message: str
    conversation_context: Optional[List[Turn]] = None

class EvidenceItem(BaseModel):
    case_id: str
    similarity: float
    reason: str

class AgentResponse(BaseModel):
    intent: str = Field(description="One of the 11 approved intents")
    intent_confidence: float = Field(description="Confidence between 0 and 1")
    reply: str = Field(description="The draft reply to the customer")
    escalate: bool = Field(description="True if human intervention is required")
    escalation_reason: Optional[str] = Field(description="Required if escalate is true")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Historical cases used to ground the reply")
