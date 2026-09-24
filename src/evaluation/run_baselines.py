"""
Run Baseline Evaluation.
Evaluates Majority and TF-IDF baselines on the frozen Golden Set V1.
Generates metrics and reports.
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

from src.evaluation.baseline_majority import MajorityBaseline
from src.evaluation.baseline_tfidf import TFIDFBaseline

WORKSPACE = Path(__file__).resolve().parents[2]
GOLDEN_CSV = WORKSPACE / "data" / "golden" / "golden_set_v1.csv"
REPORT_MD = WORKSPACE / "reports" / "baseline_results.md"

VALID_INTENTS = [
    "technical_issue", "refund_request", "delivery_delay", "account_prime",
    "order_tracking", "return_request", "issue_with_received_item",
    "missing_delivery", "gift_card_promotion", "cancel_order", "other_or_unclear"
]

def compute_metrics(y_true, y_pred, labels):
    """Compute precision, recall, f1 per class and macro."""
    metrics = {}
    total_tp = 0
    total_fp = 0
    total_fn = 0
    
    for label in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)
        
        total_tp += tp
        total_fp += fp
        total_fn += fn
        
        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
        
        metrics[label] = {"precision": p, "recall": r, "f1": f1, "support": tp + fn}
        
    # Macro F1
    macro_f1 = sum(m["f1"] for m in metrics.values()) / len(labels)
    # Weighted F1
    total_support = sum(m["support"] for m in metrics.values())
    weighted_f1 = sum(m["f1"] * m["support"] for m in metrics.values()) / total_support if total_support > 0 else 0.0
    # Accuracy
    acc = sum(1 for t, p in zip(y_true, y_pred) if t == p) / len(y_true) if y_true else 0.0
    
    return {
        "per_class": metrics,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "accuracy": acc
    }

def compute_binary_metrics(y_true, y_pred):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t and p)
    tn = sum(1 for t, p in zip(y_true, y_pred) if not t and not p)
    fp = sum(1 for t, p in zip(y_true, y_pred) if not t and p)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t and not p)
    
    acc = (tp + tn) / len(y_true) if y_true else 0.0
    p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    
    return {
        "accuracy": acc,
        "precision": p,
        "recall": r,
        "f1": f1,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn
    }

def main():
    print("Loading Golden Set...")
    golden_examples = []
    with open(GOLDEN_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            golden_examples.append(row)
            
    print(f"Loaded {len(golden_examples)} evaluation examples.")
    
    print("Fitting Majority Baseline...")
    majority = MajorityBaseline()
    majority.fit()
    
    print("Fitting TF-IDF Baseline (this may take a moment)...")
    tfidf = TFIDFBaseline(k=3, threshold=0.1)
    tfidf.fit()
    
    print("Evaluating models...")
    
    results = {
        "Majority": {"intent_true": [], "intent_pred": [], "esc_true": [], "esc_pred": [], "replies": [], "examples": []},
        "TF-IDF": {"intent_true": [], "intent_pred": [], "esc_true": [], "esc_pred": [], "replies": [], "examples": []}
    }
    
    for ex in golden_examples:
        text = ex["customer_message"]
        true_intent = ex["human_intent"]
        true_esc = ex["human_escalate"] in ("True", "Yes", "true")
        
        # Majority
        maj_pred = majority.predict(text)
        results["Majority"]["intent_true"].append(true_intent)
        results["Majority"]["intent_pred"].append(maj_pred["intent"])
        results["Majority"]["esc_true"].append(true_esc)
        results["Majority"]["esc_pred"].append(maj_pred["escalate"])
        results["Majority"]["replies"].append(maj_pred["reply"])
        
        # TF-IDF
        tf_pred = tfidf.predict(text)
        results["TF-IDF"]["intent_true"].append(true_intent)
        results["TF-IDF"]["intent_pred"].append(tf_pred["intent"])
        results["TF-IDF"]["esc_true"].append(true_esc)
        results["TF-IDF"]["esc_pred"].append(tf_pred["escalate"])
        results["TF-IDF"]["replies"].append(tf_pred["reply"])
        results["TF-IDF"]["examples"].append({
            "text": text,
            "true_intent": true_intent,
            "pred_intent": tf_pred["intent"],
            "sim": tf_pred["retrieval_similarity"],
            "reply": tf_pred["reply"]
        })
        
    print("Calculating metrics...")
    
    metrics = {}
    for name in ["Majority", "TF-IDF"]:
        intent_m = compute_metrics(results[name]["intent_true"], results[name]["intent_pred"], VALID_INTENTS)
        esc_m = compute_binary_metrics(results[name]["esc_true"], results[name]["esc_pred"])
        metrics[name] = {"intent": intent_m, "escalate": esc_m}
        
    # Generate Report
    print(f"Generating {REPORT_MD}...")
    
    md = [
        "# Baseline Evaluation Results",
        f"Evaluated on {len(golden_examples)} frozen golden examples.\n",
        "## Summary Metrics\n",
        "| System | Intent Accuracy | Intent Macro-F1 | Escalation Precision | Escalation Recall | Escalation F1 |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |"
    ]
    
    for name in ["Majority", "TF-IDF"]:
        m = metrics[name]
        md.append(f"| {name} | {m['intent']['accuracy']:.3f} | {m['intent']['macro_f1']:.3f} | {m['escalate']['precision']:.3f} | {m['escalate']['recall']:.3f} | {m['escalate']['f1']:.3f} |")
        
    # TF-IDF Qualitative Analysis
    tf_ex = results["TF-IDF"]["examples"]
    below_thresh = sum(1 for e in tf_ex if e["sim"] < tfidf.threshold)
    intent_diff = sum(1 for e in tf_ex if e["true_intent"] != e["pred_intent"])
    
    md.extend([
        "\n## TF-IDF Retrieval Analysis",
        f"- **Below threshold ({tfidf.threshold})**: {below_thresh} ({below_thresh/len(tf_ex)*100:.1f}%)",
        f"- **Incorrect Intent**: {intent_diff} ({intent_diff/len(tf_ex)*100:.1f}%)",
    ])
    
    md.extend(["\n### Successful Retrievals (Examples)"])
    successes = [e for e in tf_ex if e["true_intent"] == e["pred_intent"] and e["true_intent"] != "other_or_unclear"]
    for i, e in enumerate(successes[:3]):
        md.append(f"**Example {i+1}**")
        md.append(f"- **Customer**: {e['text']}")
        md.append(f"- **Intent**: {e['pred_intent']} (Sim: {e['sim']:.3f})")
        md.append(f"- **Baseline Reply**: {e['reply']}\n")
        
    md.extend(["\n### Failed Retrievals (Examples)"])
    failures = [e for e in tf_ex if e["true_intent"] != e["pred_intent"] and e["true_intent"] != "other_or_unclear"]
    for i, e in enumerate(failures[:3]):
        md.append(f"**Example {i+1}**")
        md.append(f"- **Customer**: {e['text']}")
        md.append(f"- **True Intent**: {e['true_intent']}")
        md.append(f"- **Predicted Intent**: {e['pred_intent']} (Sim: {e['sim']:.3f})\n")

    md.extend([
        "\n## Limitations",
        "- The Majority Baseline is trivial and entirely lacks context awareness.",
        "- The TF-IDF baseline suffers from lexical mismatch (e.g. synonyms aren't matched).",
        "- TF-IDF relies heavily on heuristic 'silver' labels applied to historical data, capping its theoretical maximum performance.",
        "- Escalation heuristics based on historical conversation length are extremely noisy proxies for actual escalation requirements."
    ])

    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    # Console Output as requested
    print("\n=======================================================")
    print("BASELINE EVALUATION RESULTS")
    print("=======================================================\n")
    
    print("1. Majority Baseline Results:")
    print(f"   - Intent Accuracy: {metrics['Majority']['intent']['accuracy']:.3f}")
    print(f"   - Intent Macro-F1: {metrics['Majority']['intent']['macro_f1']:.3f}")
    
    print("\n2. TF-IDF Baseline Results:")
    print(f"   - Intent Accuracy: {metrics['TF-IDF']['intent']['accuracy']:.3f}")
    print(f"   - Intent Macro-F1: {metrics['TF-IDF']['intent']['macro_f1']:.3f}")
    
    print(f"\n3. Intent Macro-F1: Majority={metrics['Majority']['intent']['macro_f1']:.3f}, TF-IDF={metrics['TF-IDF']['intent']['macro_f1']:.3f}")
    
    print("\n4. Escalation (P/R/F1):")
    em = metrics['Majority']['escalate']
    et = metrics['TF-IDF']['escalate']
    print(f"   - Majority: P={em['precision']:.3f}, R={em['recall']:.3f}, F1={em['f1']:.3f}")
    print(f"   - TF-IDF:   P={et['precision']:.3f}, R={et['recall']:.3f}, F1={et['f1']:.3f}")
    
    print(f"\n5. Number of golden examples evaluated: {len(golden_examples)}")
    print("\n6. Leakage check must be run separately via `python -m src.evaluation.check_leakage`.")
    
    print("\n7. Three Successful Retrievals:")
    for i, e in enumerate(successes[:3]):
        print(f"   [{e['pred_intent']}] {e['text'][:60]}...")
        
    print("\n8. Three Failed Retrievals:")
    for i, e in enumerate(failures[:3]):
        print(f"   [Pred: {e['pred_intent']}, True: {e['true_intent']}] {e['text'][:60]}...")

if __name__ == "__main__":
    main()
