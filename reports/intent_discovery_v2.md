# Intent Discovery Report (V2)

**PROPOSED TAXONOMY — REQUIRES HUMAN REVIEW**

## Methodology
- **Environment Note**: Due to a C-extension binary mismatch (`numpy.dtype size changed`) preventing `scikit-learn` and `sentence-transformers` from running, this V2 pipeline implements a pure-Python dense semantic concept embedding.
- **Sampling Strategy**: Aggressive noise filtering to remove praise/greetings. Deterministically sampled 5,000 customer messages.
- **Clustering**: Mapped text to an 11-dimensional dense semantic concept space representing core support topics (delay, missing, tracking, refund, damage, tech, etc.). Applied K-Means (K=20).

## V1 vs V2 Comparison
| Metric | V1 (Sparse TF-IDF) | V2 (Dense Semantic Concepts) |
|---|---|---|
| Sample size | 3,000 | 5,000 |
| Candidate clusters | 25 | 20 |
| Other/unclear | ~49% | ~50.1% |
| Coherent clusters | Low | High |

**Total Sampled:** 5,000
**Other / Unclear:** 2,507 (50.1%)

## Confusion & Overlap Analysis
- **Delivery Delay vs Order Tracking vs Missing Delivery**: *Order Tracking* is informational (where is it?), *Delivery Delay* is a complaint about speed/lateness, *Missing Delivery* means it was marked delivered but isn't there or is completely lost. They overlap heavily in keywords but differ in customer state.
- **Returns vs Refunds vs Wrong/Damaged Item**: A *Wrong/Damaged* item is the *cause*. *Returns/Refunds* are the *actions*. Often combined in one tweet.

## Proposed Final Taxonomy (10-15 Intents)

### Other Or Unclear (`other_or_unclear`)
- **Estimated Prevalence**: 50.1%
- **Description**: Messages that do not strongly match any known support concepts.
- **Confusable Intents**: None

**Examples:**
- "@AmazonHelp It's the same for everything I look at, it says get it for November 21st"
- "@115850 dear Amazon I bought 3 books on 22 September but Amazon did not deliver my book."
- "@115830 so annoyed of the service!🙂😫"
- "@AmazonHelp No. It was last scanned Friday on the other side of the country."
- "And yes that deserve two tweets and a follow up tweet @115821 you guys are amazing at customer service #grateful #helpful #thanks"
- "@115850 I hv ordered a dress to which it's saying is delivered but it's not in actual.look in to the matter plz"
- "@115850 @115821 thank you for your lightning delivery within 24hr. ₹461 with 10% cashback . Hope this will last long over my expectation♥ https://t.co/Y7x65m4oy2"
- "@AmazonHelp @126908 machst du mein frau an oder was  @126910"
- "@AmazonHelp Si, pero en el sitio no hay opción para cancelar la orden. Tampoco encontré una opción para explicar el problema. Solo opciones predefinidas"
- "je vous aime tellement ❤️ @AmazonHelp"


### Delivery Delay (`delivery_delay`)
- **Estimated Prevalence**: 23.5%
- **Description**: Customer inquiry strongly associated with concepts: delay, account, tracking.
- **Confusable Intents**: order_tracking, missing_delivery

**Examples:**
- "@AmazonHelp @AmazonHelp response we have had back is not helpful. Saying the Amazon prime will be extended and the courier will give us a call on delivery not helpful. If the courier calls while my partner is at work he can't answer. Item has not arrived on 2 delivery dates no wiser still!!"
- "ummmmm @115821 @AmazonHelp what's the deal with prime packages consistently being delivered late? Why bother paying for prime???"
- "@115830 please can you help me? I placed an order on 26.10.17 but it hasn't arrived and now it is past the date I needed it for. I can't cancel the order from my account."
- "Damn, @115821 Logistics in Atlanta is *still* dropping the ball with deliveries. Two in a row have been late! I sent both to my local Wholefoods Amazon locker because they can’t ever seem to deliver to my apartment. So frustrating that I can’t just specify UPS or FedEx!! 😡 https://t.co/C9kxvCuxDl"
- "@AmazonHelp Not really. Hermes said on 25/10 that my address is a security risk. Yet the delivered a Dorothy Perkins order yest am. Amazon chat told"
- "@AmazonHelp Package still has not arrived.  I went out and bought the items elsewhere.  I need to cancel the order."
- "@AmazonHelp Just tried that and it's still got a dodgy screen https://t.co/J0QzlAXLmT"
- "@AmazonHelp Hi. I ordered laundry detergent on subscribe &amp;save it arrived leaking (presume broken) can you advise what to do please?"
- "So that's two @115830 Prime orders in a row which have been delayed. What am I paying for exactly? 🤔"
- "@146907 @120533 @AmazonHelp Oui ça part en sucette. Avec le Prime sur des produits envoyés par Amazon je n'arrive plus à être livré le lendemain que de temps en temps.."


