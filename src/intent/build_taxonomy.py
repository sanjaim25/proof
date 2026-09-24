"""
Build a human-reviewable taxonomy proposal for SupportProof.
Applies strict operational boundaries to separate intents based on actual customer conversations.
"""

import json
import random
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# ── Paths ──────────────────────────────────────────────────────────────────
WORKSPACE = Path(__file__).resolve().parents[2]
IN_JSONL  = WORKSPACE / "data" / "processed" / "amazonhelp_conversations.jsonl"
OUT_JSON  = WORKSPACE / "data" / "processed" / "taxonomy_proposal.json"
REPORT    = WORKSPACE / "reports" / "taxonomy_review.md"

SEED = 42

# ── Extraction & Filtering ─────────────────────────────────────────────────

def is_support_message(text: str) -> bool:
    """Filter out obvious noise: praise, ads, meaningless short text."""
    text_lower = text.lower()
    clean_text = re.sub(r'@\w+', '', text_lower)
    clean_text = re.sub(r'http\S+', '', clean_text).strip()
    
    if len(clean_text) < 15:
        return False
        
    words = clean_text.split()
    if len(words) < 4:
        return False
        
    praise_words = {"thanks", "thank you", "great", "awesome", "love", "best", "amazing", "good job"}
    if len(words) < 10 and any(p in clean_text for p in praise_words) and not any(w in clean_text for w in ["but", "however", "issue", "problem"]):
        return False
        
    return True

def extract_customer_messages(conversations: List[dict]) -> List[str]:
    """Extract valid customer support messages."""
    messages = []
    seen = set()
    for conv in conversations:
        for turn in conv.get("turns", []):
            if turn.get("speaker") == "customer":
                text = turn.get("text", "")
                if is_support_message(text):
                    norm = re.sub(r'\s+', ' ', text.lower().strip())
                    if norm not in seen:
                        seen.add(norm)
                        messages.append(text)
    return messages

# ── Operational Boundaries and Keyword Matching ────────────────────────────

class IntentDefinition:
    def __init__(self, id_str: str, name: str, description: str, in_scope: List[str], out_of_scope: List[str], confusions: List[str], keywords: List[str], negations: List[str], action: str):
        self.id = id_str
        self.name = name
        self.description = description
        self.in_scope = in_scope
        self.out_of_scope = out_of_scope
        self.confusions = confusions
        self.keywords = keywords
        self.negations = negations
        self.action = action # KEEP, MERGE, SPLIT, REMOVE

