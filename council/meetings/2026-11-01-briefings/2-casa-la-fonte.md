# Briefing, item 2: Casa La Fonte direct marketing

Prepared 2026-10-31 (afternoon CT), read-only. Builds on Daniel's pre-read "Council briefing: Casa La Fonte 2027 bookings" (Claude Docs, 30 Oct) and adds what changed or could be checked independently on 31 Oct. No guest personal data. Partners are named by business only.

**Sources checked:** Gmail (from 20 Oct), the scheduled-task list, the casalafonte.it repo (public clone, commits to 31 Oct 10:24 UTC), and the pre-read.
**Not checked:** the live site (WebFetch and curl blocked by the proxy, so the repo source was read instead), the Google Ads console, Search Console data, Instagram Insights, the Airbnb/Vrbo dashboards, the booking sheet and the Stripe dashboard.

## 1. Channels: set-up and status

| Channel | Status on 31 Oct | Note |
|---|---|---|
| **casalafonte.it** | Live since 25 Oct. Six languages (EN, DE, IT, NL, DA, FR) plus 3 guide pages per language. Sections: house, facts, wellbeing (10 blocks), area, about, prices, FAQ. Calendar syncs from Airbnb iCal every 3 h. Monthly link/function check runs as a GitHub Action. | Request flow: an instant quote, then a **mailto** prefilled email (or copy the text), or WhatsApp to Daniel or Eva. There is no form backend. Pricing rule is in code: `floor(0.9 × (nightly sum × (1 − 7/28-night discount) + €240 cleaning) / 5) × 5`, with no extra-guest fee. This matches the ~10% rule. |
| **Google Ads phase 1** | Pre-read says: live 27 Oct to 30 Nov, €350 budget. 27–29 Oct: 207 impressions, 35 clicks, €31.70, CTR 16.9%, 0 requests. Search terms leak to seaside, competitor and "Ferienwohnung" searches. No Dutch impressions. | Gmail has **no billing receipts and no performance emails**. Generic "launch your first campaign" nudges on 27 and 30 Oct are probably marketing emails, but this is not verified. A €446.35 promo credit is pending its spend terms. |
| **Instagram @casa_lafonte** | First post 29 Oct (pre-read: 3 followers). Launch burst posts 3–9 are scheduled 1–8 Nov at 18:15 UTC, then Tuesday and Saturday from 10 Nov. | Each post is a **manual step**: a reminder on Daniel's MacBook asks him to drag in photos. Whether posts 1–2 went out on 31 Oct, and whether the "vineyards" error was fixed, is not checked. |
| **Volterratur** | Replied 29 Oct: listing **requires Consorzio membership**. €250 refundable share, then €175 + VAT for 2027, €150 for 2028 and €300 + VAT from 2029. Form attached. | Awaiting Daniel's decision. The partner tracker's prompt still says "Claudia asked where to be listed", which is out of date. |
| **Visit Tuscany** | Regional code received. Daniel registers. | Free. Not started. |
| **Traum-Ferienwohnungen** | Deferred. Decision task fires **17 Nov**: €399/yr, no commission, refund if fewer than 10 requests (terms to confirm). | It will have only about 3 weeks of mostly near-zero data to judge from. |
| **Airbnb / Vrbo** | Two 2027 stays (18 nights, ~8% of 221 season nights). Unchanged on the site calendar as of 31 Oct 05:49 UTC. | Open fixes from the pre-read: public reply to the critical top review, Vrbo Instant Book, "vineyards" text, experiences line. Not re-checked. |

## 2. Results since launch (25 Oct)

- **Direct inquiries and bookings: 0.** No "booking request" email in any language, no "[La Fonte] Approve reply" thread and no Stripe payment email. The guest-inbox task has run hourly and reported nothing.
- **Ads:** €31.70 for 35 clicks to 29 Oct, the only figures available (from the pre-read). At that rate, phase 1 spends ~€100–120 by 30 Nov, not €350, unless the budget is pacing higher. Not checked in the console.
- **Search Console:** verified for both hosts (emails 25–26 Oct). No click data seen.
- **Partner replies:** see section 3. The directory reply is Volterratur, covered in section 1.

## 3. Guest experiences and partners

| Partner | Status | Terms | Open |
|---|---|---|---|
| Fattoria Tegoni (riding, farm cooking class, lunch, tastings) | **Confirmed** 26 Oct, on the site | Guests book direct, no commission | Daniel sent "a small request" 30 Oct; no reply yet |
| Arianna & Friends (cooking at the house, chef dinners, day tours) | **Confirmed** after the 30 Oct call; partner link live on the site | 10% built in (guest discount or our commission, chosen per booking); **+€120 travel per service**; prepaid; German guide where possible | Collab post idea for 21 Nov |
| Believe Service, Casole d'Elsa (yoga, pilates, trainer, Florence guided tours) | **Agreed on the 31 Oct call.** Site updated the same day. Written answers arrived 31 Oct 14:19 UTC. | Florence tours priced per group, 2 to 8–10 people; museum tickets **not included** (named tickets, passport). **No German** (EN/IT/ES). Payment **direct to her, cash or bank transfer**. **No discount** from instructors. Travel fee case by case. | Massage: she has contacts, prices pending, but the site already says "massage on request". The Medici tour price is confusing (€300 for 10 / €40 pp). |
| Iyengar yoga teacher, Volterra | Confirmed 29 Oct (June–Sept, English) | €70 for 1, **€50 per person** from 2 (~70 min) | Wants to see the house in Nov–Dec, but Daniel and Eva are away until March. A draft reply is waiting. |
| Convivum (local cook, welcome basket) | Confirmed 29 Oct | Prices requested | — |
| Other wellbeing/PT contacts (4) | 1 declined, 3 no reply | — | Follow-up after 21 Nov per tracker |

