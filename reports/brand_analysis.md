# Brand Analysis Report

**Dataset:** 2,811,774 tweets across 108 brand accounts

## Ranking Criteria

Brands are ranked by a **composite quality score** (0–1) designed to
identify brands with the strongest *usable* customer-support data,
not simply the highest tweet volume.

| Weight | Metric | Rationale |
|--------|--------|-----------|
| 35% | Complete conversations | Conversations with both customer and brand messages — the core data unit |
| 25% | Multi-turn conversations | Conversations ≥ 3 messages with both sides — deeper interaction data |
| 20% | Response rate | Fraction of attributed conversations where the brand actually responded |
| 10% | Unique customers | Diversity of customer issues and intents |
| 10% | Avg conversation length | Depth of engagement (capped at 10 for normalisation) |

### Why not rank by tweet count?

Raw tweet volume conflates noisy, one-sided, or bot-generated traffic with
genuine support interactions. A brand with 100 k tweets but mostly
unanswered customer complaints is *less* useful than a brand with 30 k
tweets that are predominantly multi-turn resolved conversations.

## Top 20 Brands by Quality Score

| Rank | Brand | Total | Complete | Multi-turn | Resp % | Customers | Avg Len | Score |
|------|-------|-------|----------|------------|--------|-----------|---------|-------|
| 1 | `AmazonHelp` | 373,494 | 82,534 | 51,244 | 100.0% | 73,457 | 4.53 | 0.9375 |
| 2 | `AppleSupport` | 238,848 | 80,702 | 28,140 | 99.9% | 79,604 | 2.96 | 0.8089 |
| 3 | `Uber_Support` | 128,443 | 41,923 | 15,088 | 100.0% | 39,870 | 3.07 | 0.5321 |
| 4 | `SpotifyCares` | 91,813 | 28,277 | 10,500 | 100.0% | 28,304 | 3.25 | 0.4392 |
| 5 | `AmericanAir` | 86,952 | 26,385 | 11,577 | 99.7% | 23,307 | 3.32 | 0.4303 |
| 6 | `Delta` | 87,980 | 26,164 | 11,146 | 99.2% | 23,672 | 3.36 | 0.4271 |
| 7 | `comcastcares` | 72,661 | 24,061 | 8,793 | 99.9% | 23,453 | 3.04 | 0.4046 |
| 8 | `TMobileHelp` | 81,480 | 22,789 | 8,620 | 100.0% | 21,639 | 3.63 | 0.4021 |
| 9 | `Tesco` | 73,363 | 16,721 | 11,629 | 99.1% | 17,216 | 4.39 | 0.3914 |
| 10 | `SouthwestAir` | 64,469 | 21,634 | 7,231 | 99.7% | 20,798 | 2.99 | 0.3823 |
| 11 | `VirginTrains` | 65,687 | 14,848 | 9,184 | 99.9% | 13,460 | 4.43 | 0.3688 |
| 12 | `British_Airways` | 60,599 | 16,450 | 8,829 | 99.9% | 14,932 | 3.69 | 0.3682 |
| 13 | `Ask_Spectrum` | 59,212 | 18,529 | 6,559 | 99.7% | 18,778 | 3.22 | 0.3658 |
| 14 | `XboxSupport` | 57,032 | 13,434 | 8,395 | 99.6% | 15,232 | 4.29 | 0.3592 |
| 15 | `sprintcare` | 52,621 | 13,555 | 6,382 | 99.9% | 14,759 | 3.99 | 0.3469 |
| 16 | `hulu_support` | 48,700 | 14,952 | 5,897 | 99.9% | 14,302 | 3.30 | 0.3430 |
| 17 | `UPSHelp` | 43,614 | 15,522 | 5,349 | 99.8% | 15,723 | 2.87 | 0.3400 |
| 18 | `ATVIAssist` | 48,406 | 11,096 | 5,461 | 98.9% | 16,964 | 4.35 | 0.3362 |
| 19 | `GWRHelp` | 46,669 | 10,728 | 6,949 | 99.9% | 8,158 | 4.37 | 0.3331 |
| 20 | `ChipotleTweets` | 41,833 | 14,392 | 4,870 | 100.0% | 15,151 | 2.91 | 0.3329 |

## Data Quality Limitations

1. **Brand ≡ account handle.** Some companies operate multiple support handles
   (e.g. `@AmazonHelp` vs `@AmazonCS`). These appear as separate brands and
   are **not merged** automatically. Manual review may reveal opportunities
   to combine related accounts.
