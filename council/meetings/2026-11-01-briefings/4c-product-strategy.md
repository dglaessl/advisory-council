*Briefing 4c for item 4. Exported from Daniel's doc "The Council Sits — Product Strategy" (https://claude.ai/artifact/NADogWpLhk1oDHf7yuVg8t) on 2026-10-31, 13:00 CT. The doc is the live version; this copy is for seats without doc access. Not confidential.*

# The Council Sits — Product Strategy

Oct 31, 2026 · @Daniel

A deliberately unhurried AI council for high-stakes questions: the work is in shaping the question, the council sits twice a day, and every answer comes with minutes, recorded dissent and a published charter it may not break.

## The bet

Instant AI answers are now a commodity: several "AI council" apps already sell multi-model answers for $9–195 a month. Nobody sells **considered judgment**: a question that has been sharpened before anyone answers it, a council that deliberates on a schedule, and a written record of who argued what.

We bet that people facing a few high-stakes decisions a year will pay an engagement fee for that, if three things hold:

1. **The intake is the product.** Most of the value of good advice is in getting the question right. The customer leaves the intake with a better question than they arrived with, before the council has said a word.
2. **The wait is visibly earned.** Progress updates during preparation, and minutes that show the deliberation, make the time feel like work being done, not latency.
3. **The charter is a guarantee.** A published set of principles, each tied to a testable council behaviour, tells the customer whose side the council is on and what it will never do.

The proof we need before scaling is a concierge pilot where at least 3 of 5 people would pay ≥ $500 for their next question.

## Customers and the job

The customer is someone with an infrequent, high-stakes decision and no board to take it to. They hire the council to **think it through with them properly, and to leave a record they can defend**.

| Segment | Typical question | Why they'd pay |
| --- | --- | --- |
| Founders and small-company CEOs | Raise now or extend runway? Enter a second market? | No board, or a board they can't think out loud with |
| Solo investors and family offices | How should we approach this deal or allocation? (analysis, not personal investment advice) | Need structure and dissent, not a tip |
| Executives at a career turn | Take the offer, stay, or start something? | High personal stakes, few neutral advisers |
| Practice owners (clinics, studios, firms) | Hire, expand, sell, change the model? | Expert in their craft, alone on the business |
| Researchers and writers | What does the evidence actually say about X? | Want graded evidence and the counter-case |

Not the customer: anyone wanting a quick answer, a diagnosis, legal representation or a trade recommendation. While Daniel is employed, questions about housing, homebuilding, prefab or construction are out of scope.

## The experience

A question moves through six stages; the customer can see where it stands at any moment.

1. **Bring the question.** The customer writes it in their own words and uploads material: documents, numbers, links, prior advice.
2. **Shape it together.** The Framer agent interviews them in writing: the decision behind the question, options already on the table, constraints, deadline, what "good" would look like, what they fear. It proposes a framed question; the customer edits and accepts it. Daniel reviews the framing before admission.
3. **Admitted to the agenda.** The question gets a docket number, the members assigned to it, and the sitting it is scheduled for. A question that can't be answered responsibly is declined here, with the reason.
4. **Preparation, in the open.** Short updates as the work happens: "The Researcher has found three studies and is grading them", "The Sceptic is testing your assumption about pricing". Each update names the member and what changed.
5. **The sitting.** Members present their independent views, challenge each other, and the Sceptic speaks last. The Chair writes the response statement.
6. **Minutes and response.** Two documents: a one-page **response statement** (recommendation, confidence, key assumptions, what would change our mind, next steps) and the **minutes** (who argued what, the dissent, the evidence, with sources). The customer can ask one round of follow-up questions.

The council's visual identity carries through every stage: the customer sees the members around the table, who is working on their question, and later who said what.

## The council

Every question gets a **core of seven** plus **two to four specialists from the bench**, chosen at admission. Names are working placeholders; each member embodies one charter principle so customers see the charter at work.

