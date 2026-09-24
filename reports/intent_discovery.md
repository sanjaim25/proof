# Intent Discovery Report

**PROPOSED TAXONOMY — REQUIRES HUMAN REVIEW**

## Methodology
- **Sampling Strategy**: Filtered for valid lengths, removed duplicates, and deterministically sampled 3,000 customer messages.
- **Clustering**: Applied TF-IDF with stop-word removal followed by K-Means clustering (K=25) using cosine similarity (pure Python).
- **Taxonomy Generation**: Grouped clusters heuristically based on keywords to produce final proposed intents.

**Total Sampled:** 3,000
**Outliers (Noise/Unclustered):** 2 (0.1%)

## Proposed Final Taxonomy (8-15 Intents)

### Other (`other`)
- **Estimated Prevalence**: 48.9%
- **Description**: Customer inquiry related to: phone, care, la, product, said
- **In Scope**: Messages containing: phone, care, la, product, said
- **Out of Scope**: Other distinct issues
- **Common Keywords**: phone, care, la, product, said, ich, merci, take, nicht, ever
- **Confusable Intents**: None

**Examples:**
- "@115850  @115821 got fake product, trying to call Amazon and no one is answering the call. Great.."
- "@AmazonHelp Grazie, continuate cosi 👍"
- "@Tesco BEST CUSTOMER SERVICE TEAM EVER"
- "@5503 I’m enjoying the @128020  Experience on the @115833 dot. However, I’d prefer to stream it through @118117 speaker. Alexa can’t manage that, despite repeated attempts. During the most recent attempt, Alexa thought I wanted, um, this: https://t.co/VsWvhMHake"
- "Okay, @115821 was already awesome but their customer service is also amazing. So helpful!"


### Delivery Delay (`delivery_delay`)
- **Estimated Prevalence**: 14.0%
- **Description**: Customer inquiry related to: shipping, delivery, dear, arrived, youre
- **In Scope**: Messages containing: shipping, delivery, dear, arrived, youre
- **Out of Scope**: Other distinct issues
- **Common Keywords**: shipping, delivery, dear, arrived, youre, prime, time, day, return, parcel
- **Confusable Intents**: missing_delivery, order_tracking

**Examples:**
- "Dear @115821,  My bank account and I love you more and more with each passing day.💻💵🎄🎅🏻🎁 #ChristmasShoppingAlmostDone #MayHaveMoneyLeftOver"
- "Amazon Prime Now is really amazing. Just ordered something that will be at my house before I wake up tomorrow morning."
- "Okay, but if you can mark it as "delivered" 36 hours before actual delivery, can you understand how that looks super scummy/unhelpful? https://t.co/oeINRqSv3D"
- "@AmazonHelp Yea I'm aware of that we can't figure that until sell starts. Only thing is If it doesn't allows pune location 1/n"
- "Me when Amazon took their Prime money https://t.co/fIxjPmy5MS"


### Account Issue (`account_issue`)
- **Estimated Prevalence**: 13.3%
- **Description**: Customer inquiry related to: call, account, thank, link, app
- **In Scope**: Messages containing: call, account, thank, link, app
- **Out of Scope**: Other distinct issues
- **Common Keywords**: call, account, thank, link, app
- **Confusable Intents**: None

**Examples:**
- "@AmazonHelp Then you feed me auto responses and sance around every question i pose to you"
- "@AmazonHelp Yes an error message. My Kindle wasn’t downloading books so I reset it and deregistered it and now I can’t re-register it."
- "@AmazonHelp I hope so u will"
- "@AmazonHelp I have and none of those are the issue. The issue is the app on the Roku tv. I've had the TV 10 months. The app hasn't been usable"
- "@AmazonHelp Custom Dynamics Dynamic Ringz LED Turn Signal Inserts - Bullet style GEN200-AW-1157 https://t.co/wARwFlUgV6"


### Technical Issue (`technical_issue`)
- **Estimated Prevalence**: 5.9%
- **Description**: Customer inquiry related to: happened, getting, tomorrow, contacted, one
- **In Scope**: Messages containing: happened, getting, tomorrow, contacted, one
- **Out of Scope**: Other distinct issues
- **Common Keywords**: happened, getting, tomorrow, contacted, one, working, read, put, work, error
- **Confusable Intents**: None

