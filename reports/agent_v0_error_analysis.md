# SupportProof Agent v0 — Evidence-Based Error Analysis

This report provides a detailed error analysis of the Agent v0 benchmark results (165 successful predictions, 35 API failures) without altering the implementation.

---

## 1. INTENT ERRORS

Out of 165 successful predictions, there were 67 intent classification errors (accuracy = 59.4%).

### Major Confusion Pairs
| True Intent | Predicted Intent | Errors | Likely Cause |
|---|---|---|---|
| `other_or_unclear` | `technical_issue` | 7 | **Prompt/Taxonomy boundary**: Customers complaining about vague issues (e.g., app notifications not working how they want) are classified as technical issues rather than general/unclear complaints. |
| `other_or_unclear` | `issue_with_received_item` | 5 | **Ambiguous customer message**: Generic complaints like "arrived damaged" without explicit item context are forced into a specific intent instead of remaining ambiguous. |
| `other_or_unclear` | `delivery_delay` | 5 | **Taxonomy boundary**: Any mention of shipping or delivery in a vague complaint triggers this, regardless of whether the customer explicitly says it is late. |
| `other_or_unclear` | `refund_request` | 5 | **Prompting**: Mentions of charges, money, or costs are overly triggering `refund_request` even if the customer isn't explicitly asking for one. |
| `return_request` | `refund_request` | 4 | **Prompting**: The model struggles to separate "I want to return this physical item" from "I want my money back", despite the differentiation rules in the prompt. |

---

## 2. OTHER_OR_UNCLEAR ANALYSIS

The `other_or_unclear` intent acts as a catch-all for noise, highly specific outliers, or ambiguous messages. 

- **Total `other_or_unclear` in Golden Set:** 59 
- **Correctly predicted:** 24
- **Over-classified as specific intents:** 35

### Why they should remain other_or_unclear:
The model is overly eager to assign a specific label to ambiguous messages. For example:
- **gold_0122:** *"I would really like if the @115830 app would give me notifications only when something I order is on its way.."*
  - **Predicted:** `technical_issue`
  - **Why it's unclear:** This is a feature request/complaint, not a technical failure (crash/error).
- **gold_0113:** *"Is the @AmazonHelp reloadable gift card physical.I'm trying to understand the concept."*
  - **Predicted:** `gift_card_promotion`
  - **Why it's unclear:** It's a general question, not a support issue regarding a specific gift card problem.

**Conclusion:** The taxonomy boundary needs clarification. The prompt must explicitly instruct the model to use `other_or_unclear` for general questions, feature requests, and complaints that don't fit the narrow definitions of the specific intents, rather than forcing a fit.

---

## 3. ESCALATION ANALYSIS

The agent struggles significantly with escalation, prioritizing automated responses even when the criteria require human intervention.

- **Golden True Escalations (Should Escalate):** 50
- **Caught Escalations (TP):** 8
- **Missed Escalations (FN):** 27
- **False Escalations (FP):** 33

### Analysis of Missed Escalations
The model aggressively attempts to resolve issues that require human investigation, missing 77.1% of true escalations.
- **Pattern 1: Refund/Return Overconfidence.** Customers requesting refunds or returns often require account checks. The model drafts generic "please use the portal" replies instead of escalating to process the actual request. 
- **Pattern 2: Account/Order Actions.** (e.g., gold_0067: *"I subscribed to Amazon prime in july17... it is asking me again to pay"*). The model suggests logging out and back in, rather than escalating a billing/subscription issue that requires account access.

### Analysis of False Escalations
- **Pattern:** 19 of the 33 false escalations were forced by the deterministic **Grounding Validator**. The LLM generated an unsupported URL, triggering an automatic safety escalation, turning what should have been a standard reply into a false escalation.

---

## 4. GROUNDING FAILURES

The deterministic safety validator caught 19 grounding violations, replacing the agent's reply with a safe escalation message.

### Breakdown:
- **Unsupported URLs:** 17
- **Unsupported Monetary Amounts:** 2

**Root Cause for URLs:**
The model is hallucinating `t.co` shortlinks (e.g., `https://t.co/JzP7hlA23B`, `https://t.co/TdDksLo6Mf`). 
Why? Because the retrieved historical evidence (Twitter conversations) contains these exact `t.co` links. The model copies them, thinking they are helpful, but the URLs are tied to specific historical cases and are unsupported for the current user.