2. **Response-rate denominator.** Conversations are attributed to a brand via
   outbound tweets **or** `@mention` parsing of inbound tweets. Customers who
   tag a brand using non-standard spelling or omit the `@` prefix will be
   missed, potentially *overstating* the response rate.
3. **Conversation boundaries.** Threads are reconstructed using
   `in_response_to_tweet_id` and `response_tweet_id` via Union-Find. Some
   threads may be fragmented when linking IDs reference tweets absent from
   the dataset.
4. **Inbound attribution.** In the rare case of multi-brand conversations,
   inbound tweets are attributed to *all* involved brands, slightly
   inflating inbound counts.
5. **Temporal snapshot.** The dataset captures activity at a fixed point in
   time; brand behaviour may have changed.

## Suitability Analysis of Top Candidates

For the SupportProof project we need a brand whose data supports:

- **Intent taxonomy:** diverse customer issues (→ many unique customers)
- **Historical-resolution retrieval:** resolved multi-turn exchanges
- **Golden evaluation set (150–250 examples):** enough quality conversations
- **Escalation decisions:** conversations showing both resolution and escalation patterns

### 1. `AmazonHelp` — **Suitable**

- ✅ Excellent multi-turn volume (51,244)
- ✅ Large customer base (73,457) — diverse intents
- ✅ High response rate (100.0%)
- ✅ Good conversation depth (avg 4.5)

### 2. `AppleSupport` — **Suitable**

- ✅ Excellent multi-turn volume (28,140)
- ✅ Large customer base (79,604) — diverse intents
- ✅ High response rate (99.9%)
- ✅ Adequate conversation depth (avg 3.0)

### 3. `Uber_Support` — **Suitable**

- ✅ Excellent multi-turn volume (15,088)
- ✅ Large customer base (39,870) — diverse intents
- ✅ High response rate (100.0%)
- ✅ Adequate conversation depth (avg 3.1)

### 4. `SpotifyCares` — **Suitable**

- ✅ Excellent multi-turn volume (10,500)
- ✅ Large customer base (28,304) — diverse intents
- ✅ High response rate (100.0%)
- ✅ Adequate conversation depth (avg 3.2)

### 5. `AmericanAir` — **Suitable**

- ✅ Excellent multi-turn volume (11,577)
- ✅ Large customer base (23,307) — diverse intents
- ✅ High response rate (99.7%)
- ✅ Adequate conversation depth (avg 3.3)

### 6. `Delta` — **Suitable**

- ✅ Excellent multi-turn volume (11,146)
- ✅ Large customer base (23,672) — diverse intents
- ✅ High response rate (99.2%)
- ✅ Adequate conversation depth (avg 3.4)

### 7. `comcastcares` — **Suitable**

- ✅ Excellent multi-turn volume (8,793)
- ✅ Large customer base (23,453) — diverse intents
- ✅ High response rate (99.9%)
- ✅ Adequate conversation depth (avg 3.0)

### 8. `TMobileHelp` — **Suitable**

- ✅ Excellent multi-turn volume (8,620)
- ✅ Large customer base (21,639) — diverse intents
- ✅ High response rate (100.0%)
- ✅ Adequate conversation depth (avg 3.6)

### 9. `Tesco` — **Suitable**

- ✅ Excellent multi-turn volume (11,629)
- ✅ Large customer base (17,216) — diverse intents
- ✅ High response rate (99.1%)
- ✅ Good conversation depth (avg 4.4)

### 10. `SouthwestAir` — **Suitable**

- ✅ Excellent multi-turn volume (7,231)
- ✅ Large customer base (20,798) — diverse intents
- ✅ High response rate (99.7%)
- ✅ Adequate conversation depth (avg 3.0)

### 11. `VirginTrains` — **Suitable**

- ✅ Excellent multi-turn volume (9,184)
- ✅ Large customer base (13,460) — diverse intents
- ✅ High response rate (99.9%)
- ✅ Good conversation depth (avg 4.4)

### 12. `British_Airways` — **Suitable**

- ✅ Excellent multi-turn volume (8,829)
- ✅ Large customer base (14,932) — diverse intents
- ✅ High response rate (99.9%)
- ✅ Adequate conversation depth (avg 3.7)

### 13. `Ask_Spectrum` — **Suitable**

- ✅ Excellent multi-turn volume (6,559)
- ✅ Large customer base (18,778) — diverse intents
- ✅ High response rate (99.7%)
- ✅ Adequate conversation depth (avg 3.2)