**Examples:**
- "@468593 @AmazonHelp Sorry to chime in but the same thing has happened to me. Used to get stuff sat and sun now have to wait until Monday!"
- "@AmazonHelp Contacted them twice. No help."
- "Ordered a new Fire tablet from @115821 Black Friday Sale. Supposedly it will be delivered tomorrow, but hasn't even shipped yet. Apparently, they're going to just beam it directly to the local post office on the morning."
- "@AmazonHelp @469809 Same has happened to me. Useless"
- "@107085 @115821 @AmazonHelp I can't even put it in my cart--is it asking you to choose a country on the buy page?"


### Wrong Or Missing Item (`wrong_or_missing_item`)
- **Estimated Prevalence**: 5.8%
- **Description**: Customer inquiry related to: need, order, wrong, delivered, address
- **In Scope**: Messages containing: need, order, wrong, delivered, address
- **Out of Scope**: Other distinct issues
- **Common Keywords**: need, order, wrong, delivered, address
- **Confusable Intents**: None

**Examples:**
- "@115850 @AmazonHelp another pathetic issue Prime order showing delivered track# 449123579275 not done in actual https://t.co/Si8xFXWgMc"
- "I will NEVER EVER ORDER FROM @115821 AGAIN."
- "@116316 hi! I'm trying to cancel an order even before being processed but nobody is answering me :("
- "@AmazonHelp No it said order in 9hrs and it will be here Monday i ordered it and it said it’s coming Thursday . How dare y’all and i have amazon prime ."
- "@115850 Team,Kindly provide the investigation report tht how Order# 402-2926247-6753157 has been updated delivered without actual delivery"


### Returns And Refunds (`returns_and_refunds`)
- **Estimated Prevalence**: 5.1%
- **Description**: Customer inquiry related to: item, ordered, refund, want, dont
- **In Scope**: Messages containing: item, ordered, refund, want, dont
- **Out of Scope**: Other distinct issues
- **Common Keywords**: item, ordered, refund, want, dont
- **Confusable Intents**: cancel_order

**Examples:**
- "@AmazonHelp I can provide you the order number. But i dont want to switch this tweet as a customer chat support. My purpous of this tweet is to let know people how careless you becoming and disrespecting your customers now who has come trusting you these years."
- "Ordered 3x vinyl for my dad on @115821 but they sodding changed to CD?! Wtf?! Tech issue much?"
- "Made a purchase in @115821 for my son bday. I told seller I got 1of 3 items ordered, he tells me to chase after Amazon for a refund. I can't get a refund if I don't ship it back, but I never received them in the first place. Hello? #BadExperience #worstAmazonSeller #Amazon https://t.co/LFKgEDp0Jn"
- "@115830 this isn't the #XboxOneX I ordered https://t.co/BVStLQCpAA"
- "@115830 I pre ordered Battlefront 2 months ago, but you never sent me the lightsaber mastery starcard unlock code?"


### Order Tracking (`order_tracking`)
- **Estimated Prevalence**: 4.8%
- **Description**: Customer inquiry related to: still, says, today, tracking, waiting
- **In Scope**: Messages containing: still, says, today, tracking, waiting
- **Out of Scope**: Other distinct issues
- **Common Keywords**: still, says, today, tracking, waiting
- **Confusable Intents**: None

**Examples:**
- "@AmazonHelp That link says I have no orders. The email confirming it’s been shipped shows it’s out for delivery. I’m expecting it today as I need it by Thursday and I will not be home tomorrow OR Thursday to receive it."
- "@AmazonHelp Despite compliants made on app and on twitter we still have not received the ordered item"
- "@AmazonHelp Any idea where it is as still no updates since 04.42 this morning showing on the tracking page !!"
- "@AmazonHelp It may b dynamic but still it's an competitive era and a huge competitor to u like @118702 is providing it easily den y can't u?"
- "@AmazonHelp Yes, I did follow review guidelines and not written anything that is not true and abuse!!.... still you can't post it!!"


### Gift Card Issue (`gift_card_issue`)
- **Estimated Prevalence**: 2.2%
- **Description**: Customer inquiry related to: problem, gift, balance, card, bought
- **In Scope**: Messages containing: problem, gift, balance, card, bought
- **Out of Scope**: Other distinct issues
- **Common Keywords**: problem, gift, balance, card, bought
- **Confusable Intents**: None

