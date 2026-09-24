"""
Evaluate the SupportProof Agent against the frozen Golden Set V1.
"""

import csv
import json
import sys
from pathlib import Path
from collections import defaultdict

from src.agent.agent import SupportProofAgent, VALID_INTENTS
from src.agent.schemas import AgentRequest, Turn
from src.evaluation.run_baselines import compute_metrics, compute_binary_metrics

WORKSPACE = Path(__file__).resolve().parents[2]
GOLDEN_CSV = WORKSPACE / "data" / "golden" / "golden_set_v1.csv"
OUT_PREDICTIONS = WORKSPACE / "data" / "processed" / "agent_predictions_v1.1.jsonl"
METADATA_JSON = WORKSPACE / "data" / "processed" / "agent_evaluation_metadata_v1.1.json"
REPORT_MD = WORKSPACE / "reports" / "agent_results_v1.1.md"

PILOT_IDS = [
    "gold_0102", "gold_0122", "gold_0003", "gold_0137", "gold_0131",
    "gold_0014", "gold_0129", "gold_0159", "gold_0031", "gold_0160",
    "gold_0077", "gold_0107", "gold_0096", "gold_0004", "gold_0016",
    "gold_0111", "gold_0171", "gold_0195", "gold_0173", "gold_0114"
]

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate the SupportProof Agent")
    parser.add_argument("--resume", action="store_true", help="Resume from an existing checkpoint")
    parser.add_argument("--pilot", action="store_true", help="Run the 20-example pilot instead of the full benchmark")
    args = parser.parse_args()
    
    global OUT_PREDICTIONS, METADATA_JSON, REPORT_MD
    if args.pilot:
        OUT_PREDICTIONS = WORKSPACE / "data" / "processed" / "pilot_predictions_v1.1.jsonl"
        METADATA_JSON = WORKSPACE / "data" / "processed" / "pilot_evaluation_metadata_v1.1.json"
        REPORT_MD = WORKSPACE / "reports" / "pilot_results_v1.1.md"

    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    import os
    # Default to open source model for this benchmark
    model_name = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
    k = 2
    threshold = 0.55

    print("Loading Golden Set...")
    golden_examples = []
    with open(GOLDEN_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse context if stored as "turn | turn"
            context_raw = row.get("previous_turns", "")
            turns = []
            if context_raw:
                for t in context_raw.split(" | "):
                    if t.strip():
                        # Just a simple heuristic for testing context, we assume it's brand->customer alternating
                        turns.append(Turn(speaker="brand", text=t.strip()))
            
            golden_examples.append({
                "example_id": row["example_id"],
                "customer_message": row["customer_message"],
                "context": turns,
                "true_intent": row["human_intent"],
                "true_esc": row["human_escalate"] in ("True", "Yes", "true")
            })

    if args.pilot:
        print("Filtering to 20 pilot examples...")
        golden_examples = [g for g in golden_examples if g["example_id"] in PILOT_IDS]
        # Sort them in the exact order of PILOT_IDS for consistency
        id_to_g = {g["example_id"]: g for g in golden_examples}
        golden_examples = [id_to_g[eid] for eid in PILOT_IDS if eid in id_to_g]
        print("Pilot Example IDs:")
        for g in golden_examples:
            print(f" - {g['example_id']}")

    print("Initializing Agent v1.1 (loading corpus, fitting TF-IDF)...")
    # Using specific configurable thresholds
    agent = SupportProofAgent(k=2, sim_threshold=0.55)
    agent.retriever.fit()
    
    predictions = []
    completed_ids = set()
    
    if args.resume:
        if not OUT_PREDICTIONS.exists() or not METADATA_JSON.exists():
            print("Cannot resume: checkpoint or metadata file not found.")
            sys.exit(1)
            
        with open(METADATA_JSON, "r", encoding="utf-8") as f:
            meta = json.load(f)
            assert meta["model"] == model_name, f"Model mismatch: {meta['model']} vs {model_name}"
            assert meta["k"] == k, f"K mismatch: {meta['k']} vs {k}"
            assert meta["threshold"] == threshold, f"Threshold mismatch: {meta['threshold']} vs {threshold}"
            
        with open(OUT_PREDICTIONS, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                p = json.loads(line)
                predictions.append(p)
                completed_ids.add(p["example_id"])
                
        print(f"Resuming from checkpoint. {len(completed_ids)} examples already completed.")
    else:
        if OUT_PREDICTIONS.exists():
            print("Checkpoint exists. Use --resume to continue or delete the file to start fresh.")
            sys.exit(1)
            
        METADATA_JSON.parent.mkdir(parents=True, exist_ok=True)
        with open(METADATA_JSON, "w", encoding="utf-8") as f:
            json.dump({
                "model": model_name,
                "k": k,
                "threshold": threshold,
                "golden_set": "golden_set_v1.csv"
            }, f)
            
    print(f"Running evaluation on {len(golden_examples)} examples. This will take time (API rate limits apply)...")
    
    api_failures_this_run = 0
    api_failure_details = []
    rate_limit_hit = False
    
    # Open prediction file in append mode to save incrementally
    OUT_PREDICTIONS.parent.mkdir(parents=True, exist_ok=True)
    out_file = open(OUT_PREDICTIONS, "a", encoding="utf-8")
    
    try:
        for i, ex in enumerate(golden_examples, 1):
            if ex["example_id"] in completed_ids:
                continue
                
            print(f"Processing {i}/{len(golden_examples)}...", end="\r", flush=True)
            req = AgentRequest(
                customer_message=ex["customer_message"],
                conversation_context=ex["context"]
            )
            
            # NOTE: Agent NEVER sees the human label
            res = agent.process(req)
            
            pred_record = {
                "example_id": ex["example_id"],
                "true_intent": ex["true_intent"],
                "true_esc": ex["true_esc"],
                "predicted_intent": res.get("intent", ""),
                "intent_confidence": res.get("intent_confidence", 0.0),
                "predicted_reply": res.get("reply", ""),
                "predicted_escalate": res.get("escalate", False),
                "predicted_escalation_reason": res.get("escalation_reason", ""),
                "evidence": res.get("evidence", []),
                "retrieval_scores": res.get("retrieval_scores", []),
                "validation_failures": res.get("validation_failures", []),
                "api_error": res.get("api_error"),
                "retrieval_confidence": res.get("retrieval_confidence", "weak")
            }
            
            if res.get("api_error"):
                api_failures_this_run += 1
                err_str = str(res["api_error"]).lower()
                api_failure_details.append(f"Ex {ex['example_id']}: {res['api_error']}")
                
                # If rate limit, break the loop and don't save to JSONL
                if "429" in err_str or "rate limit" in err_str:
                    print(f"\nRate limit encountered at example {ex['example_id']}. Aborting remaining examples for this run.")
                    rate_limit_hit = True
                    break
            
            # Write to JSONL atomically
            predictions.append(pred_record)
            completed_ids.add(ex["example_id"])
            out_file.write(json.dumps(pred_record) + "\n")
            out_file.flush()
            import os
            os.fsync(out_file.fileno())
            
    finally:
        out_file.close()

    print(f"\nCompleted evaluation phase. (Successful/Total Predictions: {len(predictions)}/{len(golden_examples)})")

    # Reconstruct metrics from ALL predictions (including those loaded from checkpoint)
    intent_true = []
    intent_pred = []
    esc_true = []
    esc_pred = []
    validation_failures = 0
    
    from collections import Counter
    retrieval_confidences = Counter()
    total_api_failures_in_checkpoint = 0
    
    for p in predictions:
        if p.get("api_error"):
            total_api_failures_in_checkpoint += 1
            continue
            
        intent_true.append(p["true_intent"])
        intent_pred.append(p["predicted_intent"])
        esc_true.append(p["true_esc"])
        esc_pred.append(p["predicted_escalate"])
        
        if p.get("retrieval_confidence"):
            retrieval_confidences[p["retrieval_confidence"]] += 1
            
        if p.get("validation_failures") and "LLM Error" not in p.get("validation_failures"):
            validation_failures += 1

    print("Calculating metrics...")
    if len(intent_true) > 0:
        intent_m = compute_metrics(intent_true, intent_pred, list(VALID_INTENTS))
        esc_m = compute_binary_metrics(esc_true, esc_pred)
        
        fp = esc_m["fp"]
        tn = esc_m["tn"]
        fn = esc_m["fn"]
        tp = esc_m["tp"]
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    else:
        intent_m = {"accuracy": 0, "macro_f1": 0, "weighted_f1": 0}
        esc_m = {"precision": 0, "recall": 0, "f1": 0}
        fpr = 0.0
        fnr = 0.0

    print(f"Generating {REPORT_MD}...")
    
    is_complete_run = (len(predictions) == len(golden_examples)) and not rate_limit_hit
    run_status = "Complete 200-Example Benchmark" if is_complete_run else f"Partial Run ({len(predictions)}/{len(golden_examples)} completed)"
    
    md = [
        f"# SupportProof Agent v1.1 Evaluation Results - {run_status}\n",
        "**Version Tracking:**",
        f"- Model: {model_name}",
        f"- Retrieval K: {k}",
        f"- Retrieval Threshold: {threshold}",
        f"- Golden Set Size: {len(golden_examples)}",
        f"- Processed Checkpoint Size: {len(predictions)}",
        f"- Successful API Predictions: {len(intent_true)}",
        f"- API Errors in Checkpoint: {total_api_failures_in_checkpoint}",
        f"- Rate Limit Hit This Run: {rate_limit_hit}",
        "\n## Comparison to Baselines (On Successful Predictions)\n",
        "| System | Intent Accuracy | Intent Macro-F1 | Esc Precision | Esc Recall | Esc F1 |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
        "| Majority | 0.320 | 0.044 | 0.000 | 0.000 | 0.000 |",
        "| TF-IDF Baseline | 0.320 | 0.252 | 0.286 | 0.240 | 0.261 |",
        f"| **Agent v1.1** | **{intent_m['accuracy']:.3f}** | **{intent_m['macro_f1']:.3f}** | **{esc_m['precision']:.3f}** | **{esc_m['recall']:.3f}** | **{esc_m['f1']:.3f}** |",
        "\n## Agent v1.1 Detailed Metrics",
        f"- **Intent Weighted-F1**: {intent_m['weighted_f1']:.3f}",
        f"- **False Escalation Rate (FPR)**: {fpr:.3f}",
        f"- **Missed Escalation Rate (FNR)**: {fnr:.3f}",
        "\n## Grounding & Retrieval",
        f"- **Validation Failures**: {validation_failures} examples triggered deterministic safety overrides",
        f"- **Retrieval Confidence Distribution**: Strong: {retrieval_confidences['strong']}, Moderate: {retrieval_confidences['moderate']}, Weak: {retrieval_confidences['weak']}",
    ]
    
    md.append("\n## API / Evaluation Failures (This Run)")
    if api_failures_this_run == 0:
        md.append("None.")
    else:
        for fail in api_failure_details[:10]:
            md.append(f"- {fail}")
        if len(api_failure_details) > 10:
            md.append(f"- ... and {len(api_failure_details) - 10} more.")
    
    md.append("\n## Examples")
    
    successes = [p for p in predictions if not p.get("api_error") and p["true_intent"] == p["predicted_intent"] and not p["validation_failures"]]
    md.append("### Successful Examples")
    for i, p in enumerate(successes[:3]):
        md.append(f"**Example {i+1} ({p['predicted_intent']})**")
        md.append(f"> Reply: {p['predicted_reply']}\n")
        
    intent_fails = [p for p in predictions if not p.get("api_error") and p["true_intent"] != p["predicted_intent"]]
    md.append("### Intent Failures")
    for i, p in enumerate(intent_fails[:3]):
        md.append(f"**Example {i+1}**")
        md.append(f"- True: `{p['true_intent']}` | Predicted: `{p['predicted_intent']}`")
        
    esc_fails = [p for p in predictions if not p.get("api_error") and p["true_esc"] and not p["predicted_escalate"]]
    md.append("\n### Missed Escalations (Should have escalated, didn't)")
    for i, p in enumerate(esc_fails[:3]):
        md.append(f"**Example {i+1}**")
        md.append(f"- True Intent: `{p['true_intent']}`")
        md.append(f"> Agent Reply: {p['predicted_reply']}")
        
    val_fails = [p for p in predictions if not p.get("api_error") and p["validation_failures"]]
    md.append("\n### Grounding Validation Failures")
    for i, p in enumerate(val_fails[:3]):
        md.append(f"**Example {i+1}**")
        md.append(f"- Violations: {', '.join(p['validation_failures'])}")
        
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print("\n=======================================================")
    print("AGENT V1.1 EVALUATION COMPLETE")
    print("=======================================================")
    print(f"Status: {run_status}")
    print(f"Total golden examples: {len(golden_examples)}")
    print(f"Successfully evaluated examples (across all runs): {len(intent_true)}")
    print(f"API Errors preserved in checkpoint: {total_api_failures_in_checkpoint}")
    if rate_limit_hit:
        print("WARNING: Run was aborted early due to API rate limit.")
    print("---")
    if len(intent_true) > 0:
        print(f"1. Agent intent accuracy: {intent_m['accuracy']:.3f}")
        print(f"2. Agent intent macro-F1: {intent_m['macro_f1']:.3f}")
        print(f"3. Agent escalation precision: {esc_m['precision']:.3f}")
        print(f"4. Agent escalation recall: {esc_m['recall']:.3f}")
        print(f"5. Agent escalation F1: {esc_m['f1']:.3f}")
    else:
        print("No successful predictions to compute metrics.")
    print("---")
    print(f"Report saved to: {REPORT_MD}")

if __name__ == "__main__":
    main()
