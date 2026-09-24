# Golden Set V1 Validation Report

## Overall Status: PASSED
- Total Examples: 200

## Intent Distribution
| Intent | Count | % |
| :--- | :---: | :---: |
| other_or_unclear | 64 | 32.0% |
| delivery_delay | 37 | 18.5% |
| issue_with_received_item | 25 | 12.5% |
| technical_issue | 14 | 7.0% |
| refund_request | 11 | 5.5% |
| missing_delivery | 10 | 5.0% |
| cancel_order | 9 | 4.5% |
| account_prime | 8 | 4.0% |
| order_tracking | 8 | 4.0% |
| return_request | 8 | 4.0% |
| gift_card_promotion | 6 | 3.0% |

## Escalation Distribution
| Escalation | Count | % |
| :--- | :---: | :---: |
| No | 150 | 75.0% |
| Yes | 50 | 25.0% |

## Intent × Escalation Cross-Tabulation
| Intent | Escalate Yes | Escalate No |
| :--- | :---: | :---: |
| account_prime | 0 | 8 |
| cancel_order | 1 | 8 |
| delivery_delay | 3 | 34 |
| gift_card_promotion | 1 | 5 |
| issue_with_received_item | 20 | 5 |
| missing_delivery | 9 | 1 |
| order_tracking | 0 | 8 |
| other_or_unclear | 5 | 59 |
| refund_request | 9 | 2 |
| return_request | 0 | 8 |
| technical_issue | 2 | 12 |