| Member (placeholder) | Role | Principle it carries | Model family |
| --- | --- | --- | --- |
| Aude | Chair: runs the sitting, writes the response statement | Dare to know (sapere aude) | Claude |
| Mira | Framer: intake interview, framed question | Clarity before judgment | Claude |
| Lumen | Researcher: gathers and grades evidence | Public reason: show your sources | Claude + Gemini |
| Vera | Verifier: checks every fact the answer depends on | Truthfulness | Gemini |
| Contra | Sceptic: attacks the strongest view, speaks last | Fallibilism | GPT |
| Ama | Advocate for the people affected who aren't in the room | Dignity and care | Claude |
| Folio | Scribe: minutes and updates | Accountability: a record that can be checked | Claude (small) |

**The bench** (two to four per question):

- Economics and finance (analysis, not personal investment advice)
- Strategy and markets
- Science and health evidence (evidence grading, not diagnosis)
- Technology and AI
- People and organisations: incentives, negotiation, behaviour
- Law and regulation literacy: issue-spotting and questions for a lawyer, not legal advice
- Ethics and society
- Design and product

Behind the scenes, an **Evaluator** scores every answer against the charter and against a single strong model; it never appears to the customer.

## Deliberation model

Recommendation: **one default procedure, with the mode chosen at admission by question type**, and every answer benchmarked against a single strong model. Research finds that open-ended debate between agents often fails to beat one model sampling several answers; what reliably helps is diversity of model families and a structure that forces independent views first.

| Mode | How it works | Best for | Weakness |
| --- | --- | --- | --- |
| Structured council (default) | Independent drafts, then cross-critique; Sceptic speaks last; Chair synthesises and records dissent | Open strategic questions | Can converge too early if drafts aren't truly independent |
| Delphi rounds | Members give anonymous estimates with reasons, see the spread, revise over two or three rounds | Forecasts and numbers: market size, timelines, probabilities | Smooths away sharp dissent |
| Tribunal | One advocate per option, opposing counsel cross-examines, Chair rules | Either/or decisions | Can overstate the contrast between options |
| Adversarial collaboration | Two members who disagree jointly name the crux and the evidence that would settle it | Contested factual questions | Ends in "here is what to find out" rather than a verdict |

In every mode the output carries the same four things: the recommendation, the confidence, the strongest dissent, and what would change the council's mind.

## Cadence and founder time

The council sits **twice a day**, and Daniel's three 20-minute slots sit around those sittings. The promise to the customer is an answer **within 24 hours of admission**: slow enough to be considered, fast enough to be useful.

| Slot (local time, adjustable) | Who | What happens |
| --- | --- | --- |
| Morning, 20 min | Daniel | Reviews framed questions from overnight intake; admits, sends back, or declines |
| Midday sitting | Council | Sits on questions admitted the day before; drafts response statements and minutes |
| Midday, 20 min | Daniel | Reads response statements; releases or returns with a note |
| Evening sitting | Council | Sits on questions admitted that morning |
| Evening, 20 min | Daniel | Releases the evening answers; answers follow-ups |

Everything Daniel sees is prepared for a decision in under five minutes: the framed question with a one-line reason to admit, or the response statement with the Evaluator's charter check attached. At that pace the 60 minutes a day cover roughly 4–6 releases a day, far more than the 15–20 engagements a month needed for the revenue target.

Between sittings, the progress updates keep the customer informed, so the wait is visible work rather than silence.

## The charter

The charter is ten promises, published on the website and printed at the foot of every response statement. Each one maps to a council behaviour and to a test the Evaluator runs, so the charter is enforced, not just declared. Draft wording:

| # | Promise to the customer | Rooted in | How the council keeps it | How we test it |
| --- | --- | --- | --- | --- |
| 1 | We strengthen your judgment; we don't replace it. | Sapere aude (Kant) | Reasoning and evidence shown; the crux explained | Every claim traceable to a source or stated assumption |
| 2 | We don't state what we haven't checked. | Truthfulness | Verifier checks every load-bearing fact | Sampled claims audited; unsupported-claim rate tracked |
| 3 | We tell you what would change our mind. | Fallibilism | Required section in every response | Present and specific in 100% of responses |
| 4 | Disagreement is recorded, never averaged away. | Public use of reason | Minutes record dissent and who held it | Dissent appears whenever members disagreed |
| 5 | You decide. We don't nudge, flatter or sell. | Autonomy | No persuasion tactics, no upsell inside answers | Evaluator screens for manipulation patterns |
| 6 | We consider the people your decision affects. | Human dignity | Advocate member speaks for those not in the room | Section present when others are affected |
| 7 | We hear more than one view. | Tolerance, pluralism | Several model families; the opposing view steelmanned | At least two families per sitting |
| 8 | No one grades their own work, and a human signs off. | Separation of powers | Evaluator independent; Daniel releases every answer | Process audit |
| 9 | Your material is yours. | Liberty, privacy | Used only for your question; not for training; deleted on request | Data policy plus deletion log |
| 10 | We know our limits and say so. | Intellectual honesty | No diagnosis, legal opinion or personal investment advice; we refer you | Boundary test set passes before every release |

