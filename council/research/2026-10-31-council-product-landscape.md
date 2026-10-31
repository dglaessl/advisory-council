# Landscape scan: "the council sits" product (agenda item 4)

Date: 2026-10-31 | Author: Research Analyst | Status: partly verified (see per-section confidence)
Public sources only. Not employer-related. Vendor pages are marketing claims, not independent evidence.

## Answer
The "multi-model council" is already a crowded, cheap category: apps and tools charge about $9 to $195 a month and answer in seconds to minutes. Nobody I found sells a slow, scheduled sitting with minutes, recorded dissent, a published moral charter and a named, human-supervised process. That is real white space. The evidence that it can charge a premium is thin and mixed, because the "slow is better" research is weak for AI, and the "debate improves accuracy" research is contested.

## 1. Direct competitors (confidence: medium)

| Product | Price | Speed | Shows deliberation? | Named personas? |
|---|---|---|---|---|
| Suprmind | $19 / $45 / $95 / $195 per month; enterprise custom | No latency stated | Disagreement alerts, decision briefs | Modes (Debate, Red Team), not characters |
| SynthBoard | Free tier; paid pricing not found | Not stated | Multi-round debate, confidence, trade-offs | Yes: 24 role advisors (CFO, Skeptic, Lawyer) mapped to model families |
| The AI Council (iOS, Techniciti) | $8.99 one-off, BYO keys or credits | Not stated | Final synthesis plus confidence score; Debate mode shows arguments | Role modes only |
| Perplexity Model Council | Perplexity Max tier | "Slightly slower" than single model; no timings | Expandable per-model panels, disagreement badge | No |
| Karpathy "llm-council" and many clones | Free, open source | Minutes | Shows peer review | No |

Notes. SynthBoard already combines named roles, deliberate model-family assignment, and outcome tracking, which is the closest match to your concept. Its claim that real advisory boards cost $50K-$500K per year is its own marketing. I could not open the Karpathy repo (blocked in this session), so it rests on search listings only.

## 2. Adjacent products (confidence: medium)

| Category | Examples | Time / price |
|---|---|---|
| Deep research | OpenAI (5 to 30 min, per OpenAI); Gemini (several minutes, notifies when done, per Google); Perplexity (2 to 4 min); about $20/month entry tiers | Third-party figures, 2026-06 |
| Expert networks | GLG, AlphaSights | Pricing not public; negotiated annual contracts. Experts are paid roughly $100 to over $1,000 per hour (2022 article) and clients pay a markup |
| Marketplaces (Catalant) | Not verified | No pricing found |
| Second-opinion / decision-support | Not systematically surveyed | Gap in this scan |

Takeaway: AI research is $20/month and takes minutes; human expert calls cost hundreds to thousands per hour. A $50 to $500 per sitting price would sit between them, and needs a clear reason to exceed deep research.

Caveat: the 2026-06 comparison article claims Claude has no timed research agent. That looks wrong or stale to me. Anthropic's own timing is unverified here.

## 3. Labor illusion and slow service (confidence: medium on the effect, low on transfer to your product)

- Buell & Norton (Management Science, 2011): across five experiments in travel search and online dating, people sometimes preferred slower sites that showed work being done, even with identical results. The mechanism was reciprocity toward visible effort.
- Efendic et al. (OBHDP, 2020, seven studies, N = 1,928): the reverse for algorithms. Slow algorithmic predictions were trusted less, while slow human ones were trusted more.
- CHI 2026 experiment (N = 240, preprint 2026-02): 2-second chatbot answers were rated less thoughtful than 9 or 20 second ones, but trust did not differ and some users worried about reliability at long waits.
- All of these test waits of seconds, not hours or days. I found no evidence on multi-hour or fixed-cadence waits. Waiting a day is a different thing from a progress bar.

Implication: visible effort helps perceived value, but the argument for a fixed cadence has to rest on batching, quality, and ritual, not on this literature. The Efendic result warns that "AI is slow" can read as incompetence unless the work is shown and a human stands behind it.

## 4. Do multi-agent debate and ensembles improve quality? (confidence: medium)

| Evidence | Finding |
|---|---|
| Du et al. (ICML 2024, arXiv 2305.14325) | Debate between model instances improved reasoning and factuality |
| "Should we be going MAD?" (arXiv 2311.17371v3, 2024-07) | Debate does not reliably beat self-consistency; sensitive to tuning |
| Zhang et al. (arXiv 2502.08788v3, 2025-06) | Across 5 methods, 9 benchmarks, 4 models, debate often fails to beat chain-of-thought or self-consistency despite more compute; **heterogeneous models** consistently helped |

I did not find a primary source on Mixture-of-Agents in this scan. So: using different model families (your design) is the best-supported choice, but "more agents argue" is not shown to be better. Plan to test it yourself with the Evaluator, against a single strong model with self-consistency.

## 5. White space and crowding (confidence: medium)

