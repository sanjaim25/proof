"""
Verify zero leakage between Golden, Development, and Validation sets.
"""

import csv
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
IN_JSONL = WORKSPACE / "data" / "processed" / "amazonhelp_conversations.jsonl"
GOLDEN_CSV = WORKSPACE / "data" / "golden" / "golden_set_v1.csv"
DEV_IDS = WORKSPACE / "data" / "processed" / "development_conversation_ids.txt"
VAL_IDS = WORKSPACE / "data" / "processed" / "validation_conversation_ids.txt"

def normalize_text(text: str) -> str:
    import re
    t = text.lower()
    t = re.sub(r'@\w+', '', t)
    t = re.sub(r'http\S+', '', t)
    t = re.sub(r'[^a-z0-9]', '', t)
    return t

def check_leakage():
    if not all(p.exists() for p in [GOLDEN_CSV, DEV_IDS, VAL_IDS, IN_JSONL]):
        print("Missing required files for leakage check. Run split_data.py first.")
        sys.exit(1)

    golden_conv_ids = set()
    golden_messages = set()
    
    with open(GOLDEN_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            golden_conv_ids.add(row["conversation_id"])
            golden_messages.add(normalize_text(row["customer_message"]))

    with open(DEV_IDS, "r", encoding="utf-8") as f:
        dev_ids = set(line.strip() for line in f if line.strip())

    with open(VAL_IDS, "r", encoding="utf-8") as f:
        val_ids = set(line.strip() for line in f if line.strip())

    errors = []

    # 1. No golden in dev
    overlap_dev = golden_conv_ids.intersection(dev_ids)
    if overlap_dev:
        errors.append(f"LEAKAGE: {len(overlap_dev)} golden conversations found in DEVELOPMENT.")

    # 2. No golden in val
    overlap_val = golden_conv_ids.intersection(val_ids)
    if overlap_val:
        errors.append(f"LEAKAGE: {len(overlap_val)} golden conversations found in VALIDATION.")

    # 3. No dev in val
    overlap_dev_val = dev_ids.intersection(val_ids)
    if overlap_dev_val:
        errors.append(f"LEAKAGE: {len(overlap_dev_val)} conversations overlap between DEV and VAL.")

    # Check for text leakage in DEV
    dev_text_leakage = 0
    with open(IN_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                conv = json.loads(line)
                if conv["conversation_id"] in dev_ids:
                    for turn in conv.get("turns", []):
                        if turn.get("speaker") == "customer":
                            norm = normalize_text(turn.get("text", ""))
                            if norm in golden_messages:
                                dev_text_leakage += 1

    # 4 & 5. No exact golden customer message appears in dev/retrieval corpus
    if dev_text_leakage > 0:
        errors.append(f"LEAKAGE: {dev_text_leakage} exact golden messages found in DEVELOPMENT.")

    if errors:
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print("LEAKAGE CHECK PASSED: 0 Golden examples leaked.")

if __name__ == "__main__":
    check_leakage()
