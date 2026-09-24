# SupportProof Taxonomy Review

**PROPOSED TAXONOMY — REQUIRES HUMAN REVIEW**

## Why Previous Approaches Were Rejected
- **V1 (TF-IDF + K-Means)**: Grouped messages purely by shared words rather than meaning (e.g. 'Account Issue' absorbed anything with the word 'account'). Resulted in ~49% of data marked 'Other' and semantically incoherent clusters.
- **V2 (Semantic Concept Features)**: A step up, grouping by operational concepts (delay, return, refund). However, it forced overlapping issues together and lacked strict operational boundaries, resulting in ~50% 'Other' and false positives in overlapping categories (e.g., late deliveries clustered with lost deliveries).

## Operational Taxonomy Approach (V3)
This taxonomy is built strictly on *operational boundaries*. A message is assigned to an intent only if a human agent would perform a distinctly different workflow to resolve it.

**Total Analyzed Sample:** 50,000
**Estimated Coverage:** 28.8%
**Other / Unclear:** 71.2%

## Detailed Taxonomy Definitions

### Delivery Delay (`delivery_delay`)
- **Estimated Prevalence**: 4.4%
- **Recommended Action**: **KEEP**
- **Description**: Customer says an expected delivery is late.
- **IN SCOPE**:
  - Customer says an expected delivery is late.
  - Customer says promised delivery date has passed.
- **OUT OF SCOPE**:
  - Customer only asks where the package is and the delivery date has not passed.
  - Customer says tracking says 'delivered' but they did not receive it.
- **Confusable Intents**: order_tracking, missing_delivery

**Representative Examples:**
- "@AmazonHelp He said the latest they would arrive today and it never showed up. So I was just on the  phone to CS and the lady said if I wanted to"
- "Super aggravating knowing that since my @115821 orders from yesterday were shipped via AMZL US, they are guaranteed to be late."
- "@AmazonHelp Here are the last several orders. Granted some were over weekends so they look "late" and a couple were early, but look at how many have not arrived in time. This is only a small fraction of the 44 orders I have made in the last 6 months. https://t.co/BDBSGgmupb"
- "Thanks @115821 @amazonhelp for the delay in shipping. I'm a prime member for 2 day shipping, not 3-4 days. Ridiculous"
- "@115850 As a Amazon prime customer there is no diffrence of Shoppers. Still waiting for shipment from week even @23295 Ship it sooner then you guys. #Amazon #Fail Order date  21-Nov-2017  Order #  171-0390550-6849137 https://t.co/qvmd7551YX"

**Ambiguous / False Positive Candidates:**
- "@115830 Still waiting for a parcel , and the postman been and gone so obv being delivered by Amazon , use Royal Mail it's quicker !!!!!!!"
- "So @116090 shipped my latest order using #intelcom and yet again those crooks claim to have delivered - odd as I didn't get my order."
- "@115821 Ontrac delivered pkg @ 12:41am Tue. Woke up whole household. Don’t you think it’s a little late and unsafe for the delivery person?"

---

### Order Tracking (`order_tracking`)
- **Estimated Prevalence**: 3.3%
- **Recommended Action**: **KEEP**
- **Description**: Customer asks for tracking/status/location.
- **IN SCOPE**:
  - Customer asks for tracking link, status, or location of their order.
- **OUT OF SCOPE**:
  - Delivery date has already passed (delay).
  - Package is marked delivered but not received (missing).
- **Confusable Intents**: delivery_delay, missing_delivery

**Representative Examples:**
- "@AmazonHelp Really I'd just like an update on where it is now"
- "@115850 Poor service~Prime Customer; Wrong number provided to track courier and Amazon rep on call says can't do anything abt it!!!!"
- "@AmazonHelp Yup, figured as much - just worried when folks who pre-ordered after me were getting delivery updates for a limited item kind of thing"
- "@AmazonHelp I want resolution not updates, i have 'n' number of updates on e-mail which guys dont have guts to put on twitter to avoid getting exposed"
- "@293549 Hi there. If you need assistance with your delivery, please DM us your tracking # &amp; contact info. ^KS https://t.co/wKJHDXWGRQ"