**Examples:**
- "@AmazonHelp where do you find the claim code for gift cards?"
- "@AmazonHelp ...and till now ur company haven't given explanation why did my no. get blocked ....and cod facillity is closed for me ...... (4/4)"
- "@AmazonHelp when its removed the system says it's inserted but unrecognized. When it's inserted the tablet behaves as though there's no card"
- "@115850  when will I get the HDFC debit/credit card rewards/Cashback used during the great Indian festival"
- "@AmazonHelp Royal Mail are the carriers. What are you doing to rectify the problem because I’m not staying at home for the next 2 days😡😡😡😡"


## Raw Candidate Clusters

### Cluster 0 (n=399, 13.3%)
- **Proposed Intent**: `account_issue`
- **Keywords**: thank, call, app, link, account
- **Confidence**: High

**Examples:**
- "@AmazonHelp Custom Dynamics Dynamic Ringz LED Turn Signal Inserts - Bullet style GEN200-AW-1157 https://t.co/wARwFlUgV6"
- "@AmazonHelp Yes an error message. My Kindle wasn’t downloading books so I reset it and deregistered it and now I can’t re-register it."
- "@AmazonHelp I hope so u will"
- "@AmazonHelp Then you feed me auto responses and sance around every question i pose to you"
- "@AmazonHelp I have and none of those are the issue. The issue is the app on the Roku tv. I've had the TV 10 months. The app hasn't been usable"


### Cluster 23 (n=363, 12.1%)
- **Proposed Intent**: `unknown_de`
- **Keywords**: de, que, en, la, y
- **Confidence**: High

**Examples:**
- "@AmazonHelp Je me suis trompé, le transporteur c'est bien "Lp collect" mais le colis a bien été expédié par Amazon."
- "@AmazonHelp oi quanto tempo pra receber o email de confirmação de uma compra? to nervoso"
- "@AmazonHelp Creo que en el mismo mac. O en ipad, hace 4 años. Pero lo había podido leer hace tiempo en mac."
- "@AmazonHelp Hola. Gracias por responder. No me aparece la opción porque el producto llegó el 22 ago. Y apenas ayer lo recibí porque vivo en Venezuela"
- "@AmazonHelp J'ai demandé si un transfert était possible, on m'a dit oui et voici les infos nécessaires et depuis 5 mois &amp; 17 relances, cela n'avance pas"


### Cluster 8 (n=173, 5.8%)
- **Proposed Intent**: `wrong_or_missing_item`
- **Keywords**: order, delivered, address, need, wrong
- **Confidence**: High

**Examples:**
- "@115850 Team,Kindly provide the investigation report tht how Order# 402-2926247-6753157 has been updated delivered without actual delivery"
- "I will NEVER EVER ORDER FROM @115821 AGAIN."
- "@116316 hi! I'm trying to cancel an order even before being processed but nobody is answering me :("
- "@115850 @AmazonHelp another pathetic issue Prime order showing delivered track# 449123579275 not done in actual https://t.co/Si8xFXWgMc"
- "@AmazonHelp No it said order in 9hrs and it will be here Monday i ordered it and it said it’s coming Thursday . How dare y’all and i have amazon prime ."


### Cluster 7 (n=162, 5.4%)
- **Proposed Intent**: `delivery_delay`
- **Keywords**: delivery, amp, date, time, return
- **Confidence**: High

**Examples:**
- "@1898 Maybe Android is becoming the new Windows: hard to make a single operating system run smoothly on thousands of different devices"
- ". @115830 delivery is so poor. Not really sure why we pay for prime when they don’t deliver on time."
- "@AmazonHelp She advised that the delivery driver would attempt delivery again in the next 24 hours...she weren't listening to me, just reading off a screen. Useless! I had to escalate to her manager and ask for a new order to be generated. Amazon wasting my time and you're losing money!"
- "@AmazonHelp Hope that would be appreciated if it was  delivery by Wednesday..."
- "@AmazonHelp Yea I'm aware of that we can't figure that until sell starts. Only thing is If it doesn't allows pune location 1/n"


### Cluster 12 (n=157, 5.2%)
- **Proposed Intent**: `unknown_customer`
- **Keywords**: customer, service, care, phone, ever
- **Confidence**: High

