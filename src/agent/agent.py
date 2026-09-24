import os
import re
import sys
from typing import Dict, Any

from src.agent.schemas import AgentRequest, AgentResponse, EvidenceItem
from src.agent.providers import GeminiProvider, OpenAIProvider, GroqProvider
from src.agent.retriever import Retriever
from src.agent.prompts import SYSTEM_PROMPT, format_prompt

VALID_INTENTS = {
    "technical_issue", "refund_request", "delivery_delay", "account_prime",
    "order_tracking", "return_request", "issue_with_received_item",
    "missing_delivery", "gift_card_promotion", "cancel_order", "other_or_unclear"
}

_PROVIDERS = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "groq": GroqProvider,
}

class SupportProofAgent:
    def __init__(self, k: int = 5, sim_threshold: float = 0.0):
        provider_name = os.environ.get("LLM_PROVIDER", "openai").lower()
        provider_cls = _PROVIDERS.get(provider_name)
        if provider_cls is None:
            raise ValueError(
                f"Unknown LLM_PROVIDER '{provider_name}'. "
                f"Supported: {', '.join(_PROVIDERS)}"
            )
        self.provider = provider_cls()
        self.retriever = Retriever(k=k, threshold=sim_threshold)
        # Assuming retriever has already been fitted if not, the caller should fit it
        
    def _validate_grounding(self, response: AgentResponse, retrieved_cases: list) -> Dict[str, Any]:
        """Runs deterministic smart validation on the LLM response."""
        reply_lower = response.reply.lower()
        evidence_text = " ".join([c["brand_response"].lower() for c in retrieved_cases])
        
        failures = []
        
        # 1. Invalid Intent
        if response.intent not in VALID_INTENTS:
            failures.append(f"Invalid intent: {response.intent}")
            
        # 2. Empty or excessive reply
        word_count = len(response.reply.split())
        if word_count == 0:
            failures.append("Empty reply generated.")
        elif word_count > 150:
            failures.append(f"Reply exceeds maximum length ({word_count} words).")
            
        # 3. Missing escalation reason
        if response.escalate and not response.escalation_reason:
            failures.append("Escalate set to true but missing escalation reason.")
            
        # 4. Smart Monetary check: If reply has a '$' or 'refund', does evidence support it?
        # A simple heuristic: if the agent outputs "$XX", the number XX must be in the evidence.
        amounts = re.findall(r'\$\d+(?:\.\d+)?', response.reply)
        for amt in amounts:
            if amt not in evidence_text:
                failures.append(f"Unsupported monetary amount generated: {amt}")
                
        # 5. Unsupported claims of completion
        completion_phrases = ["i have cancelled", "i have refunded", "has been credited", "i have updated"]
        for phrase in completion_phrases:
            if phrase in reply_lower and phrase not in evidence_text:
                failures.append(f"Unsupported claim of completed action: '{phrase}'")
                
        # 6. Suspicious URLs (excluding standard amazon ones)
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', response.reply)
        for url in urls:
            if "amazon" not in url.lower() and url not in evidence_text:
                failures.append(f"Unsupported URL generated: {url}")
                
        return {
            "valid": len(failures) == 0,
            "failures": failures
        }

    def process(self, request: AgentRequest) -> dict:
        # 1. Retrieve historical evidence
        retrieval = self.retriever.retrieve(request.customer_message)
        cases = retrieval["cases"]
        confidence = retrieval["confidence"]
        
        evidence_items = [
            EvidenceItem(case_id=c["case_id"], similarity=c["similarity"], reason=c["brand_response"])
            for c in cases
        ]
        
        # 2. Format Prompt
        context_dicts = [{"speaker": t.speaker, "text": t.text} for t in (request.conversation_context or [])]
        user_prompt = format_prompt(request.customer_message, context_dicts, cases, confidence)
        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
        
        # 3. Generate LLM Output
        try:
            llm_response = self.provider.generate(full_prompt, AgentResponse)
        except Exception as e:
            # Fallback if LLM fails completely (e.g. invalid JSON that Pydantic rejects)
            print(f"LLM Generation Error: {e}", file=sys.stderr)
            return {
                "intent": "other_or_unclear",
                "intent_confidence": 0.0,
                "reply": "We are currently experiencing technical difficulties. Please hold for a human agent.",
                "escalate": True,
                "escalation_reason": f"LLM Generation/Parsing Error: {str(e)}",
                "evidence": [e.model_dump() for e in evidence_items],
                "retrieval_confidence": confidence,
                "retrieval_scores": {
                    "top_sim": retrieval["top_sim"],
                    "mean_sim": retrieval["mean_sim"]
                },
                "validation_failures": ["LLM Error"],
                "api_error": str(e)
            }
            
        # (The LLM handles escalation policy internally based on confidence)
        
        # Override evidence list with what we actually fed the model (to prevent hallucinated evidence)
        llm_response.evidence = evidence_items
        
        # 5. Safety Grounding Check
        val_result = self._validate_grounding(llm_response, cases)
        original_reply = llm_response.reply
        
        if not val_result["valid"]:
            # Overwrite according to safety rules
            llm_response.escalate = True
            reason_str = "Grounding Validation Failures: " + ", ".join(val_result["failures"])
            llm_response.escalation_reason = f"{llm_response.escalation_reason} | {reason_str}" if llm_response.escalation_reason else reason_str
            llm_response.reply = "Please wait while I connect you to a human agent to resolve this securely."
            
        output = llm_response.model_dump()
        output["retrieval_confidence"] = confidence
        output["retrieval_scores"] = {
            "top_sim": retrieval["top_sim"],
            "mean_sim": retrieval["mean_sim"]
        }
        output["validation_failures"] = val_result["failures"]
        output["original_draft"] = original_reply if not val_result["valid"] else None
        output["api_error"] = None
        
        return output