**Ambiguous / False Positive Candidates:**
- "@AmazonHelp all the packages to Puerto Rico are being delayed due to “Preparing for shipment” status in Orders &gt;:("
- "@AmazonHelp I didn't get my product, but delivery status shows delivered. That was intentionally updated by delivery boy and he denied to deliver me, he replied that he is not in my area. I am prime member and helpless after 24 hours of this incident."
- "@AmazonHelp hi there, we placed on order on Amazon Prime to be delivered today but it hasn't arrived. Tracking says "Parcel left the carrier facility" since 10am and it's now 8pm"

---

### Missing Delivery (`missing_delivery`)
- **Estimated Prevalence**: 0.6%
- **Recommended Action**: **KEEP**
- **Description**: Package is marked delivered but customer did not receive it.
- **IN SCOPE**:
  - Package is marked delivered but customer says they did not receive it.
  - Package appears stolen or lost.
- **OUT OF SCOPE**:
  - Package is merely late but still in transit.
- **Confusable Intents**: delivery_delay, wrong_item

**Representative Examples:**
- "@AmazonHelp Again false promise coustmer care. They told me I will get my product yesterday. Till now I didn't received"
- "@AmazonHelp traking no #521656283512 shipment didn't received yet."
- "What the hell is this @115850  Never received this and App shows this is delivered Wrost customer service https://t.co/a8o0Sjs0nu"
- "@115850 - why are you delivering empty boxes?? Where is the content of the box that I paid for!! Your customer service takes for ever to resolve a problem. Not fair ! Not cool !"
- "@115821 Hi! My husband and I registered for @95179 months ago, but never received that welcome box we've heard about.  Any tips? :)"

**Ambiguous / False Positive Candidates:**
- "@AmazonHelp Is says delivered wednesday which it wasn't. Got another cd supposedly coming today... whats the point in pre-ordering them from you if they dont turn up on release date? A week lates no good."
- "@115850 I would like to complain against the delivery agent. He called me and I told him I’m home and 2 mins later it says delivered but no one came to my house https://t.co/hrpe3cs754"
- "I am getting very upset and disappointed with @115821 prime delivery lately. First off, they never follow my directions and leave packages at my front door to get stolen. Second, they never arrive by the second day even though it says it’s going to.   Get your shit together."

---

### Wrong Item (`wrong_item`)
- **Estimated Prevalence**: 0.1%
- **Recommended Action**: **MERGE (with damaged_item -> issue_with_received_item)**
  - *Rationale*: Differentiating between a wrong item and a damaged item usually leads to the exact same support workflow (replace or refund).
- **Description**: Customer received an item different from what they ordered.
- **IN SCOPE**:
  - Customer received the wrong item, size, or color.
- **OUT OF SCOPE**:
  - Customer wants to return a correctly fulfilled item because they changed their mind.
- **Confusable Intents**: return_request, missing_delivery

**Representative Examples:**
- "@AmazonHelp Doesn't help - i live in spain and returning items is a hassle and expensive - i was sent the incorrect item so would like the right item sent . Pls link me to the email assistance"
- "@AmazonHelp And they you completely sent me the wrong item"
- "@AmazonHelp It's 7 different items and I've already placed the order. Should I DM you the order number?"
- "when you realize you order the wrong item on amazon and send a cancellation request than 2 days after you send it it ships and 5 minutes after it ships they say they can't refund it because they shipped it and the carrier cant find it... classy amazon classy 👌"
- "@AmazonHelp Received the wrong item from an Amazon prime retailer. I was trying to re-order the item again so it arrives on time. It’s a birthday gift."

**Ambiguous / False Positive Candidates:**
- "@AmazonHelp (1) Had rep Michelle D. said I would receive gift card refund for wrong item and was broken in 1-2hrs, it's been over 2hrs."

---

### Damaged Item (`damaged_item`)
- **Estimated Prevalence**: 1.2%
- **Recommended Action**: **MERGE (with wrong_item -> issue_with_received_item)**
  - *Rationale*: Differentiating between a wrong item and a damaged item usually leads to the exact same support workflow (replace or refund).
