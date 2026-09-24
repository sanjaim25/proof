# Agent v1 Escalation Policy Analysis

## 1. What conditions can force escalation regardless of the LLM's `escalate` value?
In `src/agent/agent.py`, the `SupportProofAgent.process()` method applies a deterministic override before calling the LLM:
```python
deterministic_escalate = False
if confidence == "weak" or not cases:
    deterministic_escalate = True
    deterministic_reason.append("Very low retrieval similarity / no evidence.")
```
If this condition triggers, it forces the final response to `escalate=True`, regardless of whether the LLM decided to escalate. Additionally, the smart grounding validator forces escalation if the LLM hallucinates URLs or unsupported monetary amounts.

## 2. Does low retrieval similarity/no evidence automatically force escalation?
Yes. The deterministic rule described above explicitly forces `escalate = True` and overrides any LLM decision if the retriever returns a "weak" confidence or an empty list of cases.

## 3. What similarity/confidence thresholds are used?
In `src/agent/retriever.py`, confidence is assigned based on the top cosine similarity score (`top_sim`):
- `top_sim >= 0.75` → `"strong"`
- `top_sim >= 0.55` → `"moderate"`
- `< 0.55` → `"weak"`

However, there is a fundamental implementation flaw: **the query vector is not normalized**. 
```python
q_vec = {t: 1.0 for t in q_tokens} 
```
Because the query vector uses a raw `1.0` for every matching token without Euclidean normalization, the cosine similarity dot product can (and usually does) exceed `1.0`. Because of this math bug, `top_sim` is heavily inflated.

## 4. How often did this deterministic rule cause escalation=True in the 165 successful Agent v0 benchmark predictions?
**Zero times (0/165).** 
Because of the query normalization bug, the `top_sim` score was artificially inflated above `0.75` for every single example in the v0 benchmark. Thus, `confidence` evaluated to `"strong"` 100% of the time, and the deterministic rule never actually fired during the benchmark. 

*(Note: The reason it fired during the recent 20-example pilot was a bug in the `pilot_v1.py` script where `agent.retriever.fit()` was not called, causing the internal retriever to return 0 cases, triggering the rule).*

## 5 & 6. True/False Escalation split and Intents
N/A. Because it triggered 0 times in the actual v0 benchmark, there is no split to report.

## 7. Does the current design make conceptual sense for a support agent?
No. An automatic forced escalation on low similarity is fundamentally flawed. If a customer sends a completely benign out-of-scope message, praise (e.g., `"You guys are great!"`), or a non-actionable comment, it will likely have low similarity to historical support cases. Automatically escalating this to a human agent wastes human resources. 

## 8. Is low retrieval confidence itself a safety reason to escalate, or should it instead constrain the reply?
Low retrieval confidence means the agent lacks historical context to safely resolve operational tasks (like processing a refund). However, it should **not** force an escalation. Instead, it should constrain the LLM. If evidence is missing, the LLM should confidently classify the intent (often `other_or_unclear`), provide a safe fallback reply, and *only* escalate if the intent explicitly requires account intervention or satisfies the v1 escalation policy.

## 9. Compare the deterministic policy against the intended v1 escalation policy
The deterministic rule directly contradicts the v1 prompt policy. The v1 policy specifically instructs the LLM to escalate *only* on strict operational criteria (e.g., missing deliveries, explicitly requested escalation). The deterministic rule blindly overrides this, acting as a blunt instrument that would cause massive false-positive escalations if the mathematical bug inflating `top_sim` were fixed.

---

### Recommendations and Action Plan

- **Deterministic Escalation Rules:** `if confidence == "weak" or not cases: escalate = True`.
- **Measured Impact on v0 Benchmark:** 0 cases affected due to an underlying math bug masking the rule.
- **Recommendation:** Remove the deterministic escalation override entirely. We have already instructed the LLM in v1 on exactly when to escalate (including when "available evidence is insufficient to safely resolve the issue"). Let the LLM make the decision.
- **Smallest Safe Change:** In `src/agent/agent.py`, delete the `deterministic_escalate` override logic before the LLM generation step. Leave the deterministic *grounding* validation (which catches hallucinated URLs) intact.