INTENTS = [
    IntentDefinition(
        "delivery_delay", "Delivery Delay", "Customer says an expected delivery is late.",
        ["Customer says an expected delivery is late.", "Customer says promised delivery date has passed."],
        ["Customer only asks where the package is and the delivery date has not passed.", "Customer says tracking says 'delivered' but they did not receive it."],
        ["order_tracking", "missing_delivery"],
        ["late", "delay", "delayed", "hasn't arrived", "not arrived yet", "still waiting", "promised yesterday"],
        ["delivered", "missing"],
        "KEEP"
    ),
    IntentDefinition(
        "order_tracking", "Order Tracking", "Customer asks for tracking/status/location.",
        ["Customer asks for tracking link, status, or location of their order."],
        ["Delivery date has already passed (delay).", "Package is marked delivered but not received (missing)."],
        ["delivery_delay", "missing_delivery"],
        ["track", "tracking", "status", "where is my order", "where is my package", "where's my", "update"],
        ["late", "delay", "delivered", "missing"],
        "KEEP"
    ),
    IntentDefinition(
        "missing_delivery", "Missing Delivery", "Package is marked delivered but customer did not receive it.",
        ["Package is marked delivered but customer says they did not receive it.", "Package appears stolen or lost."],
        ["Package is merely late but still in transit."],
        ["delivery_delay", "wrong_item"],
        ["says delivered", "marked delivered", "stolen", "empty box", "never received", "didn't receive"],
        ["late", "delay"],
        "KEEP"
    ),
    IntentDefinition(
        "wrong_item", "Wrong Item", "Customer received an item different from what they ordered.",
        ["Customer received the wrong item, size, or color."],
        ["Customer wants to return a correctly fulfilled item because they changed their mind."],
        ["return_request", "missing_delivery"],
        ["wrong item", "incorrect item", "different item", "not what I ordered"],
        ["damaged", "broken"],
        "MERGE (with damaged_item -> issue_with_received_item)"
    ),
    IntentDefinition(
        "damaged_item", "Damaged Item", "Customer received a damaged or defective item.",
        ["Item arrived broken, scratched, torn, or defective."],
        ["Item was stolen or missing entirely."],
        ["return_request"],
        ["damaged", "broken", "smashed", "defective", "scratched"],
        ["wrong", "incorrect"],
        "MERGE (with wrong_item -> issue_with_received_item)"
    ),
    IntentDefinition(
        "return_request", "Return Request", "Customer wants to return an item.",
        ["Customer asks how to return an item or requests a return label."],
        ["Customer is only asking for a refund without returning (e.g. for a digital service)."],
        ["refund_request", "wrong_item", "damaged_item"],
        ["return", "returning", "send back", "return label"],
        ["refund"],
        "KEEP"
    ),
    IntentDefinition(
        "refund_request", "Refund Request", "Customer is asking for a refund or money back.",
        ["Customer asks for a refund, credits, or questions a charge."],
        ["Customer is initiating a physical return (which implies a refund)."],
        ["return_request", "cancel_order"],
        ["refund", "money back", "charged", "credit"],
        ["return", "label"],
        "KEEP"
    ),
    IntentDefinition(
        "cancel_order", "Cancel Order", "Customer wants to cancel an order.",
        ["Customer wants to cancel an order that hasn't shipped yet."],
        ["Customer wants to return an order that already arrived.", "Customer wants to cancel Prime membership."],
        ["refund_request", "return_request", "account_prime"],
        ["cancel order", "cancel my order", "cancelled by mistake"],
        ["prime", "membership", "return"],
        "KEEP"
    ),
    IntentDefinition(
        "account_prime", "Account & Prime", "Issues related to account access or Prime membership.",
        ["Login, password, account lockouts, Prime membership cancellation or benefits."],
        ["General website navigation issues not tied to account access."],
        ["cancel_order", "technical_issue"],
        ["account", "password", "login", "locked", "prime membership", "cancel prime"],
        ["cancel order"],
        "KEEP"
    ),
    IntentDefinition(
        "technical_issue", "Technical Issue", "Issues with Amazon app, website, or digital devices.",
        ["App crashes, website errors, Kindle, Fire TV, or Alexa issues."],
        ["Account lockouts (Account & Prime)."],
        ["account_prime"],
        ["app", "website", "error", "glitch", "kindle", "fire tv", "alexa"],
        ["password", "locked"],
        "KEEP"
    ),
    IntentDefinition(
        "gift_card_promotion", "Gift Card & Promotion", "Issues with gift cards, promotional codes, or discounts.",
        ["Claim codes not working, missing promotional discounts, gift card balances."],
        ["Regular refunds to credit cards."],
        ["refund_request"],
        ["gift card", "promo code", "claim code", "discount"],
        [],
        "KEEP"
    )
]

def find_matches(messages: List[str], intent: IntentDefinition) -> Tuple[List[str], List[str]]:
    """Find strong matches and false positive candidates based on boundaries."""
    strong_matches = []
    false_positives = []
    
    for msg in messages:
        msg_lower = msg.lower()
        if any(kw in msg_lower for kw in intent.keywords):
            # If it has negation words, it's a likely false positive for this specific intent boundary
            if any(neg in msg_lower for neg in intent.negations):
                false_positives.append(msg)
            else:
                strong_matches.append(msg)
                
    return strong_matches, false_positives

# ── Main ───────────────────────────────────────────────────────────────────