## Annotation Warnings
The following examples passed structural validation but should be manually reviewed:
- [gold_0102] Labeled as other_or_unclear (Requires review).
- [gold_0122] Labeled as other_or_unclear (Requires review).
- [gold_0014] Escalate=Yes but human_reason is empty.
- [gold_0003] Labeled as other_or_unclear (Requires review).
- [gold_0137] Labeled as other_or_unclear (Requires review).
- [gold_0159] Escalate=Yes but human_reason is empty.
- [gold_0046] Escalate=Yes but human_reason is empty.
- [gold_0131] Labeled as other_or_unclear (Requires review).
- [gold_0031] Escalate=Yes but human_reason is empty.
- [gold_0004] Labeled as other_or_unclear (Requires review).
- [gold_0160] Escalate=Yes but human_reason is empty.
- [gold_0016] Labeled as other_or_unclear (Requires review).
- [gold_0127] Escalate=Yes but human_reason is empty.
- [gold_0187] Escalate=Yes but human_reason is empty.
- [gold_0048] Escalate=Yes but human_reason is empty.
- [gold_0111] Labeled as other_or_unclear (Requires review).
- [gold_0006] Labeled as other_or_unclear (Requires review).
- [gold_0195] Escalate=Yes but human_reason is empty.
- [gold_0038] Labeled as other_or_unclear (Requires review).
- [gold_0123] Labeled as other_or_unclear (Requires review).
- [gold_0037] Labeled as other_or_unclear (Requires review).
- [gold_0062] Escalate=Yes but human_reason is empty.
- [gold_0196] Escalate=Yes but human_reason is empty.
- [gold_0033] Labeled as other_or_unclear (Requires review).
- [gold_0011] Escalate=Yes but human_reason is empty.
- [gold_0145] Labeled as other_or_unclear (Requires review).
- [gold_0161] Labeled as other_or_unclear (Requires review).
- [gold_0053] Escalate=Yes but human_reason is empty.
- [gold_0074] Labeled as other_or_unclear (Requires review).
- [gold_0114] Labeled as other_or_unclear (Requires review).
- [gold_0106] Labeled as other_or_unclear (Requires review).
- [gold_0001] Labeled as other_or_unclear (Requires review).
- [gold_0162] Escalate=Yes but human_reason is empty.
- [gold_0193] Labeled as other_or_unclear (Requires review).
- [gold_0177] Labeled as other_or_unclear (Requires review).
- [gold_0147] Labeled as other_or_unclear (Requires review).
- [gold_0180] Labeled as other_or_unclear (Requires review).
- [gold_0085] Escalate=Yes but human_reason is empty.
- [gold_0105] Labeled as other_or_unclear (Requires review).
- [gold_0055] Labeled as other_or_unclear (Requires review).
- [gold_0197] Labeled as other_or_unclear (Requires review).
- [gold_0110] Labeled as other_or_unclear (Requires review).
- [gold_0134] Labeled as other_or_unclear (Requires review).
- [gold_0143] Labeled as other_or_unclear (Requires review).
- [gold_0034] Labeled as other_or_unclear (Requires review).
- [gold_0064] Labeled as other_or_unclear (Requires review).
- [gold_0149] Labeled as other_or_unclear (Requires review).
- [gold_0101] Labeled as other_or_unclear (Requires review).
- [gold_0156] Escalate=Yes but human_reason is empty.
- [gold_0073] Escalate=Yes but human_reason is empty.
- [gold_0028] Labeled as other_or_unclear (Requires review).
- [gold_0185] Escalate=Yes but human_reason is empty.
- [gold_0113] Labeled as other_or_unclear (Requires review).
- [gold_0052] Labeled as other_or_unclear (Requires review).
- [gold_0175] Labeled as other_or_unclear (Requires review).
- [gold_0005] Labeled as other_or_unclear (Requires review).
- [gold_0030] Labeled as other_or_unclear (Requires review).
- [gold_0100] Labeled as other_or_unclear (Requires review).
- [gold_0099] Labeled as other_or_unclear (Requires review).
- [gold_0125] Escalate=Yes but human_reason is empty.
- [gold_0035] Escalate=Yes but human_reason is empty.
- [gold_0139] Labeled as other_or_unclear (Requires review).
- [gold_0150] Escalate=Yes but human_reason is empty.
- [gold_0128] Labeled as other_or_unclear (Requires review).
- [gold_0078] Escalate=Yes but human_reason is empty.
- [gold_0078] Labeled as other_or_unclear (Requires review).
- [gold_0083] Escalate=Yes but human_reason is empty.
- [gold_0165] Labeled as other_or_unclear (Requires review).
- [gold_0120] Labeled as other_or_unclear (Requires review).
- [gold_0069] Labeled as other_or_unclear (Requires review).
- [gold_0091] Escalate=Yes but human_reason is empty.
- [gold_0095] Escalate=Yes but human_reason is empty.
- [gold_0158] Escalate=Yes but human_reason is empty.
- [gold_0148] Escalate=Yes but human_reason is empty.
- [gold_0093] Labeled as other_or_unclear (Requires review).
- [gold_0142] Escalate=Yes but human_reason is empty.
- [gold_0142] Labeled as other_or_unclear (Requires review).
- [gold_0032] Labeled as other_or_unclear (Requires review).
- [gold_0138] Labeled as other_or_unclear (Requires review).
- [gold_0118] Labeled as other_or_unclear (Requires review).
- [gold_0068] Escalate=Yes but human_reason is empty.
- [gold_0089] Escalate=Yes but human_reason is empty.
- [gold_0025] Labeled as other_or_unclear (Requires review).
- [gold_0183] Escalate=Yes but human_reason is empty.
- [gold_0191] Labeled as other_or_unclear (Requires review).
- [gold_0182] Labeled as other_or_unclear (Requires review).
- [gold_0040] Labeled as other_or_unclear (Requires review).
- [gold_0169] Escalate=Yes but human_reason is empty.
- [gold_0169] Labeled as other_or_unclear (Requires review).
- [gold_0088] Escalate=Yes but human_reason is empty.
- [gold_0088] Labeled as other_or_unclear (Requires review).
- [gold_0186] Labeled as other_or_unclear (Requires review).
- [gold_0002] Escalate=Yes but human_reason is empty.
- [gold_0072] Escalate=Yes but human_reason is empty.
- [gold_0115] Escalate=Yes but human_reason is empty.
- [gold_0057] Labeled as other_or_unclear (Requires review).
- [gold_0192] Escalate=Yes but human_reason is empty.
- [gold_0051] Escalate=Yes but human_reason is empty.
- [gold_0051] Labeled as other_or_unclear (Requires review).
- [gold_0144] Escalate=Yes but human_reason is empty.
- [gold_0198] Labeled as other_or_unclear (Requires review).
- [gold_0155] Escalate=Yes but human_reason is empty.
- [gold_0060] Escalate=Yes but human_reason is empty.
- [gold_0056] Escalate=Yes but human_reason is empty.
- [gold_0008] Escalate=Yes but human_reason is empty.
- [gold_0009] Labeled as other_or_unclear (Requires review).
- [gold_0152] Labeled as other_or_unclear (Requires review).
- [gold_0174] Escalate=Yes but human_reason is empty.
- [gold_0027] Escalate=Yes but human_reason is empty.
- [gold_0063] Escalate=Yes but human_reason is empty.
- [gold_0071] Escalate=Yes but human_reason is empty.
- [gold_0190] Escalate=Yes but human_reason is empty.
- [gold_0029] Escalate=Yes but human_reason is empty.

## Dataset Limitations
- The dataset inherits noise and truncation from the original Twitter Support corpus.
- 'other_or_unclear' examples heavily depend on annotator judgment when context is missing.
- Final evaluations must account for inherent ambiguity in short social media posts.