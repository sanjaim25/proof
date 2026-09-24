# Agent v1 Retrieval Fix Report

## 1. The Mathematical Bug
The underlying mathematical bug was that the query vector was not normalized before computing cosine similarity with the document vectors.

In `src/agent/retriever.py`, the query vector was constructed as:
```python
q_vec = {t: 1.0 for t in q_tokens}
```
Because this vector consisted of raw `1.0` weights without Euclidean length normalization, its magnitude was $\sqrt{N}$ instead of $1.0$ (where $N$ is the number of matching tokens). 

When passed to `cosine_similarity(q_vec, doc_vec)`—where `doc_vec` is already normalized—the resulting dot product was unbounded and routinely exceeded $1.0$.

## 2. Where It Occurred
The bug occurred in `src/agent/retriever.py` in the `retrieve` method. 
It interacted with the `src/intent/discover.py` module, where `build_tfidf` correctly normalized the corpus vectors but could not enforce normalization on independently constructed query vectors during inference.

## 3. How It Was Fixed
The bug was fixed in `src/agent/retriever.py` by applying L2 normalization directly to the query vector before the similarity computation:
```python
import math
norm_sq = sum(v * v for v in q_vec.values())
if norm_sq > 0:
    norm = math.sqrt(norm_sq)
    q_vec = {t: v / norm for t, v in q_vec.items()}
```
Now, both the query vector and the document vectors are unit length, meaning their dot product (cosine similarity) is mathematically guaranteed to be bounded in $[0, 1]$.

## 4. Before/After Similarity Examples
**Before the fix:**
- A query matching 3 unique terms would produce a query vector magnitude of $\sqrt{3} \approx 1.73$.
- The dot product could theoretically reach up to $1.73$.
- In the 20-example pilot, the similarity for `gold_0102` was calculated as **$1.55$**.

**After the fix:**
- The query vector is scaled so its magnitude is exactly $1.0$.
- The similarity for the exact same query against the same document is properly normalized and bounded by $1.0$. Unit tests explicitly confirm that identical vectors produce similarity $\approx 1.0$.

## 5. Bounding Confirmation
Unit tests (`TestRetrieverMath`) were added to `tests/test_agent.py` to confirm this bounding logic:
- `test_cosine_similarity_bounded`: Asserts that an identical match does not exceed 1.0 (with slight floating-point allowance up to `1.000001`).
- `test_unrelated_vectors`: Asserts that orthogonal vectors produce `0.0`.

## 6. Why Old Retrieval-Confidence Benchmark Results Are Invalid
Because the dot product was heavily inflated (frequently $>1.0$), the confidence categorization threshold logic in `retriever.py` was compromised:
```python
if top_sim >= 0.75:
    confidence = "strong"
```
Because scores were artificially inflated above $0.75$, *every single example* in the v0 benchmark evaluated to `"strong"` confidence. Consequently, we gained no signal on how the system performs under moderate or weak confidence scenarios, and the deterministic escalation policy completely failed to trigger during the entire 200-example benchmark. The reported coverage statistic ("100% Strong") in `agent_results_v0.md` is mathematically invalid.

## 7. Deterministic Escalation Change
The deterministic escalation override was completely removed from `src/agent/agent.py`. 
Previously, the agent forced escalation if `confidence == "weak"`. This was an overly aggressive rule that escalated benign out-of-scope messages and praise simply because they didn't match historical operational logs. 

Now, the agent passes the retrieval confidence score directly to the LLM. The Agent v1 Prompt dictates the escalation policy, ensuring that the model only escalates if an issue explicitly requires account action, rather than blindly escalating every unmatched query.

**Note:** The deterministic *grounding* validation (checking for hallucinated URLs or unsupported monetary claims) was strictly preserved.

## 8. Test Results
The test suite was updated and fully passes (83 tests).
- `test_weak_retrieval_does_not_force_escalation` now verifies that if the retriever yields `weak` confidence, but the LLM decides `escalate=False`, the final decision remains `False`.
- `test_retrieval_confidence_thresholds` ensures that correct matching vectors trigger `strong` confidence, and missing ones trigger `weak`.