- **Description**: Customer received a damaged or defective item.
- **IN SCOPE**:
  - Item arrived broken, scratched, torn, or defective.
- **OUT OF SCOPE**:
  - Item was stolen or missing entirely.
- **Confusable Intents**: return_request

**Representative Examples:**
- "@115850  Broken product received for order 408-7624111-6539547  Looking for replacement, cu care was unable to register replace. Do check https://t.co/b9wltyKr7f"
- "Received the damaged product with so mny prms #home_theater . Wanna change. Need #help. #HowTo  @115850 @123644"
- "@AmazonHelp can u please help me coz ur bot is broken af https://t.co/RSytYC1Rwp"
- "@AmazonHelp I spent $400 on 1 item. What they sent was broken. Now I'm responsible for paying shipping back to them?? No f*cking way!!"
- "every time i order from a third-party from @115821 my shit gets lost, damaged, or fake delivered. sad."

**Ambiguous / False Positive Candidates:**
- "@115821 is really losing my trust lately. Since all of the recent things I’ve ordered have been wrong and/or defective #veryunsatisfied."
- "@AmazonHelp I was charged a return shipping fee on an order that was a (Defective/Wrong Item Shipped TO ME) and was told over the phone that the fee would be refunded, how long would that take?"
- "@AmazonHelp I recd wrong &amp; defective item last yr, made return request within 3days, the courier person never arrived. CC dragged me along, nw no reply."

---

### Return Request (`return_request`)
- **Estimated Prevalence**: 1.9%
- **Recommended Action**: **KEEP**
- **Description**: Customer wants to return an item.
- **IN SCOPE**:
  - Customer asks how to return an item or requests a return label.
- **OUT OF SCOPE**:
  - Customer is only asking for a refund without returning (e.g. for a digital service).
- **Confusable Intents**: refund_request, wrong_item, damaged_item

**Representative Examples:**
- "@AmazonHelp Not acceptable for me to have the trouble of returning a clearly faulty item that shouldn’t have been sent out. The Packer should’ve seen it"
- "@115850 i m unable to return the product on amazon.?? they should listen the customer first completely."
- "@AmazonHelp Yes the shoes were wet and smelled of mold.  I have already returned it.  Just thought this level of bad needed to be pointed out."
- ".@AmazonHelp You say you "extended my extended". I don't know what that means or how it helps me. Do I have to return the items that I did not get? Will my packages still get carried by AMZL? All I have is hassle and all you did was send me a nonsense sentence and that you care."
- "Again I am asking is there any pickup policy of Amazon. How much time does it take to pickup the mobile for return @115850 @amazonHelp https://t.co/vZGMadAm3T"

**Ambiguous / False Positive Candidates:**
- "@AmazonHelp Acc to policy nutritional items cannot be returned, but when you send a completely wrong product, what choice does a user have? Pls refund."
- "@115850  i wanted to return my order but no one came for receive order ,, ur service is so slow, plz quick send ur agent , and refund me https://t.co/XpCaIl6704"
- "@115850 we have returned one faulty item and received a mail from Amazon that they have received the product. But,no refund or replacement"

---

### Refund Request (`refund_request`)
- **Estimated Prevalence**: 4.4%
- **Recommended Action**: **KEEP**
- **Description**: Customer is asking for a refund or money back.
- **IN SCOPE**:
  - Customer asks for a refund, credits, or questions a charge.
- **OUT OF SCOPE**:
  - Customer is initiating a physical return (which implies a refund).
- **Confusable Intents**: return_request, cancel_order

