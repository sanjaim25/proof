"""
Validate and Freeze SupportProof Golden Evaluation Set V1.
"""

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
WORKSPACE = Path(__file__).resolve().parents[2]
IN_JSONL  = WORKSPACE / "data" / "golden" / "golden_annotations.jsonl"
IN_CSV    = WORKSPACE / "data" / "golden" / "golden_set.csv"

FROZEN_JSONL = WORKSPACE / "data" / "golden" / "golden_set_v1.jsonl"
FROZEN_CSV   = WORKSPACE / "data" / "golden" / "golden_set_v1.csv"
REPORT       = WORKSPACE / "reports" / "golden_validation.md"

VALID_INTENTS = {
    "technical_issue",
    "refund_request",
    "delivery_delay",
    "account_prime",
    "order_tracking",
    "return_request",
    "issue_with_received_item",
    "missing_delivery",
    "gift_card_promotion",
    "cancel_order",
    "other_or_unclear"
}

REQUIRED_FIELDS = {
    "example_id",
    "conversation_id",
    "customer_message",
    "human_intent",
    "human_escalate"
}

def normalize_text(text: str) -> str:
    """Normalize for deduplication."""
    t = text.lower()
    t = re.sub(r'@\w+', '', t)
    t = re.sub(r'http\S+', '', t)
    t = re.sub(r'[^a-z0-9]', '', t)
    return t

