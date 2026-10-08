import json
import gzip
from pathlib import Path
from typing import Dict, List, Tuple

from src.intent.discover import build_tfidf, cosine_similarity, tokenize

WORKSPACE = Path(__file__).resolve().parents[2]
IN_JSONL = WORKSPACE / "data" / "processed" / "dev_corpus.jsonl.gz"
DEV_IDS = WORKSPACE / "data" / "processed" / "development_conversation_ids.txt"

class Retriever:
    def __init__(self, k: int = 5, threshold: float = 0.0):
        self.k = k
        self.threshold = threshold
        self.corpus: List[Dict] = []
        self.vocab: set = set()
        self.vectors: List[Dict[str, float]] = []
        
    def fit(self):
        if not DEV_IDS.exists():
            return
            
        with open(DEV_IDS, "r", encoding="utf-8") as f:
            dev_ids = set(line.strip() for line in f if line.strip())
            
        docs_tokens = []
        
        with gzip.open(IN_JSONL, "rt", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                conv = json.loads(line)
                if conv["conversation_id"] in dev_ids:
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
                            
                    self.corpus.append({
                        "case_id": conv["conversation_id"],
                        "customer_message": customer_msg,
                        "brand_response": brand_resp,
                        "turns": turns
                    })
                    
                    docs_tokens.append(tokenize(customer_msg))
                    
        if docs_tokens:
            self.vectors, self.vocab = build_tfidf(docs_tokens)

    def retrieve(self, text: str) -> dict:
        if not self.vectors:
            return {"cases": [], "confidence": "weak", "top_sim": 0.0, "mean_sim": 0.0}
            
        q_tokens = set(tokenize(text)).intersection(self.vocab)
        q_vec = {t: 1.0 for t in q_tokens}
        
        # L2 Normalize the query vector to bound similarity in [0, 1]
        import math
        norm_sq = sum(v * v for v in q_vec.values())
        if norm_sq > 0:
            norm = math.sqrt(norm_sq)
            q_vec = {t: v / norm for t, v in q_vec.items()}
        
        scores = []
        for i, doc_vec in enumerate(self.vectors):
            sim = cosine_similarity(q_vec, doc_vec)
            if sim >= self.threshold:
                scores.append((sim, self.corpus[i]))
            
        scores.sort(key=lambda x: x[0], reverse=True)
        top_k = scores[:self.k]
        
        retrieved_cases = []
        sims = []
        for sim, doc in top_k:
            retrieved_cases.append({
                "case_id": doc["case_id"],
                "customer_message": doc["customer_message"],
                "brand_response": doc["brand_response"],
                "similarity": sim
            })
            sims.append(sim)
            
        top_sim = sims[0] if sims else 0.0
        mean_sim = sum(sims) / len(sims) if sims else 0.0
        
        if top_sim >= 0.75:
            confidence = "strong"
        elif top_sim >= 0.55:
            confidence = "moderate"
        else:
            confidence = "weak"
            
        return {
            "cases": retrieved_cases,
            "confidence": confidence,
            "top_sim": top_sim,
            "mean_sim": mean_sim
        }