| Element | Status |
|---|---|
| Multi-model synthesis, debate modes, confidence scores | Crowded; commoditised at $9 to $195 per month |
| Named role personas | Partly taken (SynthBoard) |
| Document upload, decision logs, export | Table stakes |
| Guided intake that admits or reshapes the question | Not seen in the tools above (not exhaustively checked) |
| Fixed cadence, formal minutes, recorded dissent, "what would change my mind" | Not found |
| Published moral charter as a customer guarantee | Not found. Closest analogue is Anthropic's published constitution for Claude (2026-01), which is a model-training document, not a service guarantee |
| Slow pace as a feature | Untested commercially |

Main risk: customers may see the slow cadence as a cost, and the charter and minutes as presentation over a process that, per section 4, may not be more accurate. Differentiate on accountability and framing quality, not on "more intelligence".

## 6. Regulated-advice risk (confidence: medium on direction, low on detail; not legal advice)

| Area | US | EU / DACH |
|---|---|---|
| Medical | Illinois (2025) bars AI from providing therapy; Nevada similar; other states are moving. Avoid diagnosis, treatment and dosing | Germany's Heilkunde and advertising rules apply; OLG Hamm (reported 2026-05) held a clinic liable for its chatbot's false claims about doctors' titles |
| Legal | Unauthorized-practice-of-law risk for case-specific advice | RDG section 2: individual legal review of a concrete matter is a regulated service; whether AI answers count is disputed (LTO, 2025-11-03). OpenAI itself restricted licensed-field advice (2025-10-29) |
| Financial | Investment-adviser and securities rules apply to personalised recommendations | BaFin and MiFID licensing for personalised investment advice (not verified here) |
| General | Disclose AI use; do not claim credentials | EU AI Act chatbot transparency duties; high-risk obligations scheduled 2026-08-02, but I could not confirm whether the "digital omnibus" delayed them. Check the official text |

Recommended exclusions: no diagnosis, treatment, personalised legal opinions, tax filing advice or personalised securities/crypto recommendations. Use "decision framing and analysis, not professional advice" wording, add a referral path to licensed professionals, and avoid personas titled "doctor" or "lawyer". Get a one-off lawyer review for the US and DACH before launch.

## Red flags
- Almost all competitor and pricing facts come from vendor pages or SEO articles; GLG/AlphaSights pricing is not public.
- Several sources are low-quality aggregator or marketing pieces (including the EU AI Act dev.to article and the 2026-06 deep-research comparison).
- Search results contained no instructions aimed at me.
- Gaps: Catalant, Anthropic Research timing, MoA paper, financial-regulation primary sources, AI Act delay status.

## Sources
- [Suprmind pricing](https://suprmind.ai/pricing) (retrieved 2026-10-31)
- [SynthBoard on G2](https://www.g2.com/products/synthboard/reviews)
- [The AI Council, App Store](https://apps.apple.com/us/app/the-ai-council/id6758050094) (v6.2.6, 2026)
- [Perplexity Model Council write-up](https://www.taxheal.com/?p=130237) (2026-05-16, secondary)
- [OpenAI, Introducing deep research](https://openai.com/index/introducing-deep-research/) (2025-02-02, updated 2026-02-10)
- [Gemini Deep Research](https://gemini.google/overview/deep-research/)
- [Deep research tool comparison](https://nesyona.com/articles/perplexity-vs-claude-vs-chatgpt-deep-research-2026) (2026-06-10, secondary)
- [CleverX, GLG vs AlphaSights](https://cleverx.com/blog/glg-vs-alphasights) (2026-09-01)
- [Expert network hourly rates](https://expertopportunities.com/expert-network-hourly-rates/) (2022-12-15)
- [Buell & Norton 2011, abstract](https://econpapers.repec.org/RePEc:inm:ormnsc:v:57:y:2011:i:9:p:1564-1579); [DOI](https://doi.org/10.1287/mnsc.1110.1376)
- [Efendic et al. 2020](https://ideas.repec.org/a/eee/jobhdp/v157y2020icp103-114.html)
- [Response latency study, CHI 2026](https://arxiv.org/pdf/2604.06183); [NYU summary](https://engineering.nyu.edu/news/why-faster-ai-isnt-always-better) (2026-04-23)
- [Du et al., multiagent debate](https://arxiv.org/pdf/2305.14325)
- [Should we be going MAD?](https://arxiv.org/html/2311.17371v3)
- [Zhang et al., Stop overvaluing MAD](https://arxiv.org/html/2502.08788v3)
- [LTO on ChatGPT and the RDG](https://www.lto.de/recht/nachrichten/n/chatpgt-openai-aenderung-nutzungsbedingungen-keine-rechtsberatung) (2025-11-03)
- [OECD.AI, OLG Hamm chatbot incident](https://oecd.ai/en/incidents/2026-05-12-cfef) (2026-05-12)
- [Illinois AI therapy ban coverage](https://www.deeplearning.ai/the-batch/illinois-follows-nevada-prohibiting-certain-uses-of-chatbots-unless-used-by-licensed-therapists) (search listing only, not opened)
- [EU AI Act DACH overview](https://dev.to/digitalcolliers/the-eu-ai-act-is-here-what-every-dach-business-needs-to-know-before-august-2026-1ef4) (vendor blog, weak)
- [Claude's Constitution coverage, Fortune](https://fortune.com/2026/01/21/anthropic-claude-ai-chatbot-new-rules-safety-consciousness/) (search listing only)