**Examples:**
- "@AmazonHelp Thanks.  Your logistics department already responded tonight and FAR exceeded what I expected as a response.  Great customer service on that front."
- "@Tesco BEST CUSTOMER SERVICE TEAM EVER"
- "Okay, @115821 was already awesome but their customer service is also amazing. So helpful!"
- "@115830 , twice now your customer service has lied to me and assured delivery, now saying they expect it to not be delivered, prime my arse."
- "@115850 jst hd my worst experience EVER! order no 403-4518222-1255514 ,amazon shows wrongly delivered,called customer service 10 times (1)"


### Cluster 16 (n=153, 5.1%)
- **Proposed Intent**: `returns_and_refunds`
- **Keywords**: want, refund, dont, ordered, item
- **Confidence**: High

**Examples:**
- "@115830 I pre ordered Battlefront 2 months ago, but you never sent me the lightsaber mastery starcard unlock code?"
- "Ordered 3x vinyl for my dad on @115821 but they sodding changed to CD?! Wtf?! Tech issue much?"
- "Made a purchase in @115821 for my son bday. I told seller I got 1of 3 items ordered, he tells me to chase after Amazon for a refund. I can't get a refund if I don't ship it back, but I never received them in the first place. Hello? #BadExperience #worstAmazonSeller #Amazon https://t.co/LFKgEDp0Jn"
- "@AmazonHelp I can provide you the order number. But i dont want to switch this tweet as a customer chat support. My purpous of this tweet is to let know people how careless you becoming and disrespecting your customers now who has come trusting you these years."
- "@115830 this isn't the #XboxOneX I ordered https://t.co/BVStLQCpAA"


### Cluster 24 (n=151, 5.0%)
- **Proposed Intent**: `delivery_delay`
- **Keywords**: day, prime, shipping, next, delivery
- **Confidence**: High

**Examples:**
- "Amazon Prime Now is really amazing. Just ordered something that will be at my house before I wake up tomorrow morning."
- "@AmazonHelp I continue to have delivery issues with my same day orders after providing detailed instructions. What can I do to fix this?"
- "@AmazonHelp why is this my second prime purchase in a row that I'm getting later than my two day guaranteed delivery?"
- "@AmazonHelp 20 minutes to go!! Your tracking system is awful! I have literally stayed in all day waiting for this! Day off work! Joke!!!"
- "Me when Amazon took their Prime money https://t.co/fIxjPmy5MS"


### Cluster 13 (n=143, 4.8%)
- **Proposed Intent**: `order_tracking`
- **Keywords**: still, waiting, today, says, tracking
- **Confidence**: High

**Examples:**
- "@AmazonHelp Yes, I did follow review guidelines and not written anything that is not true and abuse!!.... still you can't post it!!"
- "@AmazonHelp Despite compliants made on app and on twitter we still have not received the ordered item"
- "@AmazonHelp Any idea where it is as still no updates since 04.42 this morning showing on the tracking page !!"
- "@AmazonHelp That link says I have no orders. The email confirming it’s been shipped shows it’s out for delivery. I’m expecting it today as I need it by Thursday and I will not be home tomorrow OR Thursday to receive it."
- "@AmazonHelp It may b dynamic but still it's an competitive era and a huge competitor to u like @118702 is providing it easily den y can't u?"


### Cluster 2 (n=115, 3.8%)
- **Proposed Intent**: `unknown_email`
- **Keywords**: email, received, mail, id, sent
- **Confidence**: High

**Examples:**
- "@AmazonHelp not yet...my mail id __email__"
- "@AmazonHelp I received the invite on October 5."
- "@AmazonHelp Don’t apologise, it’s cool. It was a dispatch email I think. I shall wait patiently for my items 🤓"
- "@AmazonHelp Yes did that. But may I know why pin code is being asked in address from your side if your courier partner is smart like this."
- "@AmazonHelp I just cancelled an order but is it possible to have it reinstated.  My account is __email__."


### Cluster 17 (n=113, 3.8%)
- **Proposed Intent**: `unknown_got`
- **Keywords**: got, product, available, delivered, asap
- **Confidence**: High

