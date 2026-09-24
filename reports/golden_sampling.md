# Golden Sampling Report

## Methodology
- **Random Seed**: 42
- **Candidate Pool Size**: Evaluated across 82,534 conversations.
- **Deduplication Approach**: Exact duplicate messages and multiple messages from the same user were heavily penalized/removed to ensure maximum diversity.
- **Intent Balancing**: Stratified sampling was used to force rare intents (e.g. `cancel_order`) into the golden set, ensuring all 11 intents are represented.
- **Difficult Cases**: Examples matching multiple disparate intent heuristics (e.g. 'late' AND 'refund') were deliberately sampled into a 'difficult' pool to stress-test human guidelines and classifier boundaries.

## Summary Statistics
- **Total Candidates Selected**: 200
- **Unique Conversations**: 200

## Distribution by Candidate Heuristic
(Note: These are heuristic guesses for sampling, NOT final labels.)
- `account_prime`: 15
- `cancel_order`: 10
- `delivery_delay`: 20
- `difficult`: 20
- `gift_card_promotion`: 10
- `issue_with_received_item`: 15
- `missing_delivery`: 15
- `order_tracking`: 15
- `other_or_unclear`: 25
- `refund_request`: 20
- `return_request`: 15
- `technical_issue`: 20

## Limitations
- Heuristics may have missed implicit intents. The 25 `other_or_unclear` samples are critical for evaluating whether real user issues fall outside our predefined rules.
- Deliberately keeping noisy Twitter language means annotators will have to deal with typos, missing context, and sarcasm.