**Confirmed and on the site:** riding, farm and in-house cooking, yoga (2 providers), pilates, trainer, Florence tours. **Pending:** massage, Convivum cook pricing, German-speaking instructors.

## 4. Host-agent scheduled tasks

| Task | Schedule | Last run |
|---|---|---|
| Guest inbox check | Hourly 07–23 Rome | 31 Oct 15:33 UTC, **succeeded** (prompt edited today) |
| Partner and directory replies | 09:41 / 18:41 Rome | 31 Oct 08:41 UTC, **succeeded**; it will pick up the Believe Service reply tonight |
| Instagram posts 3–9 | One-shots, 1–8 Nov | Pending; tied to the MacBook and need Daniel each time |
| Traum-Ferienwohnungen decision | 17 Nov | Pending |
| Summer price review | 15 Jan 2027 | Pending |
| Guest-message review | 1 Feb 2027 | Pending |

There are **no failures**. Two prompts have drifted from reality:
1. The **guest-inbox agent still says yoga, PT and massage are "NOT yet confirmed"**, while the site now sells them. Guest replies will under-sell or contradict the site.
2. The partner tracker's statuses for Volterratur, Believe Service and the Volterra yoga teacher are out of date.

No task reports Ads or channel metrics before 17 Nov, and none is set for the **30 Nov phase-1 review**.

## 5. Gaps and risks

1. **Tracking overstates and understates at the same time.** The Ads conversion (€150 value) fires on *clicking* the mailto button or *copying* the text, not on a sent request. A WhatsApp click is only an event, not a conversion. Consent defaults to denied, which is correct for the EU but leaves much of the data modelled. There is no GA4, so funnel drop-off can't be seen. Smart bidding will learn from noisy signals.
2. **The conversion path is fragile.** A mailto link fails silently for webmail users without a mail client. A small form endpoint, or a "we received it" auto-reply, would also give a true conversion.
3. **Stripe readiness is unverified.** "[Action required] Provide additional information" arrived 26 Oct and "Continue setting up" 27 Oct, but the host agent treats payments as live since 26 Oct. If verification is still open, the first deposit invoice could fail.
4. **Timing and target.** The DACH/NL summer booking window (Oct–Jan) is now. The 80% target needs ~159 more nights. The shoulder months are a demand problem, not a visibility problem, and the pre-read's own sum of levers comes to 60–160 nights.
5. **Budget is too small to learn.** €10/day with 0 conversions so far can't separate a channel problem from noise by 30 Nov. Phase 2 (1 Dec – 15 Feb) is planned but not yet decided.
6. **Partner terms clash with "book direct, easy".** Believe Service is cash or bank transfer with no discount; Arianna adds €120 travel per service. Experiences are listed but not packaged into a bookable reason to come in May, June or September.
7. **Reviews.** The critical review at the top of Airbnb (pre-read) is unanswered as far as seen. Vrbo has 1 review. The site has no verified-review link.
8. **Owner bandwidth.** Instagram posting, partner replies, the Visit Tuscany and Volterratur sign-ups, and the Stripe follow-up all wait on Daniel personally.
9. **Repo exposure.** The pre-read says the advisory-council repo is public on GitHub. Not re-checked here.

## 6. Decisions for Daniel on Sunday

1. **Target definition:** keep 80% of the full season by 31 Jan, or switch to 80% of Jul–Aug plus 40–50% of the season. Holding the full target means deep shoulder discounts; reframing means a lower ambition but a credible plan.
2. **Volterratur membership** (€250 refundable + €175 + VAT for 2027): yes gives a local DMC listing plus networking, at low cost; the trade-off is an uncertain booking yield and paperwork with ID and tax fields.
3. **Ads phase 1 fixes now** (negatives, a dog-friendly ad group, a conversion that counts only real requests): better data, at the cost of a reset learning period.
4. **Ads budget for the January peak** (keep €8–12/day, or move money to past-guest email and partners): reach in the booking window versus a cheaper but slower warm channel.
5. **Shoulder-season offer** (early-booking 10%, or 3-night minimum in Apr/May/Oct): fills empty nights against the fixed Convivum fee, but trains guests to wait for deals.
6. **Booking.com** (yes, no, or later): the biggest reach for NL/DE shoulder trips, but ~15% commission plus calendar-sync work with Convivum.
7. **Experiences:** package a May/September wellbeing week now, or keep à-la-carte listings. A package gives a reason to book now, but partner terms (cash, travel fees, no German) make it harder.
8. **Housekeeping, one approval:** update the guest-inbox and partner-tracker prompts to the confirmed partners, add a 30 Nov Ads-review task, and confirm Stripe verification. Low effort; it closes the drift.

## 7. Questions for the Red Team

1. With 35 clicks, a 17% CTR and 0 requests, is the problem the ads, the site's mailto conversion path, or price and positioning? What is the cheapest test that tells them apart before the January peak?
2. The direct price is 10% below platform totals and the site must not say so. Does an undisclosed discount move anyone? Does it risk Airbnb/Vrbo parity or ranking penalties once guests compare?
3. Is 80% by 31 Jan reachable without discounts that cut into net revenue after the fixed €2,550/month Convivum fee? Which levers in the pre-read are double-counted or rest on hope?