**Adapted for today.** Three ideas the 18th century didn't need, folded into the promises above: the council always says it is AI (1, 10); it shows where its information comes from (2); and it never optimises for your attention or engagement (5). Whether to name the product after this tradition (Sapere, Aude, Lumen) stays an open question; the name check comes after the strategy is agreed.

## Competitive position

Multi-model answering is crowded and cheap; the combination of intake, scheduled sitting, minutes and charter is open. Competitor facts are mostly from vendor pages (medium confidence).

| Offering | Price | Speed | What it shares with us | What it lacks |
| --- | --- | --- | --- | --- |
| [Suprmind](https://suprmind.ai/pricing) | $19–195/month | Instant | Debate and red-team modes, decision briefs | Intake, sitting, minutes, charter |
| [SynthBoard](https://www.g2.com/products/synthboard/reviews) | Free tier; paid not public | Instant | 24 named role advisors on different model families (closest match) | Question shaping, cadence, human sign-off, charter |
| [The AI Council](https://apps.apple.com/us/app/the-ai-council/id6758050094) (iOS) | $8.99 one-off | Instant | Synthesis with confidence score | Everything beyond a chat app |
| Perplexity Model Council | Bundled in Max tier | Slightly slower than one model | Side-by-side models, disagreement badge | Deliberation, record, intake |
| Deep research ([OpenAI](https://openai.com/index/introducing-deep-research/), [Gemini](https://gemini.google/overview/deep-research/)) | \~$20/month tiers | 2–30 minutes | Long, sourced reports | Dissent, framing, a council that can say no |
| Expert networks ([GLG, AlphaSights](https://cleverx.com/blog/glg-vs-alphasights)) | Experts paid \~$100–1,000+/hour, plus markup | Days | Considered human judgment | Price, availability, written record |

**Where we stand:** priced between deep research and a human expert, and the only offer where the question itself is improved before it is answered. What is easy to copy is the multi-model panel; what is hard to copy is the intake method, the charter with its tests, and a track record of minutes.

## Business model and pricing

Charge per engagement, not per seat: the customer buys a considered answer, not access to a tool. Starting price hypotheses, to be tested in the pilot:

| Offer | What's included | Price to test |
| --- | --- | --- |
| One question | Intake, one sitting, response statement, minutes, one round of follow-up | $250–500 |
| Deep sitting | Large upload set, two sittings, a second-round review after new information | $1,500–3,000 |
| Standing council | Up to four questions a month, priority admission, a running decision log | $1,000/month |

One illustrative mix that reaches $10k a month: 10 single questions at $350, 2 deep sittings at $1,500 and 4 standing councils at $1,000 ($10,500). Model costs per engagement are likely in the tens of dollars (estimate, to be measured in the pilot); the binding cost is Daniel's review time, which the cadence caps at 60 minutes a day.

The pilot is free for the trusted group, in exchange for a structured debrief and an honest answer to "what would you pay for the next one?"

## Boundaries and risks

| Risk | Why it matters | Mitigation |
| --- | --- | --- |
| Regulated advice | Medical, legal and personal investment advice from AI carries liability: Germany's legal-services law (RDG) may cover AI answers on a concrete case, a German court held a clinic liable for its chatbot's claims, and Illinois restricts AI therapy | Charter promise 10; no doctor or lawyer personas; the Framer declines or reframes such questions; lawyer review for the US and DACH before launch |
| Slow reads as weak | One study found people trust slow algorithms less, not more; the labor-illusion evidence covers waits of seconds | Progress updates, named members doing visible work, a human signature on every answer, a 24-hour promise |
| The council isn't better than one model | Agent debate often fails to beat a single model sampled several times | The Evaluator benchmarks every pilot answer against a single strong model; publish the results if the council wins |
| Conflict with Daniel's employment | Outside work, IP assignment and non-solicit terms apply while he is employed | Outside his employer's field; personal time, devices and accounts only; housing and construction questions excluded; agreement checked before any paid launch |
| Founder time creeps | Intake and reviews could exceed 60 minutes a day | Everything prepared for a five-minute decision; admission capped per day |
| Customer data | Customers upload sensitive material | Charter promise 9; per-question storage; no training on customer data; deletion on request |

## Roadmap

Four phases over about twelve weeks, each ending in a gate. Every phase doubles as a block of Daniel's AI curriculum, so the product and the skills grow together.

1. **Strategy and charter** (Nov 2–15). Agree this paper; finish the charter text; write the intake script and the response-statement template; build the Evaluator's first test set (charter checks plus a single-model baseline). *Gate:* the charter's ten tests run on three sample questions. *Skills:* specification writing, constitution design, eval design.
2. **Prototype UI** (Nov 16–Dec 13). A test website: intake with uploads, a docket page with live progress updates, the council visual with named members, and the minutes and response view. Built by the council's own builders, with Daniel directing. *Gate:* Daniel runs three of his own questions end to end. *Skills:* building agent apps, orchestration, memory, human-in-the-loop design, security basics.
3. **Concierge pilot** (Jan 4–Feb 7, after the holidays). Five trusted people outside housing, one or two questions each, free in exchange for a debrief. *Gate:* at least 3 of 5 would pay ≥ $500 for the next one; ≤ 60 minutes of Daniel's time per engagement; the council beats the single-model baseline on the Evaluator's scoring. *Skills:* running evals in production, cost and latency measurement, operating agents with real users.
4. **Decide** (by Feb 14). Launch paid, iterate, or stop. Employment agreement checked before any paid launch. *Skills:* reading the evidence you built.

The AI Tutor turns each phase into the weekly build assignment and logs what it proves for the portfolio.

## Open questions for Daniel

- [ ] Is 24 hours from admission the right promise, or should a sitting be same-day only?
- [ ] Is a human signature on every answer (yours) part of the brand, or a pilot-only step?
- [ ] Brand: your name and face on it, or a council brand only?
- [ ] Language and market: English first, or German/DACH from the start?
- [ ] Which first vertical, if any: founders, evidence reviews (the longevity angle), or general?
- [ ] Member names and visual style: classical, modern, or abstract?
- [ ] Which employment-agreement terms need checking, and when?

## Sources

From the council's research scan of 2026-10-31 (medium confidence; vendor pages for most competitor facts):

- [Suprmind pricing](https://suprmind.ai/pricing) · [SynthBoard on G2](https://www.g2.com/products/synthboard/reviews) · [The AI Council, App Store](https://apps.apple.com/us/app/the-ai-council/id6758050094)
- [OpenAI, Introducing deep research](https://openai.com/index/introducing-deep-research/) · [Gemini Deep Research](https://gemini.google/overview/deep-research/) · [CleverX, GLG vs AlphaSights](https://cleverx.com/blog/glg-vs-alphasights)
- [Buell & Norton 2011, the labor illusion](https://doi.org/10.1287/mnsc.1110.1376) · [Efendic et al. 2020, slow algorithms trusted less](https://ideas.repec.org/a/eee/jobhdp/v157y2020icp103-114.html) · [Response latency study, CHI 2026](https://arxiv.org/pdf/2604.06183)
- [Du et al., multi-agent debate](https://arxiv.org/pdf/2305.14325) · [Should we be going MAD?](https://arxiv.org/html/2311.17371v3) · [Zhang et al., Stop overvaluing MAD](https://arxiv.org/html/2502.08788v3)
- [LTO on ChatGPT and the RDG](https://www.lto.de/recht/nachrichten/n/chatpgt-openai-aenderung-nutzungsbedingungen-keine-rechtsberatung) · [OECD.AI, OLG Hamm chatbot incident](https://oecd.ai/en/incidents/2026-05-12-cfef)