**Examples:**
- "@115850  @115821 got fake product, trying to call Amazon and no one is answering the call. Great.."
- "@AmazonHelp I was going to take the phone call but I got disconnected from chat after they asked for my number. Can I request the call here?"
- "@AmazonHelp i was assured that the product will reach today positively."
- "@AmazonHelp Thank you!!! I got it working. I appreciate you replying."
- "@AmazonHelp I have not got any fields to fill. Pls provide proper url to fill detail's."


### Cluster 19 (n=107, 3.6%)
- **Proposed Intent**: `technical_issue`
- **Keywords**: one, getting, contacted, tomorrow, error
- **Confidence**: High

**Examples:**
- "@AmazonHelp why am I getting this error? Amazon prime video (India) And thank you from Sword Art Online https://t.co/Z67c3dHvEa"
- "@AmazonHelp UK. Chatting with a rep now. Ta"
- "Ordered a new Fire tablet from @115821 Black Friday Sale. Supposedly it will be delivered tomorrow, but hasn't even shipped yet. Apparently, they're going to just beam it directly to the local post office on the morning."
- "@AmazonHelp Contacted them twice. No help."
- "@AmazonHelp I’ve already had one driver not deliver an item today. It should be easier to get Amazon to deliver to a neighbor."


### Cluster 20 (n=99, 3.3%)
- **Proposed Intent**: `unknown_already`
- **Keywords**: already, take, back, done, time
- **Confidence**: High

**Examples:**
- "@AmazonHelp @116324 @AmazonHelp because you are seriously asking me to wait another couple of days. And I am seriously going to take this higher then your shitty little company and we will see how long you wanna take to respond to that"
- "@AmazonHelp Sorry to say.. But I will take precaution to order from @118702 next time.."
- "@AmazonHelp Yep. Was told to take a hike by Amazon, Maplins and Hermes."
- "@AmazonHelp @115821 this is how @81 delivered my order 1 day late and busted. Had 2 repackage &amp; take 55lb box 2 UPS 2 get money back 👎 https://t.co/l7B0YaVZfb"
- "@AmazonHelp Yep, I actually have 15 Mbits/sec connection. But the strange think it's streaming hd in Chrome on windows but on Linux mint no hd"


### Cluster 5 (n=99, 3.3%)
- **Proposed Intent**: `unknown_package`
- **Keywords**: package, delivered, packages, supposed, today
- **Confidence**: High

**Examples:**
- "I’ve fucking moved and I still can’t get a package in time. This time the lazy @118706 said my mailbox is blocked. Total bullshit https://t.co/I8geIIy36F"
- "@AmazonHelp So Amazons entire investigation was going on https://t.co/piqRd0Rsqj and tracking the package. Since it was given to someone else Amazon claims I have the package and my claim was denied"
- "@amazonhelp The same driver that reversed into my fence, delivered a damaged package with liquid pouring out of it &amp; said I just deliver it"
- "@115850 @115821 @115850 @115821 tracking ID 350134310804 I did not receive the package, give me the corrier mobile number, he has not delivered the package to me and I have already paid upfront for the item, where is my package"
- "@115850  delivered my package at 8:25 in the morning... OMG 😱😱 Is this a new record 😂"


### Cluster 15 (n=97, 3.2%)
- **Proposed Intent**: `unknown_thanks`
- **Keywords**: thanks, much, sent, go, ok
- **Confidence**: High

**Examples:**
- "@AmazonHelp Thanks guys, appreciate letting me know so I can Opt out"
- "@AmazonHelp ...my phone is linked to another account. How should I go about solving? Thanks (2/2)"
- "@116090 I can't access my other wish lists from within the app anymore... something must've broke with the last update. :-( help? thanks!"
- "@AmazonHelp Thanks. And Amazon has access to mine my private conversations in my home?"
- "@AmazonHelp I'll do that. Thanks."


### Cluster 4 (n=87, 2.9%)
- **Proposed Intent**: `unknown_ich`
- **Keywords**: ich, die, das, und, nicht
- **Confidence**: High