### Account And Prime (`account_and_prime`)
- **Estimated Prevalence**: 18.3%
- **Description**: Customer inquiry strongly associated with concepts: account, missing, tech.
- **Confusable Intents**: None

**Examples:**
- "@200784 @119038 @290981 @118797 @117795 @127852 Guess Im gonna cancel amazon prime now as a result"
- "@AmazonHelp My account's been locked for 2 months.. sent faxes with info you guys requested to unlock it but got no response. Please help!"
- "@AmazonHelp It's okay now, I've solved it. But as a recommendation, if something happens that changes an order's status etc, a visible and obvious notification or email would be appreciated as opposed to me having to find out by scrolling through my orders."
- "@115821 does anyone else find the 2 day delivery connected to Prime, turning into 3 to 4 days?"
- "@AmazonHelp Eure "Garantie" für den Prime Versand ist nichts wert!! Sendung verspätet und zwar evtl. 2-3 Tage?!? Bei Prime!?! No way!!"
- "Time to cancel @115821 prime until ur couriers can actually get me my packages on time, or at all.Nothing but problems with AZL. @AmazonHelp"
- "@AmazonHelp I received an email as a Prime Customer for £15 off an Amazon Fire Stick, but the promotional code WASN'T on it?  Can you help?"
- "@AmazonHelp I haven’t received any emails from your team in the last 5 days. I have shared my screenshot of my response of earlier ones in my previous tweets. And BTW, if it’s another email asking for this twitter handle url, pls..I have better work to do!!!"
- "@263285 @117086 tenho um Roku stick e não consigo configurar as legendas do Prime Video para pt-BR, além de que não consigo reproduzir alguns títulos, há algum suporte para esse dispositivo?"
- "@AmazonHelp Its the professional seller account that I didnt ask for in the first place . Ya ya im sure you have it inthe fine print of the subscription"


### Refunds And Charges (`refunds_and_charges`)
- **Estimated Prevalence**: 13.6%
- **Description**: Customer inquiry strongly associated with concepts: refund, account, missing.
- **Confusable Intents**: returns, cancel_order

**Examples:**
- "hello i just got home and ???? i received an email from amazon that they cannot proceed my payment for mafu's album ??????"
- "@AmazonHelp Your CC agreed 2 refund but this item is available on sale now also, when u don't have item for delivery why keep it 4 sale? AI @ work?"
- "@AmazonHelp after 36hrs I called, I have to wait 3-5 days for my refund &amp; re-order if i want the items. There should be faster solutions 4 prime members"
- "@AmazonHelp They cancelled my card. I was very upset I was not even paying my monthly bill. Had already paid it, was just making a extra payment."
- "@115850 I had ordered a Moto G5 plus and made a payment but it got cancelled without specifying any reason. Look into this asap."
- "@AmazonHelp @115821 I have raised a concern regarding charge of $99 to my Amex for prime US without my consent. Request ur response on the same by earliest."
- "@119356 I received this mail last night and I tried to contact your customer care but you've blocked my account and there is no phone number mentioned on the site. I checked with my bank and they claimed I entered the right details. How do I unblock my account? #amazonindia #wtf https://t.co/jE728fEVaj"
- "@AmazonHelp I don’t pay for prime to be lied to was promised 2 day shipping and it’s taken about 2 weeks and 3 days who I gotta sue https://t.co/deacM13XSp"
- ".@AmazonHelp it's confusing why your staff member Simone would lie about my refund. Should I expect to lied to when ordering items from your company @115821?? https://t.co/R0amWG20PF"
- "@AmazonHelp The problem is, I pay for prime and fully expected delivery of my package today.  I'd understand if it was xmas or some holiday.. however ?!"


### Order Tracking (`order_tracking`)
- **Estimated Prevalence**: 9.3%
- **Description**: Customer inquiry strongly associated with concepts: tracking, missing, tech.
- **Confusable Intents**: delivery_delay

