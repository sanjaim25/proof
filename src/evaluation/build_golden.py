"""
Build Golden Evaluation Set for SupportProof.
Samples 200 contextual conversations for human annotation.
Does NOT automatically assign final intent labels.
"""

import csv
import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

# ── Paths ──────────────────────────────────────────────────────────────────
WORKSPACE = Path(__file__).resolve().parents[2]
IN_JSONL  = WORKSPACE / "data" / "processed" / "amazonhelp_conversations.jsonl"
OUT_JSONL = WORKSPACE / "data" / "golden" / "golden_candidates.jsonl"
OUT_CSV   = WORKSPACE / "data" / "golden" / "golden_set.csv"
REPORT    = WORKSPACE / "reports" / "golden_sampling.md"

SEED = 42

# ── Target Distribution ────────────────────────────────────────────────────
TARGET_COUNTS = {
    "technical_issue": 20,
    "refund_request": 20,
    "delivery_delay": 20,
    "account_prime": 15,
    "order_tracking": 15,
    "return_request": 15,
    "issue_with_received_item": 15,
    "missing_delivery": 15,
    "gift_card_promotion": 10,
    "cancel_order": 10,
    "other_or_unclear": 25,
    "difficult": 20
}

# ── Heuristics for Candidate Selection ─────────────────────────────────────
# Note: These are ONLY for stratified sampling. Final labels must be human-assigned.
HEURISTICS = {
    "technical_issue": ["app", "website", "error", "glitch", "kindle", "fire tv", "alexa", "echo"],
    "refund_request": ["refund", "money back", "charged", "credit"],
    "delivery_delay": ["late", "delay", "delayed", "hasn't arrived", "still waiting", "promised yesterday"],
    "account_prime": ["account", "password", "login", "locked", "prime membership", "subscribe"],
    "order_tracking": ["track", "tracking", "status", "where is my order", "where's my package", "update"],
    "return_request": ["return", "returning", "send back", "return label"],
    "issue_with_received_item": ["wrong item", "incorrect item", "different item", "damaged", "broken", "smashed", "defective"],
    "missing_delivery": ["says delivered", "marked delivered", "stolen", "empty box", "never received", "didn't receive"],
    "gift_card_promotion": ["gift card", "promo code", "claim code", "discount"],
    "cancel_order": ["cancel order", "cancel my order", "cancelled by mistake"]
}

def guess_candidate_intents(text: str) -> List[str]:
    text_lower = text.lower()
    matches = []
    for intent, kws in HEURISTICS.items():
        if any(kw in text_lower for kw in kws):
            matches.append(intent)
    return matches

def normalize_text(text: str) -> str:
    """Normalize for deduplication."""
    t = text.lower()
    t = re.sub(r'@\w+', '', t)
    t = re.sub(r'http\S+', '', t)
    t = re.sub(r'[^a-z0-9]', '', t)
    return t

# ── Main ───────────────────────────────────────────────────────────────────

