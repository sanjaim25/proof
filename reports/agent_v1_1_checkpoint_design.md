# Agent v1.1 Evaluation Checkpoint Design

This document details the checkpoint and resume mechanism implemented for the Agent v1.1 evaluation runner. The primary goal is to allow a 200-example golden set benchmark to be completed across multiple Groq token quota days, without altering the evaluation methodology or risking methodological drift.

## 1. Checkpoint Format
The evaluation persists state incrementally to two files:
- **`data/processed/agent_evaluation_metadata_v1.1.json`**: Written at the start of a fresh evaluation run. It stores the configuration of the run (Model, K, Threshold, Golden Set reference).
- **`data/processed/agent_predictions_v1.1.jsonl`**: A JSON Lines (JSONL) file. Each line is an atomic, self-contained JSON object representing a completed evaluation of a single golden example. It records the true labels, predictions, confidences, replies, deterministic grounding violations, and any non-rate-limit API errors.

## 2. Crash Safety
To prevent data corruption if the process halts (e.g. out of memory, VM termination, keyboard interrupt):
- The `agent_predictions_v1.1.jsonl` file is opened in append (`"a"`) mode.
- Immediately after processing an example, the script writes the JSON string to the file.
- The script immediately calls `out_file.flush()` and `os.fsync(out_file.fileno())` to force the OS to write the data to disk before proceeding to the next example.

## 3. Resume Behavior & Configuration Consistency
When the script is launched with the `--resume` flag, it executes the following safe-resume procedure:

1. **Existence Check**: It verifies that both the metadata and the prediction files exist. If not, it aborts.
2. **Metadata Validation**: It loads the metadata JSON and strictly asserts that the current environment's Model, K, and similarity Threshold exactly match the metadata recorded when the run started. If they differ, the runner raises an `AssertionError` and aborts. This prevents a benchmark from containing a silent mix of configuration parameters.
3. **Completed IDs Extraction**: It iterates through the JSONL file and collects a set of `example_id`s that have already been evaluated.
4. **Evaluation Loop**: The runner loops through the frozen 200 `golden_examples` in their original order. If an `example_id` is in the completed set, it is skipped entirely. This guarantees that successful predictions are never duplicated, discarded, or re-evaluated.

## 4. Rate-Limit Handling (429s)
API rate limits (like Groq's daily 200,000 token limit) are gracefully intercepted:
- If a rate limit error is detected in the `api_error` field (containing "429" or "rate limit"), the loop immediately **breaks**.
- The failed rate-limit example is **not** written to the checkpoint JSONL file.
- The runner reports a "Partial Run" markdown report summarizing the examples completed thus far.
- Because the 429 failure was not written to the checkpoint, it will be evaluated normally when `--resume` is invoked on a future day.
- Other API failures (e.g., 500s or JSON parsing failures) are treated as legitimate run-time failures and are permanently written to the JSONL.

## 5. Methodological Equivalence
The resumed benchmark is methodologically identical to a single, uninterrupted run because:
1. The **golden set is frozen** and ordered exactly as before. The agent processes the remaining examples precisely as it would have if it hadn't stopped.
2. The **retriever is refitted identically** across resumes. Since the training data and parameters (K, threshold) are guarded by metadata checks, the retrieval space is identical.
3. The **metrics are reconstructed simultaneously**. After the loop finishes (either through completion or a rate limit abort), the script loads *all* predictions (both newly completed and historically checkpointed) into memory and reconstructs the metrics. Thus, the final denominator and metric calculation code are identical to a single-pass run.

## 6. Test Suite
The implementation was covered with a specialized `pytest` suite (`tests/test_run_agent.py`) simulating API responses. Key tests guarantee:
- Metadata creation on fresh runs.
- Protection against accidental overwrite if `--resume` is omitted but files exist.
- Hard failures if the configuration changes during a resume attempt.
- Rate-limit skipping and non-rate-limit error preservation.
- Accurate metrics reconstruction across aborted and resumed runs.
