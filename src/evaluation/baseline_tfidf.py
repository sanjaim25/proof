"""
TF-IDF Retrieval Baseline.
Uses the development set to retrieve similar historical cases,
predicting intent by majority vote and generating a reply from the nearest case.
"""

import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

from src.intent.discover import build_tfidf, cosine_similarity, tokenize
from src.evaluation.build_golden import guess_candidate_intents

WORKSPACE = Path(__file__).resolve().parents[2]
IN_JSONL = WORKSPACE / "data" / "processed" / "amazonhelp_conversations.jsonl"
DEV_IDS = WORKSPACE / "data" / "processed" / "development_conversation_ids.txt"

class TFIDFBaseline:
    def __init__(self, k: int = 3, threshold: float = 0.1, escalate_threshold: int = 5):
        self.k = k
        self.threshold = threshold
        self.escalate_threshold = escalate_threshold
        self.corpus: List[Dict] = []
        self.vocab: set = set()
        self.vectors: List[Dict[str, float]] = []
        
    def fit(self):
        """Builds the development corpus and fits TF-IDF."""
        if not DEV_IDS.exists():
            return
            
        with open(DEV_IDS, "r", encoding="utf-8") as f:
            dev_ids = set(line.strip() for line in f if line.strip())
            
        docs_tokens = []
        
        with open(IN_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                conv = json.loads(line)
                if conv["conversation_id"] in dev_ids:
                    # Find first customer msg
                    customer_msg = ""
                    brand_resp = ""
                    customer_idx = -1
                    turns = conv.get("turns", [])
                    
                    for i, turn in enumerate(turns):
                        if turn.get("speaker") == "customer":
                            customer_msg = turn.get("text", "")
                            customer_idx = i
                            break
                            
                    if not customer_msg:
                        continue
                        
                    for i in range(customer_idx + 1, len(turns)):
                        if turns[i].get("speaker") == "brand":
                            brand_resp = turns[i].get("text", "")
                            break
                            
                    # Silver labels
                    cands = guess_candidate_intents(customer_msg)
                    silver_intent = cands[0] if len(cands) == 1 else "other_or_unclear"
                    # Heuristic for historical escalation: if conv is unusually long (>= 5 turns)
                    silver_escalate = len(turns) >= self.escalate_threshold
                    
                    self.corpus.append({
                        "message": customer_msg,
                        "reply": brand_resp,
                        "intent": silver_intent,
                        "escalate": silver_escalate
                    })
                    
                    docs_tokens.append(tokenize(customer_msg))
                    
        if docs_tokens:
            self.vectors, self.vocab = build_tfidf(docs_tokens)

    def _vectorize(self, text: str) -> Dict[str, float]:
        """Vectorize a single document against the fitted vocab."""
        tokens = tokenize(text)
        vec = {}
        for token in set(tokens):
            if token in self.vocab:
                vec[token] = 1.0 # Simple binary TF for query, since IDF is pre-computed globally in a real system. But we'll just use a fast approximation.
        return vec

    def predict(self, text: str) -> dict:
        if not self.vectors:
            return {
                "intent": "other_or_unclear",
                "escalate": False,
                "reply": "",
                "retrieval_similarity": 0.0
            }
            
        # Very simple query vectorization (just matching overlap)
        q_tokens = set(tokenize(text)).intersection(self.vocab)
        q_vec = {t: 1.0 for t in q_tokens}
        
        scores = []
        for i, doc_vec in enumerate(self.vectors):
            sim = cosine_similarity(q_vec, doc_vec)
            scores.append((sim, self.corpus[i]))
            
        scores.sort(key=lambda x: x[0], reverse=True)
        top_k = scores[:self.k]
        
        top_sim = top_k[0][0] if top_k else 0.0
        
        if top_sim < self.threshold:
            return {
                "intent": "other_or_unclear",
                # Unfamiliar issue -> escalate
                "escalate": True, 
                "reply": "Thanks for contacting us. Please provide more details so we can help.",
                "retrieval_similarity": top_sim
            }
            
        # Majority vote intent
        intents = [doc["intent"] for sim, doc in top_k]
        predicted_intent = Counter(intents).most_common(1)[0][0]
        
        # Escalate if majority of top K were historically escalated
        escalates = [doc["escalate"] for sim, doc in top_k]
        predicted_escalate = sum(escalates) >= (self.k / 2.0)
        
        # Best historical reply
        predicted_reply = top_k[0][1]["reply"] or "Thanks for contacting us."
        
        return {
            "intent": predicted_intent,
            "escalate": predicted_escalate,
            "reply": predicted_reply,
            "retrieval_similarity": top_sim
        }
