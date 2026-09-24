# SupportProof Agent v0 Evaluation Results

**Version Tracking:**
- Model: gemini-2.5-flash
- Retrieval K: 5
- Retrieval Threshold: 0.55 (Moderate)
- Golden Set Size: 200
- Successful Predictions: 165
- API/Evaluation Failures: 35 (17.5%)

## Comparison to Baselines (On Successful Predictions)

| System | Intent Accuracy | Intent Macro-F1 | Esc Precision | Esc Recall | Esc F1 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Majority | 0.320 | 0.044 | 0.000 | 0.000 | 0.000 |
| TF-IDF Baseline | 0.320 | 0.252 | 0.286 | 0.240 | 0.261 |
| **Agent v0** | **0.594** | **0.584** | **0.195** | **0.229** | **0.211** |

## Agent v0 Detailed Metrics
- **Intent Weighted-F1**: 0.591
- **False Escalation Rate (FPR)**: 0.254
- **Missed Escalation Rate (FNR)**: 0.771

## Grounding & Retrieval
- **Validation Failures**: 19 examples triggered deterministic safety overrides
- **Retrieval Confidence Distribution**: Strong: 200, Moderate: 0, Weak: 0

## API / Evaluation Failures
- Ex gold_0188: Error code: 400 - {'error': {'message': "Failed to generate JSON. Please adjust your prompt. See 'failed_generation' for more details.", 'type': 'invalid_request_error', 'code': 'json_validate_failed', 'failed_generation': '{"intent":"missing_delivery","intent_confidence":0.95,"reply":"I’m sorry your package shows delivered but hasn’t arrived. I’ll open a missing‑package investigation and your claim will be processed. We’ll update you shortly. If it takes more than 48 hours, let us know.","escalate":true,"escalation_reason":"Customer reported marked delivered but not received","evidence":[]'}}
- Ex gold_0112: Error code: 400 - {'error': {'message': "Generated JSON does not match the expected schema. Please adjust your prompt. See 'failed_generation' for more details. Error: jsonschema: '' does not validate with /required: missing properties: 'escalate'", 'type': 'invalid_request_error', 'code': 'json_validate_failed', 'failed_generation': '{"intent":"refund_request","intent_confidence":0.9,"reply":"I’m sorry you’re frustrated. I need to look into your order to help with the refund. I’ve escalated this to a specialist who will reach out shortly. Thank you for your patience.","elevate":true,"escalation_reason":"Insufficient evidence to process refund; requires account investigation.","evidence":[]}'}}
- Ex gold_0127: Error code: 400 - {'error': {'message': "Failed to generate JSON. Please adjust your prompt. See 'failed_generation' for more details.", 'type': 'invalid_request_error', 'code': 'json_validate_failed', 'failed_generation': '{"intent":"other_or_unclear","intent_confidence":0.9,"reply":"I’m sorry you’re seeing unfamiliar orders. I’ve flagged this for the fraud team. Please contact Amazon Customer Service at (phone or email) or go to help.amazon.com. They’ll investigate and ensure your account is secure.","escalate":true,"escalation_reason":"Potential fraud, account security","evidence":[]'}}
- Ex gold_0121: Error code: 400 - {'error': {'message': "Failed to generate JSON. Please adjust your prompt. See 'failed_generation' for more details.", 'type': 'invalid_request_error', 'code': 'json_validate_failed', 'failed_generation': '{"intent":"delivery_delay","intent_confidence":0.9,"reply":"DPD is a delivery partner in certain regions. Check your order status in Amazon.com. If it still hasn’t arrived, let us help locate it.","escalate":false,"escalation_reason":null,"evidence":[]'}}
- Ex gold_0151: Error code: 429 - {'error': {'message': 'Rate limit reached for model `openai/gpt-oss-20b` in organization `org_01kfjem4g7fs9rr4zbbj335n2d` service tier `on_demand` on tokens per day (TPD): Limit 200000, Used 199290, Requested 1805. Please try again in 7m53.039999999s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}
- Ex gold_0115: Error code: 429 - {'error': {'message': 'Rate limit reached for model `openai/gpt-oss-20b` in organization `org_01kfjem4g7fs9rr4zbbj335n2d` service tier `on_demand` on tokens per day (TPD): Limit 200000, Used 199289, Requested 1982. Please try again in 9m9.072s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}
- Ex gold_0057: Error code: 429 - {'error': {'message': 'Rate limit reached for model `openai/gpt-oss-20b` in organization `org_01kfjem4g7fs9rr4zbbj335n2d` service tier `on_demand` on tokens per day (TPD): Limit 200000, Used 199289, Requested 1717. Please try again in 7m14.592s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}
- Ex gold_0108: Error code: 429 - {'error': {'message': 'Rate limit reached for model `openai/gpt-oss-20b` in organization `org_01kfjem4g7fs9rr4zbbj335n2d` service tier `on_demand` on tokens per day (TPD): Limit 200000, Used 199288, Requested 1762. Please try again in 7m33.6s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}
- Ex gold_0192: Error code: 429 - {'error': {'message': 'Rate limit reached for model `openai/gpt-oss-20b` in organization `org_01kfjem4g7fs9rr4zbbj335n2d` service tier `on_demand` on tokens per day (TPD): Limit 200000, Used 199288, Requested 1770. Please try again in 7m37.056s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}
- Ex gold_0167: Error code: 429 - {'error': {'message': 'Rate limit reached for model `openai/gpt-oss-20b` in organization `org_01kfjem4g7fs9rr4zbbj335n2d` service tier `on_demand` on tokens per day (TPD): Limit 200000, Used 199287, Requested 1953. Please try again in 8m55.679999999s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}
- ... and 25 more.

## Examples
### Successful Examples
**Example 1 (account_prime)**
> Reply: I’m sorry you’re seeing that payment prompt again. Please log in to your Amazon Prime account on a web browser and review your subscription status. If it still shows as inactive, I’ll forward this to the Prime support team for investigation.

**Example 2 (other_or_unclear)**
> Reply: Thank you for your kind words! We're delighted we could help. If you need anything else, just let us know.

**Example 3 (delivery_delay)**
> Reply: I’m sorry to hear about your delivery experience. I’ll review the order status and get back to you with details on the delay and how we can improve. Please allow me a moment to investigate—thank you for your patience.

### Intent Failures
**Example 1**
- True: `order_tracking` | Predicted: `other_or_unclear`
**Example 2**
- True: `technical_issue` | Predicted: `other_or_unclear`
**Example 3**
- True: `other_or_unclear` | Predicted: `technical_issue`

### Missed Escalations (Should have escalated, didn't)
**Example 1**
- True Intent: `issue_with_received_item`
> Agent Reply: I’m sorry you’ve not heard back yet. Please contact our return support at the link below to expedite your request. Thank you for your patience.
**Example 2**
- True Intent: `refund_request`
> Agent Reply: I’m sorry you’re still waiting for your refund. Please check the refund status using the link I’ve provided and let us know if the issue persists.
**Example 3**
- True Intent: `issue_with_received_item`
> Agent Reply: I’m sorry the book arrived damaged. We can issue a refund or send a replacement without a return. Please let me know which you prefer, and I’ll process it right away.

### Grounding Validation Failures
**Example 1**
- Violations: LLM Error
**Example 2**
- Violations: LLM Error
**Example 3**
- Violations: Unsupported URL generated: https://t.co/SatXDZJSNM)