**Representative Examples:**
- "@AmazonHelp Have not signed up for Amazon Prime services in any shape or form. Please forward a contact no and person who can rectify and refund this."
- "@AmazonHelp i bought my wedding champagne through you, it was supposed to be delivered on Sunday, however i was informed that the driver crashed and therefore couldn't deliver it. I was then told i was being refunded for the amount and i had to make the order again"
- "@AmazonHelp @115850 i have other owrk also in my life Amazon: We are here to take care of the issue. Me: i dont want to scold u..pls dnt come to a level that i start abusing u Amazon: You need not worry about it.. Me: refund my money now..i dnt blv on u any more Amazon: I am sorry we cannot issue r"
- "@AmazonHelp It was going into investigation as an unauthorised purchase and my account was being frozen, I’ve heard nothing since. Apparently if the third party were refusing to refund the money Amazon were going to look into giving me the money back. Thanks for the quick reply though."
- "@AmazonHelp Looks like everything is settled, just need to ship the item back. I'll have to look for the correct item again once I have my refund."

**Ambiguous / False Positive Candidates:**
- "@AmazonHelp I need your explanation why there is a delay in refunding my amount and also why the order was not delivered and returned to seller!"
- "@AmazonHelp If it arrives tomorrow I’m going to return it and ask for a full refund"
- "@AmazonHelp Take it back from my home, i won't parcel it😡. Send my return order or refund me"

---

### Cancel Order (`cancel_order`)
- **Estimated Prevalence**: 0.1%
- **Recommended Action**: **KEEP**
- **Description**: Customer wants to cancel an order.
- **IN SCOPE**:
  - Customer wants to cancel an order that hasn't shipped yet.
- **OUT OF SCOPE**:
  - Customer wants to return an order that already arrived.
  - Customer wants to cancel Prime membership.
- **Confusable Intents**: refund_request, return_request, account_prime

**Representative Examples:**
- "@AmazonHelp @115850 @115851 So I'll repeat, I will NOT cancel my order. Why should I? You should rather focus on sourcing the product &amp; delivering it to customer asap instead of asking him to cancel. Or pay me the excess amount I'll have to pay if I buy from someone else &amp; if you want me to cancel from you."
- "@AmazonHelp I have  to get the Item today itself.  I am leaving from home tommorrow. Else I hav to cancel my order."
- "@AmazonHelp @115850 shields dubious, fake &amp; fraudulent sellers. Asks customer to cancel order without taking any action on seller #BoycottAmazon"
- "@AmazonHelp  Order# 402-7551271-6222767 Please cancel my order as  it is placed mistakenly"
- "@AmazonHelp I hv requested my order cancellation but customer care cancelled my all order  really pathetic U cannot cancel my orders without my permissi"

**Ambiguous / False Positive Candidates:**
- "@AmazonHelp Only options are track return cancel order. Doesn't help as I need to complain I didn't get delivery https://t.co/WooFqWFCBq"
- "@AmazonHelp Have done that - for the 3rd time. It's passed useful now, I'm going to have to cancel my order and be satisfied that I'll never be able to get into my Amazon account, and not get a new camera until I return home in 3 months."
- "@AmazonHelp @115850  there is no CANCEL ORDER tab in my app. How can i return the item for the refund, when I have not at all received it?"

---

### Account & Prime (`account_prime`)
- **Estimated Prevalence**: 3.9%
- **Recommended Action**: **KEEP**
- **Description**: Issues related to account access or Prime membership.
- **IN SCOPE**:
  - Login, password, account lockouts, Prime membership cancellation or benefits.
- **OUT OF SCOPE**:
  - General website navigation issues not tied to account access.
- **Confusable Intents**: cancel_order, technical_issue

**Representative Examples:**
- "@AmazonHelp is this real? Logged into my account and it says I’m not a prime member which would be right? https://t.co/I3kmoNx1v6"
- "@AmazonHelp Tried placing an order on amazon.fr and amazon.es for snes classic. Order cancelled and accounts closed. Multiple times."
- "@AmazonHelp my account is having major issues, changing my password has not helped"
- "@AmazonHelp Yes but I need someone take the block off my account"
- "I’ve been trying to unblock my @115821 account for 1+ week. Phone calls, emails.Still not get why my account was suddenly blocked! 1/2"

**Ambiguous / False Positive Candidates:**
- "@AmazonHelp There isn’t a status, you are asking for my payment details again, this will be the 7th time in 24 hours. Have spoke with bank, payment has left my account. I have tried to cancel order numerous times but there’s a technical fault"