**Examples:**
- "@AmazonHelp @487191 Zurückschicken und die Zweier-Aktion nochmal bestellen wäre keine Lösung? 🤨"
- "@AmazonHelp Also in der Praxis komm ich mit DSL 6.000 aus dem Buffering nicht mehr raus 😢 Welche Internet-Bandbreite brauchts denn für HD oder 4K?"
- "@AmazonHelp Der Bote sagte nicht zu Hause  War zu Hause   wer den Concierge belügt kommt... ….in die Zalando Hölle   da wird er erst mal SCHREIEN lernen https://t.co/49GInk76Tk"
- "@AmazonHelp Ich hoffe auch, denn ich denke meine Prime Mitgliedschaft wohl zu überdenken."
- "@AmazonHelp Die Frage wäre, warum der Telefonsupport 3 Anläufe braucht, und ihr sofort den richtigen Riecher hattet."


### Cluster 21 (n=78, 2.6%)
- **Proposed Intent**: `unknown_india`
- **Keywords**: india, music, alexa, echo, play
- **Confidence**: High

**Examples:**
- "@117634 @115821 Not only that, but I just spent like 20 minutes looking up if there’s a way to hide my list. It was faster just to remove all my friends so it’s private again. Fucking dumb."
- "can anyone help us to decipher what house number @115821 left our parcel at https://t.co/5GjEwmAJdA"
- "@5503 I’m enjoying the @128020  Experience on the @115833 dot. However, I’d prefer to stream it through @118117 speaker. Alexa can’t manage that, despite repeated attempts. During the most recent attempt, Alexa thought I wanted, um, this: https://t.co/VsWvhMHake"
- "@115833 my second gen echo will play music, keeps not playing radio. Understands the command and says it's playing. No sound"
- "@115850 there is no Buy now Button..!!! https://t.co/KX6NplEBdK"


### Cluster 22 (n=74, 2.5%)
- **Proposed Intent**: `unknown_deliveries`
- **Keywords**: deliveries, two, weeks, really, different
- **Confidence**: High

**Examples:**
- "@AmazonHelp The lady was quite unhelpful yesterday. I love amazon but feel really let down now."
- "Anyone else with Prime from @115830 having the issue where weekend delivery has disappeared? Two different answers from two different customer service peeps (technical issue &amp; Black Friday delays). I thought I was paying for “next day” delivery?"
- "So @115821 is really bad with their "next day deliveries", it's been two days since a book was ordered for me and it still hasn't arrived."
- "@AmazonHelp So if it's not delivered in the next hour I'm stuck without a costume"
- "If you are missing an Amazon pkg... strongly suspect we have a driver miss delivering.  I didn’t get a pair of shoes recently."


### Cluster 1 (n=71, 2.4%)
- **Proposed Intent**: `technical_issue`
- **Keywords**: happened, put, working, work, read
- **Confidence**: High

**Examples:**
- "@107085 @115821 @AmazonHelp I can't even put it in my cart--is it asking you to choose a country on the buy page?"
- "@AmazonHelp We have already spoken to someone at Amazon and are waiting for this to be resolved. Why has this happened 3 times?!!"
- "@468593 @AmazonHelp Sorry to chime in but the same thing has happened to me. Used to get stuff sat and sun now have to wait until Monday!"
- "@AmazonHelp @469809 Same has happened to me. Useless"
- "Not working in Berln either. Second order this week, again they just didn’t show up. @116316 https://t.co/CpQK3RmhEl"


### Cluster 11 (n=69, 2.3%)
- **Proposed Intent**: `unknown_days`
- **Keywords**: days, bad, n, quality, prime
- **Confidence**: High

**Examples:**
- "@153820 Terrible experience with Amazon Restaurants, waited an hour and a half just to get my order canceled. Better yet, all restaurants have since closed so I guess I now have to sleep on an empty stomach. #thanksamazon"
- "@115821 Prime math....where 1 week equals 2 days. #notimpressed"
- "@AmazonHelp it was doing this a few days ago and a factory reset dixednit, for two days. A hard reboot did not resolve."
- "@AmazonHelp one bad Apple..   among lot good apples.  bad ones are out. there . hope they learn ."
- "@AmazonHelp @115821 A new low of this brand. Started selling used products online. Wepay for new products not used products n please dnt ask me contact ur customer support, they could not provide any help. You guys juz boast off saying we will refund. What about time and urgency?"


### Cluster 18 (n=66, 2.2%)
- **Proposed Intent**: `gift_card_issue`
- **Keywords**: gift, card, bought, problem, balance
- **Confidence**: High