def main():
    import io
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        
    if not IN_JSONL.exists():
        print(f"ERROR: {IN_JSONL} not found"); sys.exit(1)
        
    print(f"Reading conversations from {IN_JSONL}...")
    conversations = []
    with open(IN_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                conversations.append(json.loads(line))
                
    messages = extract_customer_messages(conversations)
    print(f"Found {len(messages):,} valid unique customer support messages.")
    
    # Deterministic sampling for speed and reproducibility (50k for good coverage)
    rng = random.Random(SEED)
    sample_size = min(50000, len(messages))
    sampled_messages = rng.sample(messages, sample_size)
    
    print("Evaluating operational boundaries against candidate intents...")
    
    assigned_indices = set()
    taxonomy_out = []
    
    for intent in INTENTS:
        strong, false_pos = find_matches(sampled_messages, intent)
        
        # Keep track of assigned messages
        strong_unassigned = []
        for s in strong:
            if s not in assigned_indices:
                strong_unassigned.append(s)
                assigned_indices.add(s)
                
        rng.shuffle(strong_unassigned)
        rng.shuffle(false_pos)
        
        estimated_prevalence = len(strong_unassigned) / sample_size
        
        taxonomy_out.append({
            "intent_id": intent.id,
            "name": intent.name,
            "description": intent.description,
            "in_scope": intent.in_scope,
            "out_of_scope": intent.out_of_scope,
            "representative_examples": strong_unassigned[:15],
            "false_positive_examples": false_pos[:5],
            "confusable_intents": intent.confusions,
            "estimated_prevalence": estimated_prevalence,
            "recommended_action": intent.action,
            "total_matches": len(strong_unassigned)
        })

    # Calculate Other
    other_count = sample_size - len(assigned_indices)
    other_examples = [msg for msg in sampled_messages if msg not in assigned_indices]
    rng.shuffle(other_examples)
    
    taxonomy_out.append({
        "intent_id": "other_or_unclear",
        "name": "Other / Unclear",
        "description": "Messages that do not confidently fit into any strictly defined operational intent.",
        "in_scope": ["Ambiguous complaints, multi-intent requests lacking a primary focus, highly specific outliers."],
        "out_of_scope": ["Clear, actionable requests covered by specific intents."],
        "representative_examples": other_examples[:15],
        "false_positive_examples": [],
        "confusable_intents": [],
        "estimated_prevalence": other_count / sample_size,
        "recommended_action": "KEEP",
        "total_matches": other_count
    })
    
    # Output JSON
    output_json = {
        "version": "0.1",
        "status": "human_review_required",
        "intents": taxonomy_out
    }
    
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=2, ensure_ascii=False)
        
    # Write Markdown Report
    md = [
        "# SupportProof Taxonomy Review",
        "\n**PROPOSED TAXONOMY — REQUIRES HUMAN REVIEW**",
        "\n## Why Previous Approaches Were Rejected",
        "- **V1 (TF-IDF + K-Means)**: Grouped messages purely by shared words rather than meaning (e.g. 'Account Issue' absorbed anything with the word 'account'). Resulted in ~49% of data marked 'Other' and semantically incoherent clusters.",
        "- **V2 (Semantic Concept Features)**: A step up, grouping by operational concepts (delay, return, refund). However, it forced overlapping issues together and lacked strict operational boundaries, resulting in ~50% 'Other' and false positives in overlapping categories (e.g., late deliveries clustered with lost deliveries).",
        "\n## Operational Taxonomy Approach (V3)",
        "This taxonomy is built strictly on *operational boundaries*. A message is assigned to an intent only if a human agent would perform a distinctly different workflow to resolve it.",
        f"\n**Total Analyzed Sample:** {sample_size:,}",
        f"**Estimated Coverage:** {100 - (other_count/sample_size)*100:.1f}%",
        f"**Other / Unclear:** {(other_count/sample_size)*100:.1f}%",
        "\n## Detailed Taxonomy Definitions\n"
    ]
    
    for t in taxonomy_out:
        md.append(f"### {t['name']} (`{t['intent_id']}`)")
        md.append(f"- **Estimated Prevalence**: {t['estimated_prevalence']*100:.1f}%")
        md.append(f"- **Recommended Action**: **{t['recommended_action']}**")
        if t['recommended_action'].startswith("MERGE"):
            md.append("  - *Rationale*: Differentiating between a wrong item and a damaged item usually leads to the exact same support workflow (replace or refund).")
        md.append(f"- **Description**: {t['description']}")
        md.append("- **IN SCOPE**:")
        for item in t['in_scope']:
            md.append(f"  - {item}")
        md.append("- **OUT OF SCOPE**:")
        for item in t['out_of_scope']:
            md.append(f"  - {item}")
        md.append(f"- **Confusable Intents**: {', '.join(t['confusable_intents']) if t['confusable_intents'] else 'None'}")
        
        md.append("\n**Representative Examples:**")
        for ex in t['representative_examples'][:5]: # Only show 5 in markdown for brevity, JSON has 15
            clean_ex = ex.replace('\n', ' ').strip()
            md.append(f"- \"{clean_ex}\"")
            
        if t['false_positive_examples']:
            md.append("\n**Ambiguous / False Positive Candidates:**")
            for ex in t['false_positive_examples'][:3]:
                clean_ex = ex.replace('\n', ' ').strip()
                md.append(f"- \"{clean_ex}\"")
        md.append("\n---\n")
        
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(md), encoding="utf-8")
    
    # Console output
    print("\n=======================================================")
    print("TAXONOMY PROPOSAL GENERATED (HUMAN REVIEW REQUIRED)")
    print("=======================================================\n")
    print(f"Total Coverage: {100 - (other_count/sample_size)*100:.1f}% (Other: {(other_count/sample_size)*100:.1f}%)\n")
    
    for t in taxonomy_out:
        print(f"[{t['recommended_action']}] {t['name']} ({t['estimated_prevalence']*100:.1f}%)")
        
    print(f"\nFull JSON proposal saved to {OUT_JSON}")
    print(f"Markdown report saved to {REPORT}")

if __name__ == "__main__":
    main()
