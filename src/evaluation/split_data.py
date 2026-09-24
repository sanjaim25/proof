"""
Split AmazonHelp conversations into Development and Validation sets,
excluding the Golden Set.
"""

import json
import random
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
RAW_JSONL = WORKSPACE / "data" / "processed" / "amazonhelp_conversations.jsonl"
GOLDEN_CSV = WORKSPACE / "data" / "golden" / "golden_set_v1.csv"

OUT_DEV = WORKSPACE / "data" / "processed" / "development_conversation_ids.txt"
OUT_VAL = WORKSPACE / "data" / "processed" / "validation_conversation_ids.txt"
OUT_GOLDEN = WORKSPACE / "data" / "processed" / "golden_conversation_ids.txt"

SEED = 42

def normalize_text(text: str) -> str:
    import re
    t = text.lower()
    t = re.sub(r'@\w+', '', t)
    t = re.sub(r'http\S+', '', t)
    t = re.sub(r'[^a-z0-9]', '', t)
    return t

def main():
    if not RAW_JSONL.exists() or not GOLDEN_CSV.exists():
        print("Required data files not found.")
        sys.exit(1)

    golden_ids = set()
    golden_texts = set()
    import csv
    with open(GOLDEN_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            golden_ids.add(row["conversation_id"])
            golden_texts.add(normalize_text(row["customer_message"]))

    all_conv_ids = set()
    leakage_conv_ids = set()
    
    with open(RAW_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                conv = json.loads(line)
                cid = conv["conversation_id"]
                all_conv_ids.add(cid)
                
                # Check for exact text leakage
                for turn in conv.get("turns", []):
                    if turn.get("speaker") == "customer":
                        norm = normalize_text(turn.get("text", ""))
                        if norm in golden_texts:
                            leakage_conv_ids.add(cid)

    # Exclude golden AND any conversation with text leakage
    remaining_ids = sorted(list(all_conv_ids - golden_ids - leakage_conv_ids))
    
    rng = random.Random(SEED)
    rng.shuffle(remaining_ids)

    split_idx = int(len(remaining_ids) * 0.8)
    dev_ids = remaining_ids[:split_idx]
    val_ids = remaining_ids[split_idx:]

    print(f"Total conversations: {len(all_conv_ids)}")
    print(f"Golden (exact IDs): {len(golden_ids)}")
    print(f"Excluded due to text leakage: {len(leakage_conv_ids - golden_ids)}")
    print(f"Development (80%): {len(dev_ids)}")
    print(f"Validation (20%): {len(val_ids)}")

    # Write out
    OUT_DEV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_DEV, "w", encoding="utf-8") as f:
        for cid in dev_ids:
            f.write(cid + "\n")

    with open(OUT_VAL, "w", encoding="utf-8") as f:
        for cid in val_ids:
            f.write(cid + "\n")

    with open(OUT_GOLDEN, "w", encoding="utf-8") as f:
        for cid in golden_ids:
            f.write(cid + "\n")
            
    print("Exported IDs successfully.")

if __name__ == "__main__":
    main()