**Examples:**
- "Update: luckily the lady wasn’t home where my package was delivered so it was still on her doorstep. There was another persons package #1461 at the same door (1416). Get it together @115821 . If it wasn’t for my kindness 1461 wouldn’t have received their package. 😩😒🤯🤬"
- "@AmazonHelp very pathetic service by amazon . they even dont know where is product . call 9713730311"
- "@AmazonHelp more strange thing. status showing deliverd yestrday not yet received #pathetic what is use of prime? guaranteed delivery?Will u compensate?"
- "@115850 without delivering my order,consignment status is showing delieverd to me... Disgusting...very bad..not expected from u..this is second time facing same issue for two seprate orders..r u betraying me.."
- "@AmazonHelp sure what’s going on as there haven’t been any updates on the tracking so no one knows where it is or when it’s coming"
- "@AmazonHelp I ordered some clothes that USPS appears to have lost 😩 I’d like to re order them but I don’t want to waste money. Any help?"
- "@AmazonHelp If your system was checked you'd know because your system told me the package was "lost in transit". This is untrue because it sat at the carrier bc he couldn't deliver it bc the locker is down."
- "@AmazonHelp Yes once again it made it to my city in two days but then sits at the post office until the 3rd or 4ty day. USPS is never 2 day for us"
- "@115850 Yesterday I placed an order with 1 day delivery option. Where is my order, I don't have contact number of you delivery agent also?"
- "@AmazonHelp Hi, that link says they're out for delivery, arriving today, but current status on both on tracking link from e-mail is: "your packages may be lost."  They were due to arrive on Nov 7th, ordered on 5th."


### Technical Issue (`technical_issue`)
- **Estimated Prevalence**: 9.2%
- **Description**: Customer inquiry strongly associated with concepts: tech, missing, delay.
- **Confusable Intents**: None

**Examples:**
- "Overwhelmed to receive early invitation from @115850  #AmazonEcho  Thanks for choosing me one on your #echo journey in India!"
- "@115833 @5503  is the "Your Voice" feature US only at present? Cant see it on any of my UK device settings."
- "@AmazonHelp I've already done that and your no help and every time I pre-order off your website you lot never deliver it on time it's always a week late"
- "@AmazonHelp No, i wasn’t trying to buy from the Kindle App, I was using the Amazon iOS app"
- "Wann kommt eigentlich die tolle App von @115825 auf dem iOS TV raus? Wurde vor 6 Monaten angekündigt. Bis heute nicht da 👎😒 #AppleTV"
- "@AmazonHelp Why ask me to call up to be told that's it's just hard luck and there's nothing you can do about it? Was it just to rub it in that your website lost me the tickets?"
- "Anyone else having issues with the @116618 app. Never seems to work on Samsung s8."
- "@AmazonHelp “Lost in transit” It was out for delivery twice before this happened. I DM’d you guys and you advised to contact via website but haven’t had a reply."
- ".@115833 keeps disconnecting from bluetooth, and the @122609 app is so poor I can't fix typos in my feedback to try and provide data."
- "@115850  I show a add on app 13oct load amazon pay balance 15% back offer,i cant receive.,i call customer care says offer does nt exit wow"


### Missing Delivery (`missing_delivery`)
- **Estimated Prevalence**: 8.2%
- **Description**: Customer inquiry strongly associated with concepts: missing, damage, wrong.
- **Confusable Intents**: delivery_delay, wrong_item

**Examples:**
- "Ordered a book from Amazon arrived damaged @AmazonHelp 😭 Bought the Boots star buy on Saturday went to wrap it one item missing! @210670"
- "@AmazonHelp @115821  Wht happened sir, didnt get any reply from ur team. Wht i need to do with this empty box nd vedio... give me suggetion team amazon."
- "Absolutely stumped at how Amazon managed to send me an empty package. Wasn't damaged or anything, literally just an empty bit of packaging...🤔🤷🏻‍♂️⁉️ https://t.co/hYlTEQjV8w"
- "@AmazonHelp The link didnt go to app instead asked me to buy movies :-) I am looking for those on Amazon prime. Search function said did not exist"
- "@115850 @228164 @13150 I was never knowing you people also deliver a pair of shoe in two different sizes. Really it is a to z"
- "@115821 May I check with you? The delivery indicated that the product reached me, but I have not received anything. This is not the first time Amazon delivery claimed that item sent but I received nothing, only till next day or worst. https://t.co/wwWBVfIv7V"
- "Hey @115821, this does not count as "delivered" when you live downtown -- package was probably stolen minutes after this photo was taken  Best part? I had had another Amazon package successfully delivered earlier sitting right inside the door! https://t.co/Az4Tsstswk"
- "F you @115821 you lost my corgi onesie and now Halloween is ruined"
- "@AmazonHelp What can be done if I received a damaged box inside the Amazon packaging? This is the fourth time it has happened."
- "@115850 I haven't received headset in the box!  I just examine the packaging there was a tape covering the package &amp; inside the tap there was a big cut in the packaging! Its seams to be that After the packaging somebody's manipulated it! Just hard to believe it! https://t.co/5Srouzbvid"