**Conclusion:** The prompt needs a strict rule: "Do NOT include URLs or links in your reply. Customers cannot click them." or the retriever needs to scrub URLs from the evidence before formatting the prompt.

---

## 5. API FAILURES

Out of 200 requests, 35 failed at the API layer.

- **429 Rate Limit Exceeded (31 failures):**
  These were spread throughout the run (from example 7 to 198), indicating that the 200,000 Tokens Per Day (TPD) limit is too tight for K=2, even with our prompt optimizations. 
- **JSON Validation Failed (4 failures):**
  - **gold_0112:** Missing the required `escalate` property (model generated `elevate` instead).
  - **Others:** Groq's strict schema engine occasionally failed to generate valid JSON due to complex characters or internal generation timeouts (e.g., `"Failed to generate JSON. Please adjust your prompt."`).

---

## 6. REPRESENTATIVE CASES

### Representative Intent Errors
1. **gold_0122**
   - **Msg:** *"I would really like if the @115830 app would give me notifications only when something I order is on its way.."*
   - **True:** `other_or_unclear` | **Pred:** `technical_issue`
   - **Diagnosis:** Feature request misclassified as a technical app failure.
2. **gold_0014**
   - **Msg:** *"WTH guys! I've been trying to return a faulty product since 7th Oct but haven't gotten a response yet!"*
   - **True:** `issue_with_received_item` | **Pred:** `return_request`
   - **Diagnosis:** Mentions returning a faulty item. Model prioritized "return" over the root cause ("faulty").
3. **gold_0104**
   - **Msg:** *"My parcel was supposed to be delivered today and come before 8, where is it?"*
   - **True:** `delivery_delay` | **Pred:** `order_tracking`
   - **Diagnosis:** Model interpreted "where is it?" as tracking, missing the "supposed to be delivered today" delay signal.
4. **gold_0065**
   - **Msg:** *"when you cancel my order, at least have the courtesy of showing it under 'Canceled Orders'"*
   - **True:** `technical_issue` | **Pred:** `cancel_order`
   - **Diagnosis:** Misinterpreted a UI complaint about a canceled order as a request to cancel an order.

### Representative Missed Escalations
1. **gold_0067**
   - **Msg:** *"I subscribed to Amazon prime... it is asking me again to pay"*
   - **Diagnosis:** Model suggested troubleshooting steps instead of escalating a billing account issue.

### Representative Grounding Failure
1. **gold_0011**
   - **Msg:** *"I received a parcel today but when I opened it, it was empty."*
   - **Diagnosis:** Model hallucinated `https://t.co/HQhpS2qeEd`, copied directly from a retrieved historical case, triggering the safety validator.

---

## 7. ROOT CAUSES (TOP 5)

| Rank | Failure Mode | Frequency | Impact | Root Cause | Proposed Fix Category |
|---|---|---|---|---|---|
| **1** | Over-classification of `other_or_unclear` | 35 errors | High (Intent Acc) | Model forces ambiguous messages, general questions, and feature requests into narrow intent categories. | **Prompting** (Clarify boundary definitions for other_or_unclear) |
| **2** | Missed Escalations on Account Issues | 27 errors | Critical (Safety) | Model tries to resolve billing/refund/return logistics itself using generic steps instead of recognizing it lacks account access. | **Prompting/Policy** (Strengthen escalation criteria for account actions) |
| **3** | URL Hallucinations triggering False Escalations | 17 errors | High (Grounding) | Retrieved historical Twitter evidence contains `t.co` links. The model copies them, violating grounding rules. | **Prompting** (Explicit instruction to never include links/URLs) |
| **4** | API Rate Limits (429) | 31 errors | High (Coverage) | Token usage per K=2 prompt (~950 tokens) * 200 examples = ~190k, pushing right up against Groq's 200k TPD limit. | **Retrieval** (Truncate evidence further or drop to K=1) |
| **5** | Confusion: Return vs. Refund vs. Item Issue | ~8 errors | Medium (Intent Acc) | Customers often combine these (e.g. "I want to return a broken item for a refund"). Model struggles with precedence. | **Prompting** (Add explicit precedence rules for overlapping intents) |
