# Dataset Inspection Report

**File encoding:** utf-8
**Number of rows:** 2,811,774
**Number of columns:** 7

## Column Names

1. `tweet_id`
2. `author_id`
3. `inbound`
4. `created_at`
5. `text`
6. `response_tweet_id`
7. `in_response_to_tweet_id`

## Expected Columns Check

- `tweet_id`: ✅ present
- `author_id`: ✅ present
- `inbound`: ✅ present
- `created_at`: ✅ present
- `text`: ✅ present
- `response_tweet_id`: ✅ present
- `in_response_to_tweet_id`: ✅ present

## Inferred Data Types

| Column | Type |
|--------|------|
| `tweet_id` | int |
| `author_id` | str |
| `inbound` | bool |
| `created_at` | str |
| `text` | str |
| `response_tweet_id` | str |
| `in_response_to_tweet_id` | int |

## Missing-Value Counts

| Column | Missing |
|--------|---------|
| `tweet_id` | 0 |
| `author_id` | 0 |
| `inbound` | 0 |
| `created_at` | 0 |
| `text` | 0 |
| `response_tweet_id` | 1,040,629 |
| `in_response_to_tweet_id` | 794,335 |

## Duplicate Rows

**Duplicate-row count:** 0

## Unique Tweet IDs

**Unique tweet IDs:** 2,811,774

## Inbound vs Outbound Tweets

- **Inbound:** 1,537,843
- **Outbound:** 1,273,931

## First 5 Rows

| `tweet_id` | `author_id` | `inbound` | `created_at` | `text` | `response_tweet_id` | `in_response_to_tweet_id` |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | sprintcare | False | Tue Oct 31 22:10:47 +0000 2017 | @115712 I understand. I would like to assist you. We would need to get you in... | 2 | 3 |
| 2 | 115712 | True | Tue Oct 31 22:11:45 +0000 2017 | @sprintcare and how do you propose we do that |  | 1 |
| 3 | 115712 | True | Tue Oct 31 22:08:27 +0000 2017 | @sprintcare I have sent several private messages and no one is responding as ... | 1 | 4 |
| 4 | sprintcare | False | Tue Oct 31 21:54:49 +0000 2017 | @115712 Please send us a Private Message so that we can further assist you. J... | 3 | 5 |
| 5 | 115712 | True | Tue Oct 31 21:49:35 +0000 2017 | @sprintcare I did. | 4 | 6 |
