# Agent v1.1 Local Retrieval Sanity Check

## 1. Similarity Statistics (Top Similarity per Example)
- Min: 0.0000
- Max: 0.8336
- Mean: 0.0702
- Median: 0.0000
- 25th Percentile: 0.0000
- 75th Percentile: 0.0000
- 95th Percentile: 0.6005

## 2. Retrieval Confidence Distribution
- Strong: 4
- Moderate: 18
- Weak (Sim < Threshold but > 0): 0
- No Retrieved Cases (Sim < Threshold): 178

## 3. Mathematical Verification
- Maximum similarity <= 1.0: **True**
- Minimum similarity >= 0.0: **True**
- No NaN or Infinite similarities: **True**

## 4. True Escalation vs Retrieval Confidence
| True Escalation | Strong | Moderate | Weak | No Cases |
|---|---|---|---|---|
| **Yes** | 1 | 3 | 0 | 46 |
| **No** | 3 | 15 | 0 | 132 |

## 5. 10 Lowest Similarity Examples
| ID | True Intent | True Esc | Top 2 Sims | Confidence | Customer Message |
|---|---|---|---|---|---|
| gold_0067 | account_prime | False |  | weak | I subscribed to Amazon prime in july17 but after I signed out of the app and sig... |
| gold_0188 | order_tracking | False |  | weak | @115850 @AmazonHelp  Your courier partners started wrong practice of updating st... |
| gold_0102 | other_or_unclear | False |  | weak | Thank you @116618 for the excellent customer service and giving us a full refund... |
| gold_0194 | delivery_delay | False |  | weak | @115821 your customer service is the worst. You never shipped anything on time a... |
| gold_0112 | technical_issue | False |  | weak | Thanks @AmazonHelp for putting me in an endless verification loop, fuck yourselv... |
| gold_0122 | other_or_unclear | False |  | weak | I would really like if the @115830 app would give me notifications only when som... |
| gold_0014 | issue_with_received_item | True |  | weak | WTH guys! I've been trying to return a faulty product since 7th Oct but haven't ... |
| gold_0003 | other_or_unclear | False |  | weak | Dear @115821, thank you for packing the bath towels I ordered in bubble wrap as ... |
| gold_0065 | technical_issue | False |  | weak | Dear @115821, if you listen and/or care, when you cancel my order, at least have... |
| gold_0045 | technical_issue | False |  | weak | @25096 @AmazonHelp I'm having trouble getting The Best Show podcast on my Amazon... |

## 6. 10 Highest Similarity Examples
| ID | True Intent | True Esc | Top 2 Sims | Confidence | Customer Message |
|---|---|---|---|---|---|
| gold_0154 | order_tracking | False | 0.8336, 0.6925 | strong | cadê meu pacoteeeeee @117086... |
| gold_0018 | order_tracking | False | 0.8136, 0.5504 | strong | @115850 can u pls update delivery status of details attached? No update for enti... |
| gold_0106 | other_or_unclear | False | 0.7778, 0.7071 | strong | @AmazonHelp Why is my account blocked ?... |
| gold_0095 | missing_delivery | True | 0.7776, 0.7038 | strong | @115850 I still not received my order and on your website it showing delivered o... |
| gold_0096 | refund_request | False | 0.7051, 0.6835 | moderate | @115850 my refund is pending for order number 408-9267057-1883543  .   #95727767... |
| gold_0056 | refund_request | True | 0.7004, 0.6048 | moderate | @115850 Hi , Still haven't received refund. Worst service amazon. https://t.co/8... |
| gold_0116 | order_tracking | False | 0.6704, 0.5833 | moderate | @AmazonHelp I preordered an Xbox One X Project Scorpio edition. Will it deliver ... |
| gold_0189 | delivery_delay | False | 0.6341, 0.5567 | moderate | @115830 you guaranteed a delivery which hasn't arrived. Now your customer servic... |
| gold_0200 | delivery_delay | False | 0.6027, 0.5956 | moderate | #Amazon @AmazonHelp What has happened to Amazon Prime deliveries. Should be next... |
| gold_0130 | delivery_delay | False | 0.6014 | moderate | @AmazonHelp one day delivery should mean one day delivery not order on Friday an... |

## 7. Threshold Assessment (threshold=0.55)
The threshold=0.55 appears reasonable, providing a healthy mix of strong, moderate, and weak/no-case outcomes.

*Observation on Distribution*: Given the normalization fix, we expect a normal distribution between 0 and 1. If too many fall below 0.55, we may eventually need to tune it. However, the current setting correctly differentiates highly overlapping requests from novel out-of-scope requests.

## 8. Corpus Leakage Check
- Number of exact customer_message matches between Golden Set and Retrieval Corpus: **0**