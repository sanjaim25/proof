# SupportProof Agent v1.1 Evaluation Results - Partial Run (202/200 completed)

**Version Tracking:**
- Model: openai/gpt-oss-20b
- Retrieval K: 2
- Retrieval Threshold: 0.55
- Golden Set Size: 200
- Processed Checkpoint Size: 202
- Successful API Predictions: 185
- API Errors in Checkpoint: 17
- Rate Limit Hit This Run: False

## Comparison to Baselines (On Successful Predictions)

| System | Intent Accuracy | Intent Macro-F1 | Esc Precision | Esc Recall | Esc F1 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Majority | 0.320 | 0.044 | 0.000 | 0.000 | 0.000 |
| TF-IDF Baseline | 0.320 | 0.252 | 0.286 | 0.240 | 0.261 |
| **Agent v1.1** | **0.595** | **0.567** | **0.403** | **0.659** | **0.500** |

## Agent v1.1 Detailed Metrics
- **Intent Weighted-F1**: 0.588
- **False Escalation Rate (FPR)**: 0.305
- **Missed Escalation Rate (FNR)**: 0.341

## Grounding & Retrieval
- **Validation Failures**: 0 examples triggered deterministic safety overrides
- **Retrieval Confidence Distribution**: Strong: 4, Moderate: 16, Weak: 165

## API / Evaluation Failures (This Run)
- Ex gold_0174: Connection error.
- Ex gold_0027: Connection error.
- Ex gold_0189: Connection error.
- Ex gold_0036: Connection error.
- Ex gold_0058: Connection error.
- Ex gold_0063: Connection error.
- Ex gold_0071: Connection error.
- Ex gold_0190: Connection error.
- Ex gold_0007: Connection error.
- Ex gold_0029: Connection error.
- ... and 1 more.

## Examples
### Successful Examples
**Example 1 (account_prime)**
> Reply: It looks like your Prime subscription may have been impacted by the sign‑out. Please verify your account's subscription status in the app. If it still asks to pay, I recommend contacting Prime support to review your account.

**Example 2 (other_or_unclear)**
> Reply: Thank you for your feedback! We're glad we resolved your concern. If you have any other questions, feel free to let us know.

**Example 3 (delivery_delay)**
> Reply: I’m sorry to hear about your recent experience. I’ll pass your feedback to the team so we can investigate and improve our shipping and support. If you have a specific order in mind, let me know the order number and I’ll help further.

### Intent Failures
**Example 1**
- True: `order_tracking` | Predicted: `missing_delivery`
**Example 2**
- True: `technical_issue` | Predicted: `refund_request`
**Example 3**
- True: `other_or_unclear` | Predicted: `issue_with_received_item`

### Missed Escalations (Should have escalated, didn't)
**Example 1**
- True Intent: `technical_issue`
> Agent Reply: I’m sorry to hear about the delivery issues. I’ll forward your feedback to our delivery team so they can review the problem. If you have a specific order you’d like help with, let me know.
**Example 2**
- True Intent: `missing_delivery`
> Agent Reply: It looks one package was delivered while the other had a delivery attempt but couldn’t access the front door. Please check the delivery status in the Amazon app or contact the carrier to arrange a pickup or re‑delivery.
**Example 3**
- True Intent: `delivery_delay`
> Agent Reply: I’m sorry your shipment hasn’t arrived yet. Please check the tracking for the latest status. If the order is still overdue, let me know the order number so I can check further.

### Grounding Validation Failures