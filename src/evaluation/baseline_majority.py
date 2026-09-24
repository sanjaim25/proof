"""
Majority (Trivial) Baseline.
Always predicts the most common intent in the Development set.
Always predicts escalate = No.
Returns a generic fallback reply.
"""

import json
from collections import Counter
from pathlib import Path

from src.evaluation.build_golden import guess_candidate_intents

WORKSPACE = Path(__file__).resolve().parents[2]
IN_JSONL = WORKSPACE / "data" / "processed" / "amazonhelp_conversations.jsonl"
DEV_IDS = WORKSPACE / "data" / "processed" / "development_conversation_ids.txt"

class MajorityBaseline:
    def __init__(self):
        self.majority_intent = "other_or_unclear"
        self.generic_reply = "Thanks for contacting us. Please provide more details so we can help."
        
    def fit(self):
        """Finds the majority intent in the development set using heuristics."""
        if not DEV_IDS.exists():
            return
            
        with open(DEV_IDS, "r", encoding="utf-8") as f:
            dev_ids = set(line.strip() for line in f if line.strip())
            
        intent_counts = Counter()
        
        with open(IN_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                conv = json.loads(line)
                if conv["conversation_id"] in dev_ids:
                    # Find first customer msg
                    customer_msg = ""
                    for turn in conv.get("turns", []):
                        if turn.get("speaker") == "customer":
                            customer_msg = turn.get("text", "")
                            break
                            
                    if customer_msg:
                        cands = guess_candidate_intents(customer_msg)
                        if len(cands) == 1:
                            intent_counts[cands[0]] += 1
                        else:
                            intent_counts["other_or_unclear"] += 1
                            
        if intent_counts:
            self.majority_intent = intent_counts.most_common(1)[0][0]

    def predict(self, text: str) -> dict:
        return {
            "intent": self.majority_intent,
            "escalate": False,
            "reply": self.generic_reply,
            "retrieval_similarity": 0.0
        }