**Examples:**
- "@AmazonHelp Royal Mail are the carriers. What are you doing to rectify the problem because I’m not staying at home for the next 2 days😡😡😡😡"
- "@AmazonHelp ...and till now ur company haven't given explanation why did my no. get blocked ....and cod facillity is closed for me ...... (4/4)"
- "@AmazonHelp when its removed the system says it's inserted but unrecognized. When it's inserted the tablet behaves as though there's no card"
- "@AmazonHelp where do you find the claim code for gift cards?"
- "@115850  when will I get the HDFC debit/credit card rewards/Cashback used during the great Indian festival"


### Cluster 6 (n=64, 2.1%)
- **Proposed Intent**: `delivery_delay`
- **Keywords**: hours, parcel, logistics, arrived, even
- **Confidence**: High

**Examples:**
- "@115830 Credit where credit is due, my parcel arrived with hours to spare."
- "Pleased to find my @115830 parcel delivery is missing the metres and metres of brown paper I'd normally get😂 #FirstTime"
- "@AmazonHelp Sold by Amazon. Delivered by Amazon Logistics. Arrived like this: https://t.co/kOfLrk2dfb"
- "@AmazonHelp I have to wait 12 hours?"
- "Okay, but if you can mark it as "delivered" 36 hours before actual delivery, can you understand how that looks super scummy/unhelpful? https://t.co/oeINRqSv3D"


### Cluster 9 (n=48, 1.6%)
- **Proposed Intent**: `unknown_reply`
- **Keywords**: reply, kind, thats, said, requesting
- **Confidence**: Low

**Examples:**
- "@AmazonHelp Thanks for prompt reply. You gave the link to yu our website which shows the same thing. It left a place yesterday at 1.06 PM which is less than an hour far from delivery destination. So why is it now saying 1 Dec ? I need to know the reason, someone to talk to"
- "@AmazonHelp She said "I already spoke to my supervisor" when I asked her why I couldn't be transferred."
- "@AmazonHelp @115830 356th day requesting any kind of response"
- "@AmazonHelp Sure. I loved the positive reply! :)"
- "@115850 ... where is my order. U guys dont hve particular update abt my escalation ...  is this the kind of services ur providing..."


### Cluster 10 (n=42, 1.4%)
- **Proposed Intent**: `delivery_delay`
- **Keywords**: late, dear, youre, telling, delivered
- **Confidence**: Low

**Examples:**
- "Dear @115850, my order with tracking no. 111130061073 is not being delivered by your executive as per convenience. Please help"
- "@AmazonHelp Could you imagine your competition in this market (UPS, USPS, Fedex) telling a customer that their packages have been at a nearby location but there's no delivery person available to bring them - for more than an entire day?"
- "@AmazonHelp For the same event I had 13 items for same day Friday delivery. Called after they weren't delivered. Said they would it would arr Sat. #late"
- "When you're too tired to bark at the Amazon courier even though Mom did a shit ton of Cyber Monday shopping. https://t.co/X3iXIMrjAQ"
- "Dear @115821,  My bank account and I love you more and more with each passing day.💻💵🎄🎅🏻🎁 #ChristmasShoppingAlmostDone #MayHaveMoneyLeftOver"


### Cluster 3 (n=40, 1.3%)
- **Proposed Intent**: `unknown_check`
- **Keywords**: check, result, ill, doubt, details
- **Confidence**: Low

**Examples:**
- "@AmazonHelp DM’ed you. Please check and reply"
- "@AmazonHelp Their is already existing complaint going on can you please check and expedite the process"
- "@AmazonHelp Don't able to chat using this feature, please check. No in my bank statement the debit is 746 and credit is 686."
- "@AmazonHelp How can i check my result?"
- "@AmazonHelp Please check my email sent your cs ... and revert. #this #sucks"


### Cluster 14 (n=28, 0.9%)
- **Proposed Intent**: `unknown_merci`
- **Keywords**: merci, wtf, à, 👍, tout
- **Confidence**: Low

**Examples:**
- "Nigga really stole my amazon package like wtf bro 😒😒😒"
- "@AmazonHelp Grazie, continuate cosi 👍"
- "@AmazonHelp Merci. Bonne fin de journée."
- "@404793 @AmazonHelp Tu te crois vraiment tout permis haha"
- "@AmazonHelp Merci, je vais faire ça de suite."