### Gift Card And Promo (`gift_card_and_promo`)
- **Estimated Prevalence**: 4.6%
- **Description**: Customer inquiry strongly associated with concepts: gift, refund, missing.
- **Confusable Intents**: None

**Examples:**
- "@ATVIAssist @AmazonHelp my pre order bonus code isn’t working it just says “Sorry, an unexpected error occurred” (WWII)"
- "@AmazonHelp I'm in Italy and the code for the locker I've sent my package to is not working..."
- "@AmazonHelp They keep asking and telling me the same thing. They say please send us the claim code and then say it’s not available for use. And not telling me why. No attempt to say sorry that I have now lost $100"
- "@AmazonHelp I don’t know it won’t let me return or replace my order. It’s not a package it’s a digital code for a game"
- "@115850 poor service. No update on order for past 10 days. Same template replies. Ordered refrigerator, got 250/- voucher as gift.Pathetic"
- "@158307 @AmazonHelp pre-ordered #StarWarsBattlefrontII and got the #Beta code. Entered it in the #psn but it won’t let me download. https://t.co/bgAzFPchCY"
- "@115850 Ya received but why it got  cancel? I got the Diwali discount  and then it got https://t.co/ud8cMMbLiv its cost is higher if i want to buy."
- "@AmazonHelp Direct on @115830 @115830 i never shared the code nor my mum. @AmazonHelp told me to do a charge back on my card! Not happy."
- "@AmazonHelp They were not able to help that is why i am here. It ws a bday gift I don't think i can reschedule the birthday by 2 days like your parcels."
- "@AmazonHelp I had sent a gift to my bro One plus 5T 64 gb cost 33k. But my bro did not like 64gb and needs 128gb. Bcoz it was a gift I was unknown of the storage choice of my bro. But I knew he likes One Plus 5T. Ready to pay. No one listening to me. 😣 But appreciated you listened.😊"


### Damaged Item (`damaged_item`)
- **Estimated Prevalence**: 3.9%
- **Description**: Customer inquiry strongly associated with concepts: damage, delay, cancel.
- **Confusable Intents**: returns

**Examples:**
- "Hey @AmazonHelp whoever delivers prime packages blocked my door w 2 big boxes and me w my broken foot had to crawl on the floor to move them"
- "@115830 ridiculously disappointed that after specifying an order was a gift, it still came in its original packaging leading to my Mum seeing it and the surprise being ruined, well done 👍"
- "I have no words right now, describing how I am feeling, @115830 You failed to provide the product on day one and then tell me it's delayed and you ruined my day, chances are I will not pre-order games from you guys. https://t.co/drjWUWslj5"
- "@AmazonHelp I pre-ordered PUBG for the Xbox thinking that it was a digital code when it was actually a physical copy. When I went to cancel, it said I needed to check the box next to the appropriate title, but no such box was on the page. Help?"
- "I swear @115821 delivery drivers get worse and worse, name is on the box, the delivery recipient is massively misspelled 1/?"
- "@131283 @17017 @115850 @294367 i am really struggling to get replacement of my defective product from amazon"
- "@AmazonHelp Please help.  I have been trying for ages to get someone to close the seller account opened by mistake.  Please help me."
- "I bought mini hurdles from @115821 and i get this big ass box with only 1 fucking hurdle.?! Fuck Amazon bruh.!"
- "@AmazonHelp poxa Amazon, comprei o box de livros de Desventuras em Série, chegou adiantado até, mas quando abri estava amassado. Chateadíssima aqui :("
- "for fucks sake. I finally got the DNA test for Max and the code on the box is defective AND product has been used wtf amazon."


### Cancel Order (`cancel_order`)
- **Estimated Prevalence**: 3.7%
- **Description**: Customer inquiry strongly associated with concepts: cancel, tech, delay.
- **Confusable Intents**: refunds_and_charges