### 14. `XboxSupport` — **Suitable**

- ✅ Excellent multi-turn volume (8,395)
- ✅ Large customer base (15,232) — diverse intents
- ✅ High response rate (99.6%)
- ✅ Good conversation depth (avg 4.3)

### 15. `sprintcare` — **Suitable**

- ✅ Excellent multi-turn volume (6,382)
- ✅ Large customer base (14,759) — diverse intents
- ✅ High response rate (99.9%)
- ✅ Adequate conversation depth (avg 4.0)

### 16. `hulu_support` — **Suitable**

- ✅ Excellent multi-turn volume (5,897)
- ✅ Large customer base (14,302) — diverse intents
- ✅ High response rate (99.9%)
- ✅ Adequate conversation depth (avg 3.3)

### 17. `UPSHelp` — **Suitable**

- ✅ Excellent multi-turn volume (5,349)
- ✅ Large customer base (15,723) — diverse intents
- ✅ High response rate (99.8%)
- ✅ Adequate conversation depth (avg 2.9)

### 18. `ATVIAssist` — **Suitable**

- ✅ Excellent multi-turn volume (5,461)
- ✅ Large customer base (16,964) — diverse intents
- ✅ High response rate (98.9%)
- ✅ Good conversation depth (avg 4.3)

### 19. `GWRHelp` — **Suitable**

- ✅ Excellent multi-turn volume (6,949)
- ✅ Large customer base (8,158) — diverse intents
- ✅ High response rate (99.9%)
- ✅ Good conversation depth (avg 4.4)

### 20. `ChipotleTweets` — **Suitable**

- ✅ Adequate multi-turn volume (4,870)
- ✅ Large customer base (15,151) — diverse intents
- ✅ High response rate (100.0%)
- ✅ Adequate conversation depth (avg 2.9)

---

## Recommended Brands for SupportProof

Based on the analysis above, the top 3 brands are:

### Recommendation 1: `AmazonHelp`

| Metric | Value |
|--------|-------|
| Total tweets | 373,494 |
| Inbound (customer) tweets | 203,654 |
| Outbound (brand) tweets | 169,840 |
| Unique customers | 73,457 |
| Complete conversations | 82,534 |
| Multi-turn conversations | 51,244 |
| Average conversation length | 4.53 |
| Response rate | 100.0% |
| Quality score | 0.9375 |

**Why this brand:**

- 51,244 multi-turn conversations comfortably exceed the 150–250 golden-set requirement, leaving room for stratified sampling.
- 73,457 unique customers provide a broad distribution of intents for taxonomy discovery.
- 100.0% response rate means the majority of customer queries have brand responses available for resolution retrieval.
- Average conversation length of 4.5 messages indicates substantive back-and-forth, useful for escalation analysis.

### Recommendation 2: `AppleSupport`

| Metric | Value |
|--------|-------|
| Total tweets | 238,848 |
| Inbound (customer) tweets | 131,988 |
| Outbound (brand) tweets | 106,860 |
| Unique customers | 79,604 |
| Complete conversations | 80,702 |
| Multi-turn conversations | 28,140 |
| Average conversation length | 2.96 |
| Response rate | 99.9% |
| Quality score | 0.8089 |

**Why this brand:**

- 28,140 multi-turn conversations comfortably exceed the 150–250 golden-set requirement, leaving room for stratified sampling.
- 79,604 unique customers provide a broad distribution of intents for taxonomy discovery.
- 99.9% response rate means the majority of customer queries have brand responses available for resolution retrieval.

### Recommendation 3: `Uber_Support`

| Metric | Value |
|--------|-------|
| Total tweets | 128,443 |
| Inbound (customer) tweets | 72,173 |
| Outbound (brand) tweets | 56,270 |
| Unique customers | 39,870 |
| Complete conversations | 41,923 |
| Multi-turn conversations | 15,088 |
| Average conversation length | 3.07 |
| Response rate | 100.0% |
| Quality score | 0.5321 |

**Why this brand:**

- 15,088 multi-turn conversations comfortably exceed the 150–250 golden-set requirement, leaving room for stratified sampling.
- 39,870 unique customers provide a broad distribution of intents for taxonomy discovery.
- 100.0% response rate means the majority of customer queries have brand responses available for resolution retrieval.
- Average conversation length of 3.1 messages indicates substantive back-and-forth, useful for escalation analysis.
