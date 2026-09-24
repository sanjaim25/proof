# SupportProof Agent v1.1 Evaluation Results - Partial Run (3/20 completed)

**Version Tracking:**
- Model: openai/gpt-oss-20b
- Retrieval K: 2
- Retrieval Threshold: 0.55
- Golden Set Size: 20
- Processed Checkpoint Size: 3
- Successful API Predictions: 3
- API Errors in Checkpoint: 0
- Rate Limit Hit This Run: True

## Comparison to Baselines (On Successful Predictions)

| System | Intent Accuracy | Intent Macro-F1 | Esc Precision | Esc Recall | Esc F1 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Majority | 0.320 | 0.044 | 0.000 | 0.000 | 0.000 |
| TF-IDF Baseline | 0.320 | 0.252 | 0.286 | 0.240 | 0.261 |
| **Agent v1.1** | **0.667** | **0.073** | **0.000** | **0.000** | **0.000** |

## Agent v1.1 Detailed Metrics
- **Intent Weighted-F1**: 0.800
- **False Escalation Rate (FPR)**: 0.333
- **Missed Escalation Rate (FNR)**: 0.000

## Grounding & Retrieval
- **Validation Failures**: 0 examples triggered deterministic safety overrides
- **Retrieval Confidence Distribution**: Strong: 0, Moderate: 0, Weak: 3

## API / Evaluation Failures (This Run)
- Ex gold_0137: Error code: 429 - {'error': {'message': 'Rate limit reached for model `openai/gpt-oss-20b` in organization `org_01kfjem4g7fs9rr4zbbj335n2d` service tier `on_demand` on tokens per day (TPD): Limit 200000, Used 200000, Requested 1187. Please try again in 8m32.784s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

## Examples
### Successful Examples
**Example 1 (other_or_unclear)**
> Reply: Thank you for your feedback! If you need any further assistance, let us know.

**Example 2 (other_or_unclear)**
> Reply: You can manage notification settings in the app to receive alerts only for shipment status. Go to Settings → Notifications → Order Alerts to adjust.

### Intent Failures
**Example 1**
- True: `other_or_unclear` | Predicted: `issue_with_received_item`

### Missed Escalations (Should have escalated, didn't)

### Grounding Validation Failures