---

### Technical Issue (`technical_issue`)
- **Estimated Prevalence**: 8.6%
- **Recommended Action**: **KEEP**
- **Description**: Issues with Amazon app, website, or digital devices.
- **IN SCOPE**:
  - App crashes, website errors, Kindle, Fire TV, or Alexa issues.
- **OUT OF SCOPE**:
  - Account lockouts (Account & Prime).
- **Confusable Intents**: account_prime

**Representative Examples:**
- "@AmazonHelp hi, I've recently bought Kindle Unlimited. Aren't all books supposed to be available, cos some only give me an option to buy?"
- "@115821 I'm disappointed. I paid for my package to be here today yet you haven't even shipped it. Very disappointing as a prime member."
- "@AmazonHelp That I paid overnight shipping for on SUNDAY. That still hasn’t shipped. Crappy, crappy customer service."
- "@AmazonHelp le numero  du service  après  vente est indisponible   comment je les rappelles"
- "Amazon PrimeとKindle Unlimitedは一つになったのかな？ Prime Reading？"

**Ambiguous / False Positive Candidates:**
- "@AmazonHelp Unable to login. Changed password many times. It says wrong password.  Called amazon help from Friend's app. I was told that I will receive mail about my account issues in max 48 hours . 4 days passed since. account not active."
- "@AmazonHelp Wait... you guys have it. Just that the first run of the app, asked me to enter my email/password. Found the easier way the second time."
- "@AmazonHelp email received and I've read it. There is no solution 4 my problem. I just want my account unblocked. It is an error frm ur end."

---

### Gift Card & Promotion (`gift_card_promotion`)
- **Estimated Prevalence**: 0.4%
- **Recommended Action**: **KEEP**
- **Description**: Issues with gift cards, promotional codes, or discounts.
- **IN SCOPE**:
  - Claim codes not working, missing promotional discounts, gift card balances.
- **OUT OF SCOPE**:
  - Regular refunds to credit cards.
- **Confusable Intents**: refund_request

**Representative Examples:**
- "@AmazonHelp one of the customer reps answer: (I do understand but as we all have the same system and we all do follow the same protocol. So system is not allowing us for the shipping upgrade as well as he discounts.)"
- "@AmazonHelp being given the option to sign up to a discounted amazon prime but only if i put in a baby name? No context on this screen? https://t.co/jmSixlG66B"
- "@AmazonHelp When it's mentioned an amount in lightning deal, on check out it mentions something else. when I go back , it shows again the discount"
- "@AmazonHelp I already did but again received false assurance instead of the Gift card"
- "@AmazonHelp On some gift cards the glue is too strong on the peel up strip and it peels up EVERY number on the claim code but one...."

---

### Other / Unclear (`other_or_unclear`)
- **Estimated Prevalence**: 71.2%
- **Recommended Action**: **KEEP**
- **Description**: Messages that do not confidently fit into any strictly defined operational intent.
- **IN SCOPE**:
  - Ambiguous complaints, multi-intent requests lacking a primary focus, highly specific outliers.
- **OUT OF SCOPE**:
  - Clear, actionable requests covered by specific intents.
- **Confusable Intents**: None

**Representative Examples:**
- "@AmazonHelp I found the package at my neighbor's house.  Never looking at the label: they opened it and said, "I don't have a cat.". need2 Geotag photo!"
- "@672345 @AmazonHelp La han cagao pero bien!"
- "@116316 Ich sehe gerade, dass eine meiner Bestellungen als "Zugestellt" markiert ist, die bei uns allerdings nicht angekommen ist. Irgendetwas ist da falsch gelaufen und ich finde leider nicht, wo ich das auf der Seite melden kann. Hilfe?!"
- "@AmazonHelp Non plus 😢pas la du week-end. Si je peux par contre le mettre en relais colis à la place je peux attendre, sinon autant annuler"
- "@AmazonHelp Not very good customer service. Also emailed the complaints email address i was given and not even received an automated response. Care to help?"

---
