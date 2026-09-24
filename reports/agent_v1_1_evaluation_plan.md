# Agent v1.1 Evaluation Plan & Technical Risk Assessment

## 1. Evaluation Code Verification
The current evaluation runner (`src/evaluation/run_agent.py`) and Agent logic (`src/agent/agent.py`) have been thoroughly inspected and verified:
- **Production Path**: The script instantiates `SupportProofAgent(k=2, sim_threshold=0.55)` and calls `agent.retriever.fit()`. 
- **Corrected Math**: The retriever now uses the strictly bounded L2 normalized cosine similarity.
- **Model Configuration**: Environment variables dictate `openai/gpt-oss-20b` via Groq.
- **Strict JSON Schema**: Groq strict JSON formatting is fully integrated and tested.
- **Golden Set**: It strictly reads from the frozen `data/golden/golden_set_v1.csv` without modifying it.
- **Agent v0 Artifacts**: The v0 benchmark artifacts (`agent_predictions.jsonl` and `agent_results_v0.md` or `v1.md`) are completely untouched. The new outputs are safely isolated to `agent_predictions_v1.1.jsonl` and `agent_results_v1.1.md`.

## 2. API Failure & Partial Run Handling
- **API Failures**: Any API failures (e.g. rate limits, 503s) are caught in `run_agent.py`. They are completely excluded from the metric denominators (Accuracy, Precision, Recall, etc.). They are counted and reported separately under "API/Evaluation Failures".
- **Misreporting Risk**: A partial run cannot accidentally be misrepresented as a complete benchmark. The final markdown report explicitly logs the number of *Successful Predictions* and *API Failures* out of the total Golden Set size, ensuring transparency.

## 3. Token Estimation & Quota Analysis
Groq currently enforces a strict **200,000 Tokens Per Day (TPD)** limit on the free tier for `openai/gpt-oss-20b`.

Based on our previous API request payloads, we can estimate token consumption per example:
- **System Prompt**: ~900 tokens
- **Schema Definition Overhead**: ~200 tokens
- **Retrieved Evidence & Context**: ~300 tokens (for K=2)
- **User Prompt (Customer Message)**: ~50 tokens
- **Total Expected Input**: ~1,450 tokens
- **Total Expected Output**: ~150 - 250 tokens
- **Estimated Total per Example**: **~1,700 tokens**

**Budget Forecast**:
- **20-Example Pilot**: 20 * 1,700 = **~34,000 tokens**
- **Expected Remaining Quota (post-pilot)**: 200,000 - 34,000 = **~166,000 tokens**
- **200-Example Benchmark**: 200 * 1,700 = **~340,000 tokens**

> [!WARNING] 
> **The 200-example benchmark CANNOT fit within the 200,000 TPD limit on a single day.** 
> Attempting to run all 200 examples concurrently will result in a hard `429 Rate Limit` failure around the ~117th example (117 * 1700 = 198,900 tokens).

## 4. Technical Risks & Evaluation Runner Limitations
I evaluated whether `run_agent.py` supports safely resuming a benchmark from previously completed examples.

> [!IMPORTANT]
> **The evaluation runner currently does NOT support resuming.** 
> It processes examples sequentially and only writes the final `.jsonl` and `.md` reports at the very end of the loop. If the script crashes or hits the Groq rate limit at example 117, it will either skip the remaining examples (resulting in a permanently partial run report) or crash, losing all progress. 

Because you explicitly requested *not* to implement a resume mechanism unless it is perfectly safe and doesn't alter the denominator/methodology, I have left the script untouched.

## 5. Project Readiness
The project architecture, unit tests, agent prompts, deterministic logic removal, and mathematical fixes are **100% ready** for the Agent v1.1 evaluation. The full `pytest` suite is passing (83/83).

However, due to the Groq TPD limit, you will need to either:
1. Upgrade to a paid/dev tier on Groq to lift the 200,000 TPD limit.
2. Direct me to implement a robust JSONL-based checkpointing/resume mechanism in `run_agent.py` so the benchmark can be completed over the span of 2 days.