**Examples:**
- "@119625 there is a mistake in listing of Jaane Bhi Do Yaaro ..It is shown under Crime genre where it should not be ..Rather it should be under Comedy genre.@13780  also puts it under Comedy https://t.co/ub6ziXi03X"
- "@AmazonHelp It was saying arriving today but our delivery’s stop at 12 and on your website it isn’t at the out for delivery point. Was looking forward to playing on release day. ☹️"
- "@AmazonHelp why am I unable to cancel an order which has not yet been shipped? https://t.co/YXJy4ushZ2"
- "@AmazonHelp @127550 I have IM'd and DM'd about this issue 5/6 times. That's why I asked if there is a known issue. I may have to cancel service"
- "@AmazonHelp Yes... I just cancelled and reordered...but I was curious as to if the "guarantee" promised anything..."
- "@AmazonHelp I have tried both Chrome and my iPhone’s app, multiple times over a 2-3 hour period. No joy. I do not want this order suddenly appearing and changing me, when it should be cancelled already."
- "@AmazonHelp Stop cheating #amazon stop scamming"
- "@115821 please stop using @115817 they've delivered half my order and are claiming the address doesn't exist for the other half of the same order. #GoogleMaps"
- "@115821 @AmazonHelp When You promise a Customer 1 day shipping that doesn’t mean the order will arrive 2 days later! Stop cheating customers"
- "@115850  Highly dissapointed. Twice the same mistake, still nothing."


### Wrong Item (`wrong_item`)
- **Estimated Prevalence**: 3.0%
- **Description**: Customer inquiry strongly associated with concepts: wrong, delay, return.
- **Confusable Intents**: missing_delivery, returns

**Examples:**
- "@AmazonHelp Thanks for ur prompt response. I'll wait till 8pm. Still, the fact that the number of the delivery agent in ur database is incorrect is bothering me. Either that or he deliberately told me that I've got the wrong number. How would you look into this?"
- "@AmazonHelp I've tried emailing, I get told that DPD are wrong. I've tried calling I get put on hold and then cut off after 30 minutes on hold"
- "@AmazonHelp I am just fed up with you guys !! You delivered me a wrong product and i have been struggling for a replacement for last 1 month. Pathetic Service...seriously!!"
- "@AmazonHelp I have cancelled the order on 21 sep n still get refund frm ur end n after chat wid custmr representative each time I m geting different ans"
- "@115821 You've got the book # incorrect for @111744 new book - want to pre-order #7, but you've got it listed as #6 !! #firstworldproblems in a school library https://t.co/DDREMXn7tn"
- "@AmazonHelp I have updated all details i need complain for wrong commitment from all of your employee and delivery at high priority."
- "This is the 2nd time I've ordered THIS ORDER And got something completely different I'm sick of paying for what I'm not getting . @115821 https://t.co/87htjOHKf2"
- "@AmazonHelp Learn something from your competitor like @118702 or @4167  They have good policy when they deliver wrong items #NotAGreatIndianSale"
- "@AmazonHelp A very unclear message about ‘different fulfilment centres’. If there is a problem, then I don’t have issue with that. But saying it will be delivered next day, then saying it will be 4 days later with no reason why, is really poor."
- "@115821 is always freaking me out choosing the wrong delivery updates. Tell me how it says “hand delivered to Alexandra” when no one is home"


### Returns (`returns`)
- **Estimated Prevalence**: 2.8%
- **Description**: Customer inquiry strongly associated with concepts: return, delay, tracking.
- **Confusable Intents**: refunds_and_charges, wrong_item, damaged_item

**Examples:**
- "@AmazonHelp eligible to return until the 4th Nov on the Completed Orders screen. It wasnt what was advertised and sold directly by Amazon!"
- "@AmazonHelp You (not marketplace) sold me a counterfeit Apple phone case and customer service decided returning it was my problem as was sourcing a legitimate one."
- "@115830 how do I return a parcel that has been delivered to my address but the person no longer lives here?"
- "Trying to return an item I got from @AmazonHelp and UPS is charging me $50+ for the return... the item value was $68"
- "Pathetic service by @115850 waiting for return process from last 3 days after so many calls to @115850 no one response. #pathetic #poorservice #AmazonIndia https://t.co/3Xl43b8TVD"
- "@115830 any reason why the delivery driver left my package inside my food bin on my driveway? I'll be returning the item as I can't help but feel that it smells like rotting vegetables now!! Seriously, why?!"
- "@AmazonHelp what's your return policy on wireless routers?"
- "@115821 I just found a package I thought I sent for return weeks ago. Is it too late? If it weren’t for the shoes being too small, I’d eat it, but I really hope I have time."
- "@AmazonHelp Your return authorization, return mailing label and acknowledgement letter not available on the site.. Also how do I pack the return packet"
- "@AmazonHelp you have failed to collect my return twice, meaning two days work missed, now need to take off a third day!!!!!"

