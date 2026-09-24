# SupportProof Annotation Guide (v0.1)

This guide defines the rules for manually assigning the `human_intent` and `human_escalate` fields in the golden evaluation set. 
The golden set contains 200 real, noisy customer interactions. Your job is to assign the single most accurate intent and decide whether human intervention (escalation) is required.

## 1. Intent Definitions

| Intent | Description |
| :--- | :--- |
| **technical_issue** | App crashes, website errors, digital device problems (Kindle, Fire, Echo), or payment processing technical errors. |
| **refund_request** | Customer explicitly asks for a refund, credits, or disputes a charge. |
| **delivery_delay** | Customer complains that an expected delivery is late, delayed, or missed a promised delivery date. |
| **account_prime** | Issues related to account access (login, password, lockouts) or Prime membership (benefits, cancellation). |
| **order_tracking** | Customer asks for the location or status of their order, or asks for a tracking link. |
| **return_request** | Customer asks how to return a physical item, requests a return label, or asks about a return policy. |
| **issue_with_received_item** | Customer received their order, but it is the wrong item, damaged, defective, or missing parts. |
| **missing_delivery** | Package is marked as "delivered" but the customer did not receive it, or the package was confirmed stolen/lost. |
| **gift_card_promotion** | Issues with gift cards, claim codes, promo codes, or applying a discount. |
| **cancel_order** | Customer wants to cancel an order (that presumably has not shipped yet). |

## 2. Handling the "other_or_unclear" Intent

Use `other_or_unclear` ONLY when:
- The message is purely noise, a joke, or meaningless.
- The message is praise or a general comment without a support request.
- The message is too ambiguous to confidently assign to any of the 10 core intents, *even after reading the previous turns*.
- The message is a highly specific outlier issue that clearly does not fit the taxonomy.

Do NOT use `other_or_unclear` just because a message is difficult. Try to find the closest core intent first.

## 3. Inclusion / Exclusion Rules & Distinguishing Intents

### Handling Multiple Issues
If a customer brings up multiple issues (e.g., "My item is damaged and I want a refund"), assign the intent that represents the **root cause** or the **primary operational action**.
- Cause vs Action: Usually, label the cause. If the item is damaged, label `issue_with_received_item`. A refund is just the consequence of that cause.
- Exception: If they explicitly ask for a specific operational action ("cancel my order"), that action intent (`cancel_order`) is very strong.

### Distinctions
- **`delivery_delay` vs `order_tracking`**
  - Use `delivery_delay` if the tone is a complaint about lateness or a missed date.
  - Use `order_tracking` if it's purely informational ("Where is it?", "Can I have tracking?").
- **`delivery_delay` vs `missing_delivery`**
  - Use `missing_delivery` ONLY if the tracking falsely says "delivered" or the package is confirmed stolen. 
  - If it's just really late, use `delivery_delay`.
- **`refund_request` vs `return_request`**
  - If they want to send a physical item back, use `return_request`.
  - If they just want their money back (e.g. for a digital service, a late fee, or an item they don't have to return), use `refund_request`.
- **`issue_with_received_item` vs `return_request`**
  - Label the cause. If they mention the item is wrong/damaged, label `issue_with_received_item`.
  - If they just say "I want to return this", use `return_request`.
- **`account_prime` vs `technical_issue`**
  - Login/password/account lockouts = `account_prime`.
  - App crashing, website broken, Kindle not syncing = `technical_issue`.
- **`gift_card_promotion` vs `refund_request`**
  - If it involves applying a code, discount, or gift card balance, use `gift_card_promotion`.
  - Standard credit card refunds = `refund_request`.

## 4. Handling Missing Context
Use the `previous_turns` field to understand the `customer_message`. If the message is a reply like "Yes that would be great" and the previous turn was the brand asking "Would you like a refund?", the intent is `refund_request`. If there is absolutely no context and the message is ambiguous, use `other_or_unclear`.

## 5. Escalation (`human_escalate`) Rules

The `human_escalate` field should be a boolean (`true` or `false`). 
**Be conservative.** Do not escalate simply because the customer is unhappy or frustrated.

Mark `human_escalate = true` ONLY when:
- The issue requires investigating specific account/order details that a generic FAQ AI cannot do.
- There are repeated, failed attempts to resolve the issue in the past.
- The customer is highly frustrated *after* previous support attempts.
- The request is unusual, unsupported, or a legal/safety threat.
- The issue cannot be safely answered from the available historical evidence, or requires a sensitive action that a public Twitter response cannot complete.

If the AI could theoretically answer it (e.g., "Here is a link to track your order"), set `human_escalate = false`.
