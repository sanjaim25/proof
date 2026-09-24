# Baseline Evaluation Results
Evaluated on 200 frozen golden examples.

## Summary Metrics

| System | Intent Accuracy | Intent Macro-F1 | Escalation Precision | Escalation Recall | Escalation F1 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Majority | 0.320 | 0.044 | 0.000 | 0.000 | 0.000 |
| TF-IDF | 0.320 | 0.252 | 0.286 | 0.240 | 0.261 |

## TF-IDF Retrieval Analysis
- **Below threshold (0.1)**: 0 (0.0%)
- **Incorrect Intent**: 136 (68.0%)

### Successful Retrievals (Examples)
**Example 1**
- **Customer**: @AmazonHelp hey guys, having an issue with a refund? I sent the item back almost two weeks ago and there's been no update on it.
- **Intent**: refund_request (Sim: 1.538)
- **Baseline Reply**: @756889 I'm sorry you haven't received your refund. We don't have access to your account via Twitter, but we'd like to help! Please reach out to us here: https://t.co/hApLpMlfHN ^ZW

**Example 2**
- **Customer**: @115821 i took your survey for the gift card and i’m really hoping it was fake cause in the end where you get a prize. how is it a prize if i have to pay for it and how is sex enhance and antiaging cream or even brain development a prize for a 19yr? who was your target audience?
- **Intent**: gift_card_promotion (Sim: 1.289)
- **Baseline Reply**: @148408 To verify if this was sent from Amazon, we recommend checking your Message Center here: https://t.co/GNYv5KTPY8. If it's not from us, the e-mail can be forwarded for investigation. More info is avail here: https://t.co/CiDPsASQLc ^EP

**Example 3**
- **Customer**: @115821 why cant i buy @119038 bits with the 10 dollar gift card i have in my accout?
- **Intent**: gift_card_promotion (Sim: 1.378)
- **Baseline Reply**: @763811 I get your concern regarding the purchase of the gift card. I'd like to inform you that unfortunately Amazon Pay balance cannot be used to purchase Amazon.in Gift Cards. Appreciate your understanding. ^EM


### Failed Retrievals (Examples)
**Example 1**
- **Customer**: I subscribed to Amazon prime in july17 but after I signed out of the app and signed in again after sometime, it is asking me again to pay for it. I need help @116618 @8623 @AmazonHelp
- **True Intent**: account_prime
- **Predicted Intent**: other_or_unclear (Sim: 1.388)

**Example 2**
- **Customer**: @115850 @AmazonHelp 
Your courier partners started wrong practice of updating status even before delivery. They marked my package delivered even though no courier boy has arrived in my society.
- **True Intent**: order_tracking
- **Predicted Intent**: other_or_unclear (Sim: 1.499)

**Example 3**
- **Customer**: @115821 your customer service is the worst. You never shipped anything on time anymore and you make it impossible to get customer service support.
- **True Intent**: delivery_delay
- **Predicted Intent**: other_or_unclear (Sim: 1.711)


## Limitations
- The Majority Baseline is trivial and entirely lacks context awareness.
- The TF-IDF baseline suffers from lexical mismatch (e.g. synonyms aren't matched).
- TF-IDF relies heavily on heuristic 'silver' labels applied to historical data, capping its theoretical maximum performance.
- Escalation heuristics based on historical conversation length are extremely noisy proxies for actual escalation requirements.