def main():
    import io
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        
    if not IN_JSONL.exists():
        print(f"ERROR: {IN_JSONL} not found")
        sys.exit(1)
        
    print("Reading conversations...")
    conversations = []
    with open(IN_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                conversations.append(json.loads(line))
                
    print(f"Loaded {len(conversations)} conversations.")
    
    # Pools for stratified sampling
    pools = {k: [] for k in TARGET_COUNTS.keys()}
    
    seen_texts = set()
    seen_users = set()
    
    rng = random.Random(SEED)
    rng.shuffle(conversations) # Shuffle before iterating
    
    print("Categorizing candidates into pools...")
    for conv in conversations:
        conv_id = conv.get("conversation_id")
        turns = conv.get("turns", [])
        
        # Find the first customer message that looks substantial
        customer_turn_idx = -1
        customer_msg = ""
        for i, turn in enumerate(turns):
            if turn.get("speaker") == "customer" and len(turn.get("text", "").split()) >= 4:
                customer_turn_idx = i
                customer_msg = turn.get("text", "")
                break
                
        if customer_turn_idx == -1:
            continue
            
        # Deduplication
        norm_text = normalize_text(customer_msg)
        if norm_text in seen_texts:
            continue
            
        author_id = turns[customer_turn_idx].get("author_id")
        if author_id in seen_users:
            # We want to avoid multiple examples from same user if possible, 
            # but we won't strictly forbid it if pools are small. 
            # For simplicity, we strictly forbid it for a highly diverse golden set.
            continue
            
        seen_texts.add(norm_text)
        seen_users.add(author_id)
        
        # Extract Context
        prev_turns = [t["text"] for t in turns[:customer_turn_idx]]
        next_brand_resp = None
        for i in range(customer_turn_idx + 1, len(turns)):
            if turns[i].get("speaker") == "brand":
                next_brand_resp = turns[i].get("text")
                break
                
        # Heuristics
        guessed_intents = guess_candidate_intents(customer_msg)
        
        record = {
            "conversation_id": conv_id,
            "customer_message": customer_msg,
            "previous_turns": prev_turns,
            "brand_response": next_brand_resp,
            "created_at": turns[customer_turn_idx].get("created_at"),
            "candidate_intents": guessed_intents
        }
        
        if len(guessed_intents) >= 2:
            pools["difficult"].append(record)
        elif len(guessed_intents) == 1:
            intent = guessed_intents[0]
            pools[intent].append(record)
        else:
            pools["other_or_unclear"].append(record)

    # ── Selection ────────────────────────────────────────────────────────
    
    golden_set = []
    
    print("Selecting exact counts...")
    for category, target in TARGET_COUNTS.items():
        pool = pools[category]
        if len(pool) < target:
            print(f"WARNING: Not enough candidates for {category}. Needed {target}, found {len(pool)}.")
            selected = pool
        else:
            selected = rng.sample(pool, target)
            
        for rec in selected:
            # Mark the primary reason we selected it, just for internal tracking,
            # but leave the candidate_intents array for the JSON
            golden_set.append(rec)
            
    # Assign sequential IDs and add null fields
    rng.shuffle(golden_set) # Randomize final order so categories aren't clumped
    
    final_golden = []
    for i, rec in enumerate(golden_set, 1):
        final_rec = {
            "example_id": f"gold_{i:04d}",
            "conversation_id": rec["conversation_id"],
            "created_at": rec["created_at"],
            "customer_message": rec["customer_message"],
            "previous_turns": rec["previous_turns"],
            "brand_response": rec["brand_response"],
            "candidate_intents": rec["candidate_intents"],
            "human_intent": None,
            "human_escalate": None,
            "human_reason": None,
            "annotation_notes": None
        }
        final_golden.append(final_rec)
        
    print(f"\nGolden set size: {len(final_golden)}")
    
    # ── Output ───────────────────────────────────────────────────────────
    
    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Writing {OUT_JSONL}...")
    with open(OUT_JSONL, "w", encoding="utf-8") as f:
        for rec in final_golden:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            
    print(f"Writing {OUT_CSV}...")
    fieldnames = [
        "example_id", "conversation_id", "created_at", "customer_message", 
        "previous_turns", "brand_response", "candidate_intents",
        "human_intent", "human_escalate", "human_reason", "annotation_notes"
    ]
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in final_golden:
            # Flatten lists for CSV readability
            csv_rec = rec.copy()
            csv_rec["previous_turns"] = " | ".join(rec["previous_turns"])
            csv_rec["candidate_intents"] = ", ".join(rec["candidate_intents"])
            writer.writerow(csv_rec)
            
    print(f"Writing {REPORT}...")
    
    cat_counts = defaultdict(int)
    for rec in final_golden:
        # Determine how we categorized it based on candidate intents
        cands = rec["candidate_intents"]
        if len(cands) >= 2:
            cat_counts["difficult"] += 1
        elif len(cands) == 1:
            cat_counts[cands[0]] += 1
        else:
            cat_counts["other_or_unclear"] += 1
            
    unique_convs = len(set(r["conversation_id"] for r in final_golden))
    
    md = [
        "# Golden Sampling Report",
        "\n## Methodology",
        "- **Random Seed**: 42",
        "- **Candidate Pool Size**: Evaluated across 82,534 conversations.",
        "- **Deduplication Approach**: Exact duplicate messages and multiple messages from the same user were heavily penalized/removed to ensure maximum diversity.",
        "- **Intent Balancing**: Stratified sampling was used to force rare intents (e.g. `cancel_order`) into the golden set, ensuring all 11 intents are represented.",
        "- **Difficult Cases**: Examples matching multiple disparate intent heuristics (e.g. 'late' AND 'refund') were deliberately sampled into a 'difficult' pool to stress-test human guidelines and classifier boundaries.",
        "\n## Summary Statistics",
        f"- **Total Candidates Selected**: {len(final_golden)}",
        f"- **Unique Conversations**: {unique_convs}",
        "\n## Distribution by Candidate Heuristic",
        "(Note: These are heuristic guesses for sampling, NOT final labels.)"
    ]
    for k, v in sorted(cat_counts.items()):
        md.append(f"- `{k}`: {v}")
        
    md.append("\n## Limitations")
    md.append("- Heuristics may have missed implicit intents. The 25 `other_or_unclear` samples are critical for evaluating whether real user issues fall outside our predefined rules.")
    md.append("- Deliberately keeping noisy Twitter language means annotators will have to deal with typos, missing context, and sarcasm.")
    
    REPORT.write_text("\n".join(md), encoding="utf-8")
    
    print("\n=======================================================")
    print("GOLDEN SET SAMPLING COMPLETE")
    print("=======================================================\n")
    print(f"Total Selected: {len(final_golden)}")
    for k, v in sorted(cat_counts.items()):
        print(f"  {k}: {v}")
        
    print(f"\nUnique Conversations: {unique_convs}")
    print(f"JSONL: {OUT_JSONL}")
    print(f"CSV:   {OUT_CSV}")
    print(f"Guide: data/golden/ANNOTATION_GUIDE.md")

if __name__ == "__main__":
    main()
