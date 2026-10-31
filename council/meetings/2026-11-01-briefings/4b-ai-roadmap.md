# 4b. Daniel's AI-expert road map (Nov 2026 – Jan 2027)

**Seat:** AI Tutor & Portfolio Lead · **Mode:** learning · **Draft written alone, without seeing other seats' views** · 2026-10-31
**Scope:** the AI-skills part of agenda item 4, plus proposal E. The side-business choice is a separate decision; this plan works for each of the three directions on the shortlist.

## 1. Skills baseline (0 none · 1 aware · 2 can use · 3 can build · 4 can teach)

Ratings count what Daniel built, decided or explained between 2026-10-23 and 10-31. Claude did most of the coding, so "can build" here means he designed the thing, decided the trade-offs and ran it. A short explain-back at the meeting (one question per area) confirms each 3. Without it, the area stays at 2.

| Area | Now | Evidence (done, not read) | Gap |
|---|---|---|---|
| LLM fundamentals (tokens, context, cost) | **2** | Chose a model for each seat across three model families. Assigned the long-context audit to Gemini. | Doesn't track spending per seat (proposal D). No cost or latency numbers for any engagement. |
| Prompting and system prompts | **3** | Wrote and revised the Chair prompt and the trading rulebook. Changed rules after failures, for example dropping limit entries after they filled 0 of 5 times. | Doesn't keep prompt versions or compare a change against an eval. |
| Evals and measurement | **2** | Set up the pre-registered strategy review, the backtests, the tabletops and the bridge regression tests (28/28). All of them check code or trading. | **No eval of LLM output quality** (guest messages, research answers). No checks that an LLM judge agrees with Daniel. |
| Agents and orchestration | **3** | A council of 3 model families with a Bridge envelope and R0–R3 permissions. A cloud trading agent with a run lock, reconciliation, a heat cap and NAV tracking. A host agent. | Hasn't explained or published how it's built (that's level 4). Orchestration is manual. |
| Memory systems | **2** | Uses the journal as agent state, the decision log with revisit dates, and Hermes as system of record. | Hasn't designed retrieval and doesn't know when files stop being enough. |
| Tool use and MCP | **2** | Uses the Robinhood, Strava and Docs connectors. Built the Strava sync into the Ledger. | Hasn't written an MCP server or designed a tool's interface. |
| Agent security | **3** | Quarantined OpenClaw on a VM and parked it after it failed checks. Ran cross-model red-teaming. Decided that capabilities are the boundary and filters are only a tripwire. Set Phase 2 gates. | No threat model written in his own words. Data tiers for external seats are still open (proposal B). |
| Fine-tuning and RL | **0** | No evidence. | Needs enough grounding to judge when fine-tuning beats prompting. |
| AI product strategy and pricing | **2** | Three side-business ideas, naming criteria, and the employment-conflict boundary. Product judgement in his own field is at level 4. | No AI offer tested and no price set or tried with a customer. |

**Weakest area to target in November: evals.** Fine-tuning is lower, but evals pay off more. They're the skill clients hire for, and every direction on the shortlist needs them (owner-facing host agent, council product, longevity research).

## 2. Twelve-week build plan (about 5 h on weekdays plus a weekend block; lighter weeks around Thanksgiving and Christmas)

Each build has a clear "done", teaches one concept, and feeds a live project. Weeks 9–12 adapt to whichever direction Daniel picks in November. **Housing and real estate stay out of every public build.**

| Wk | Starts | Build → done when | Concept | Direction it serves | Public? |
|---|---|---|---|---|---|
| 1 | Nov 2 | **Red-team findings ledger.** Backfill rounds 1–2 into `evals/council/redteam-findings.csv` (schema in §3). Then run a **control**: the same brief, through a Claude-based red team, on the snapshot from before the fixes. Done when every finding is a row with its overlap marked. | Designing eval data. Testing a claim with a control. | Council product | Yes, after redaction |
| 2 | Nov 9 | **Guest-message eval for the host agent.** 30 synthetic guest messages. Daniel labels each reply pass/fail with a reason. An LLM judge must agree with his labels on ≥ 80% of messages. | Error analysis. Aligning an LLM judge with a human. | Host agent | The method; never guest data |
| 3 | Nov 16 | **Article v1:** "What a second AI found in my AI council". The redaction checklist passes and the Red Team attacks the draft for leaks. **Needs a check of the employment terms on public writing first.** | Teaching (level 4) | All three | Yes |
| 4 | Nov 23 | **Cost meter (light week).** Cost per seat and per engagement for October–November from the OpenRouter and Anthropic usage data, plus a monthly spending cap. | Tokens, context and cost | Council (proposal D) | Aggregated figures only |
| 5 | Nov 30 | **Replay eval for the trading agent.** Freeze 5 past cycles (journal plus market data), run the agent's decisions again and score rule compliance. Done when the score is reproducible run to run. | Evaluating agent trajectories | Council product | The method; no account data |
| 6 | Dec 7 | **Decision-log recall.** 15 questions about past decisions. Compare grep plus long context against embedding retrieval on accuracy, citations and cost. Write down the choice. | Trade-offs in memory and retrieval | Council product | Yes |
| 7 | Dec 14 | **His own MCP server, built with the Toolsmith.** 3 read-only tools (for example Casa La Fonte availability and rates, from a public calendar feed), with tests and a Red Team security pass. | Tool design and least privilege | Host agent | Yes, as an open-source template |
| 8 | Dec 21 | **Teach-back talk (light week).** A 15-minute recorded walkthrough of the council's design: seats, trust rules, the Bridge. | Teaching (level 4) | Council product | Yes, after redaction |
| 9 | Dec 28 | **Package the chosen direction.** For example "council-in-a-box" (prompts, seats, Bridge, evals, no secrets) or a host-agent onboarding kit. Done when someone else can install it in under an hour. | Turning configuration into a product | Chosen direction | Yes |
| 10 | Jan 4 | **Fine-tuning vs prompting.** Fine-tune a small open model on the week-2 data (synthetic, ≤ $20) and score it on the week-2 eval against the prompted baseline. | When fine-tuning pays off (usually it doesn't) | Host agent | Yes |
| 11 | Jan 11 | **Accuracy eval for the Scientific Researcher.** 10 longevity questions with known answers from public papers, scored on citation accuracy and effect size. Used to accept or reject the planned seat. | Evaluating research agents | Longevity | Yes; uses no Ledger data |
| 12 | Jan 18 | **Offer test,** only after the conflict check passes. A one-page offer and a price hypothesis for the chosen direction, sent to 5 people for discovery calls. Then the 3-month review of the skills map. | AI product strategy and pricing | Chosen direction | Yes |

**Core resources (each confirmed to exist on 2026-10-31):**
- Anthropic, *Building effective agents*: https://www.anthropic.com/engineering/building-effective-agents. Workflows vs agents, and when to keep things simple (weeks 6, 9).
- Hamel Husain, *Your AI Product Needs Evals*: https://hamel.dev/blog/posts/evals/ and the *Evals FAQ*: https://hamel.dev/blog/posts/evals-faq/. Error analysis and judge alignment (weeks 2, 5, 11).
- Simon Willison, *The lethal trifecta for AI agents*: https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/. A plain-language threat model to frame the article (week 3).
- Chip Huyen, *AI Engineering* (O'Reilly, 2025): https://www.oreilly.com/library/view/ai-engineering/9781098166298/. The evaluation and finetuning chapters (weeks 2, 10).

## 3. First public piece: the cross-model red-team story

**Working title:** "What a second AI found in my AI council". Source: decision log `2026-10-28-phase1-red-team-review`.

**Outline (about 1,500 words):**
1. *Hook.* A GPT-based agent attacked a Claude-designed system. In one finding it replaced the Red Team's own dissent with a forged reply.
2. *Setup.* What the council is and why it uses three model families. One diagram, no seat secrets.
3. *Method.* A sanitized snapshot, the attack brief, the rule that a second model reproduces a finding before anyone fixes it, a regression test for each fix, then a re-attack.
4. *Three findings as stories:* (a) a keyword filter mistaken for authorization, beaten by paraphrase ("filters aren't boundaries"); (b) dissent overwritten through a shared task ID; (c) a trailing newline slipping past `re.match` and `$`, a real but small bug.
5. *Numbers.* Findings by round and severity, share reproduced, tests 17 → 28, cost and time (from week 1 onward).
6. *What stayed open.* OS-level seat identity and verified isolation. Being honest about the gaps adds credibility.
7. *Takeaways for teams adopting agents.* A checklist of 5 items.
8. *Credit, stated plainly.* Daniel designed the process and made the calls. Claude reproduced and fixed the findings, and GPT attacked. The article says so.

The week-1 control decides one framing choice. If a Claude red team finds the same issues, the claim becomes "adversarial review works" rather than "model diversity works". Publish whichever the data supports.

**Redaction checklist (each item is checked by the Red Team before publishing):**
- [ ] Nothing about the employer: name, products, colleagues, and no work time or devices used to write it. Public-writing terms checked.
- [ ] No financial data: the 2149 account, balances, positions, P&L, deposit amounts.
- [ ] No health or Ledger data: no peptides, labs or metrics. No guest data from Casa La Fonte.
- [ ] No secrets or infrastructure details: keys, hostnames, IPs, VM or provider details, Telegram IDs, Agent Zero chat IDs.
- [ ] Gaps that are still open are described as classes of problem, never as working exploit steps.
- [ ] No family members, and no home locations beyond "Austin".
- [ ] Code excerpts are rewritten or reduced to the minimum. Check provider terms on publishing model outputs.
- [ ] The snapshot canary scan has been run on any repo or gist that gets linked.

**Metrics to log from today** (`evals/council/redteam-findings.csv`, one row per finding; the Evaluator owns it):
`finding_id, date, round, attacker_model, target_component, category (authz | injection | integrity | concurrency | data-leak | availability | process), impact, likelihood, reproduced_by, repro_minutes, unique_to_model (Y/N/untested), false_positive, fixed, fix_minutes, regression_tests_added, reattack_result, changed_recommendation (Y/N)`.
Per engagement: tokens and $ for each seat, wall-clock time, and Daniel's hands-on minutes.

## 4. Monthly measurement (scorecard row "AI skills and portfolio")

| Metric | How | Target by Jan 31 |
|---|---|---|
| Skills-map levels | The Tutor re-rates each area. A rating counts only with a linked artifact plus an explain-back. | Evals, memory, MCP, strategy 2 → 3. Agents and security 3 → 4. Fine-tuning 0 → 2. |
| Builds shipped | Weekly builds that met their "done" | ≥ 10 of 12 |
| Explain-back quiz | 5 questions a month, each scored 0–2 | ≥ 8/10 by January |
| Eval coverage | Share of live projects with an eval that runs | 3 of 3 (trading, host agent, Ledger method) |
| Portfolio | Pieces shipped and how many are public | 3 shipped, ≥ 2 public |
| Red-team value | Findings, % reproduced, % unique to the model, recommendation changes | Logged every engagement |
| Monetization | Offers tested, conversations, revenue (after the conflict check) | 1 offer, 5 conversations |
| Cost of learning | $ and hours per build | Under the cap set in week 4 |

**Decisions for Daniel:** (1) Approve evals as November's focus. (2) Approve starting the log today. (3) Check the employment terms on public writing before week 3. (4) Pick the direction for weeks 9–12 by Nov 30.