def validate_data() -> dict:
    if not IN_JSONL.exists():
        raise FileNotFoundError(f"{IN_JSONL} not found.")

    records = []
    with open(IN_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    # Check 1: Exactly 200 examples
    if len(records) != 200:
        raise ValueError(f"Expected 200 examples, found {len(records)}.")

    example_ids = set()
    norm_messages = set()
    warnings = []

    intent_counts = defaultdict(int)
    escalate_counts = defaultdict(int)
    cross_tab = defaultdict(lambda: {"Yes": 0, "No": 0})

    for rec in records:
        # Check 2: Required fields
        missing = REQUIRED_FIELDS - set(rec.keys())
        if missing:
            raise ValueError(f"Example {rec.get('example_id')} missing fields: {missing}")

        # Check 3: Duplicate example IDs
        eid = rec["example_id"]
        if eid in example_ids:
            raise ValueError(f"Duplicate example_id: {eid}")
        example_ids.add(eid)

        # Check 4: Duplicate customer messages
        norm_msg = normalize_text(rec["customer_message"])
        if norm_msg in norm_messages:
            raise ValueError(f"Duplicate customer message in example: {eid}")
        norm_messages.add(norm_msg)

        # Check 5: Valid Intent
        intent = rec["human_intent"]
        if intent not in VALID_INTENTS:
            raise ValueError(f"Invalid intent '{intent}' in {eid}")
        
        # Check 6: Valid Escalate
        esc = rec["human_escalate"]
        if not isinstance(esc, bool) and esc not in ("Yes", "No", "true", "false", True, False):
            raise ValueError(f"Invalid escalate value '{esc}' in {eid}")

        # Normalize escalate to string 'Yes' / 'No' for reporting
        is_esc = esc in (True, "Yes", "true")
        esc_str = "Yes" if is_esc else "No"

        # Tally stats
        intent_counts[intent] += 1
        escalate_counts[esc_str] += 1
        cross_tab[intent][esc_str] += 1

        # Check 9: Warnings
        if is_esc and not rec.get("human_reason"):
            warnings.append(f"[{eid}] Escalate=Yes but human_reason is empty.")
        
        notes = rec.get("annotation_notes")
        if notes and len(notes.strip()) < 5:
            warnings.append(f"[{eid}] Annotation notes extremely short: '{notes}'")
            
        if intent == "other_or_unclear":
            warnings.append(f"[{eid}] Labeled as other_or_unclear (Requires review).")

        msg_len = len(rec["customer_message"].split())
        if msg_len < 3:
            warnings.append(f"[{eid}] Unusually short customer message ({msg_len} words).")
        elif msg_len > 100:
            warnings.append(f"[{eid}] Unusually long customer message ({msg_len} words).")

    stats = {
        "total": len(records),
        "intent_counts": intent_counts,
        "escalate_counts": escalate_counts,
        "cross_tab": cross_tab,
        "warnings": warnings,
        "records": records
    }
    
    return stats

def main():
    try:
        stats = validate_data()
    except Exception as e:
        print(f"Validation FAILED: {e}")
        sys.exit(1)

    print(f"Validation passed for {stats['total']} examples.")

    # 11. Freeze Data
    print(f"Freezing {FROZEN_JSONL}...")
    with open(FROZEN_JSONL, "w", encoding="utf-8") as f:
        for rec in stats["records"]:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Freezing {FROZEN_CSV}...")
    fieldnames = [
        "example_id", "conversation_id", "created_at", "customer_message", 
        "previous_turns", "brand_response", "candidate_intents",
        "human_intent", "human_escalate", "human_reason", "annotation_notes"
    ]
    with open(FROZEN_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in stats["records"]:
            csv_rec = rec.copy()
            if isinstance(csv_rec.get("previous_turns"), list):
                csv_rec["previous_turns"] = " | ".join(csv_rec["previous_turns"])
            if isinstance(csv_rec.get("candidate_intents"), list):
                csv_rec["candidate_intents"] = ", ".join(csv_rec["candidate_intents"])
            writer.writerow(csv_rec)

    # 10. Generate Report
    print(f"Generating {REPORT}...")
    total = stats["total"]
    
    md = [
        "# Golden Set V1 Validation Report\n",
        "## Overall Status: PASSED",
        f"- Total Examples: {total}\n",
        "## Intent Distribution",
        "| Intent | Count | % |",
        "| :--- | :---: | :---: |"
    ]
    
    for intent, count in sorted(stats["intent_counts"].items(), key=lambda x: x[1], reverse=True):
        pct = (count / total) * 100
        md.append(f"| {intent} | {count} | {pct:.1f}% |")

    md.extend([
        "\n## Escalation Distribution",
        "| Escalation | Count | % |",
        "| :--- | :---: | :---: |"
    ])
    
    for esc, count in stats["escalate_counts"].items():
        pct = (count / total) * 100
        md.append(f"| {esc} | {count} | {pct:.1f}% |")

    md.extend([
        "\n## Intent × Escalation Cross-Tabulation",
        "| Intent | Escalate Yes | Escalate No |",
        "| :--- | :---: | :---: |"
    ])
    
    for intent in sorted(VALID_INTENTS):
        if intent in stats["cross_tab"]:
            y = stats["cross_tab"][intent]["Yes"]
            n = stats["cross_tab"][intent]["No"]
            md.append(f"| {intent} | {y} | {n} |")
        else:
            md.append(f"| {intent} | 0 | 0 |")

    md.extend([
        "\n## Annotation Warnings",
        "The following examples passed structural validation but should be manually reviewed:"
    ])
    
    if not stats["warnings"]:
        md.append("- None")
    else:
        for w in stats["warnings"]:
            md.append(f"- {w}")
            
    md.extend([
        "\n## Dataset Limitations",
        "- The dataset inherits noise and truncation from the original Twitter Support corpus.",
        "- 'other_or_unclear' examples heavily depend on annotator judgment when context is missing.",
        "- Final evaluations must account for inherent ambiguity in short social media posts."
    ])

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    # Print to console
    print("\n=======================================================")
    print("GOLDEN SET V1 VALIDATION SUMMARY")
    print("=======================================================")
    print(f"1. Total examples: {total}")
    print("\n2. Final intent counts and percentages:")
    for intent, count in sorted(stats["intent_counts"].items(), key=lambda x: x[1], reverse=True):
        print(f"   - {intent}: {count} ({count/total*100:.1f}%)")
        
    print("\n3. Escalation Yes/No counts and percentages:")
    for esc, count in stats["escalate_counts"].items():
        print(f"   - {esc}: {count} ({count/total*100:.1f}%)")
        
    print("\n4. Intent × Escalation table:")
    print(f"   {'Intent':<30} | {'Yes':<5} | {'No':<5}")
    print("   " + "-"*46)
    for intent in sorted(VALID_INTENTS):
        y = stats["cross_tab"][intent]["Yes"]
        n = stats["cross_tab"][intent]["No"]
        print(f"   {intent:<30} | {y:<5} | {n:<5}")

    print("\n5. Annotation Warnings:")
    if not stats["warnings"]:
        print("   None.")
    else:
        for w in stats["warnings"][:10]:
            print(f"   {w}")
        if len(stats["warnings"]) > 10:
            print(f"   ... and {len(stats['warnings']) - 10} more warnings (see report).")

    print(f"\n6. Confirmation:")
    print(f"   [OK] Frozen JSONL created at: {FROZEN_JSONL}")
    print(f"   [OK] Frozen CSV created at:   {FROZEN_CSV}")
    print(f"   [OK] Report created at:       {REPORT}")

if __name__ == "__main__":
    main()
