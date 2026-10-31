# Item 3 · Longevity Ledger: data audit and pre-registered analysis plan

Prepared 2026-10-31 for the 2026-11-01 meeting (proposal C). Data read-only from the Ledger database at about 14:30 UTC. **No outcome trends or correlations were computed.** Aggregates only. Not medical advice: clinical points are questions for Daniel's physician.

## 1. Data inventory

| Source (collection) | Range | Days with data | Completeness and quality |
|---|---|---|---|
| Apple Health via Health Auto Export (`health`, `settings/health`) | 22–29 Oct 2026 | 8 (22 Oct partial: temperature and breathing only) → **7 usable** | One file per day, imported 1–3 days late; 30–31 Oct not in yet (last sync today, file of 29 Oct). RHR, HRV (SDNN), SpO₂, respiration, steps and wrist temperature are present 7/7. **Nothing before 22 Oct**, so there is no pre-peptide baseline in the Ledger. |
| Sleep, nightly (inside `health`) | 23–29 Oct | 7 nights | **The device changes from night to night**: 3 Apple Watch, 4 Oura, never both on the same night. Bedtime is consistent except one late night. Pre-period available only as an **Oura 90-day aggregate** (22 Jul–19 Oct) in `labs`, not daily. |
| Morning/evening check-ins (`checkins`) | 20–31 Oct | 12 AM / 7 PM (some partial) | Seated and standing BP, Oura/Watch sleep scores, deep/REM, temperature deviation: 12/12. Typed RHR/HRV/sleep only 20–23 Oct (4 days). On the one overlap day, **typed HRV was about twice the Watch value and typed RHR much lower**: different devices or metrics, so don't mix them. **Weight is the same value all 12 days**, probably a carried-over default and not a real reading. Symptoms and notes are empty on every day. No PM check-in on 24, 25, 29 and 31 Oct. |
| Intake log (`checkins.intake`) | 20–31 Oct | 12 | Only ticked items are stored, so a missing tick reads as "unknown", not "skipped". Peptide ticks match the schedule except **Sermorelin on Thu 29 Oct (scheduled, no tick)**. No alcohol, travel or illness field exists. |
| Protocol (`protocol/current`, 37 items) | updated 25 Oct | — | Start and stop dates for peptides are recorded. Zepbound and the other Rx/supplements are "ongoing" **with no start date**. |
| Strava (`training`, `settings/strava`) | 31 Oct 2025–31 Oct 2026 | 544 activities on 285 days; no gap > 7 days | **Sync is current**: last sync today 14:19 UTC, newest activity this morning. No duplicate IDs. 2 near-duplicate pairs (28 Dec 2025, 21 Mar 2026) to drop. HR on ~99% and Relative Effort on 86/87 in the last 90 days. No TSS. One max HR above the profile max HR (Jan 2026; probably an artefact). Location: Austin for all of Oct except one Bay Area activity on 17 Oct. |
| Labs (`labs`) | Jul 2025–Mar 2026 | 3 blood panels (Labcorp Jul 2025; Quest Oct 2025 and Mar 2026), urine toxins, InBody (Jan), DEXA (Mar), genetics, Oura report | Unit labels differ but mean the same (U/L vs IU/L etc.); mixing labs adds some variability. **IGF-1 was measured only in Jul 2025.** |
| Baselines (`settings/profile`) | — | — | RHR/HRV baselines were **reset on 27 Oct from 23–27 Oct**, which is already during GHK-Cu and Sermorelin, and from a different source than before. They are not a clean pre-exposure baseline. |
| Unused: `nutrition` (empty), `reports`, `healthdebug` (import logs) | | | |

**Bottom line:** Strava is strong (one year of data). Daily physiology covers only 7 days, all during exposure. Proposed fix before Sunday's computation: **a one-off Health Auto Export backfill for 22 Jul–21 Oct** (to match the Oura 90-day window). Without it, the peptide before/after comparison cannot be run.

## 2. Pre-registered analysis plan (fixed before results)

**Main metrics (5):** (1) Apple Watch daily resting HR; (2) Apple Watch HRV (SDNN), analysed as ln-HRV; (3) sleep duration; (4) sleep timing consistency, as the SD of the sleep midpoint over 7 nights; (5) training load, as Strava Relative Effort per day, 7-day sum and 7:28-day ratio. Secondary safety readout, descriptive only: seated and standing morning BP. One source per metric. Sleep: Oura is primary (it has the pre-period aggregate); Apple Watch nights are reported separately, never spliced together.

**Exposures (as recorded):** GHK-Cu 19 Oct→13 Dec (daily) · Sermorelin 22 Oct→18 Dec (Mon–Fri, bedtime) · Thymosin α-1 26 Oct→17 Dec (Mon/Thu) · Semax 2 Nov→13 Nov (Mon–Fri). Background, assumed stable: Zepbound (weekly, Fri), Metformin, Hair Rx (paused 6–8 Nov), about 25 supplements (most paused 21–27 Dec). Later events, each its own window: senolytic pulse 17–18 Nov and 15–16 Dec, fasting-mimicking diet 19–23 Dec.

**Windows and lags:**
- *Primary contrast:* pre-period (28 days, 21 Sep–18 Oct, needs the backfill) vs the "full stack" (26 Oct–1 Nov, then each later 7-day block). Because the peptides started 3–7 days apart, **the stack is treated as one exposure**. Phases A (19–25 Oct), B (26 Oct–1 Nov), C (+Semax, 2–13 Nov) and D (from 14 Nov) are shown descriptively only.
- Each window is computed twice: with and without a 3-day wash-in after each start.
- *Exploratory, not before mid-December:* Sermorelin nights vs non-dose nights → next-morning RHR, HRV and sleep (about 30 vs 12 nights by then). Same for Thymosin α-1 days.
- *Sleep → next day:* night ending on the morning of day d vs RHR and HRV on day d (lag 0) and day d+1 (lag 1). Rank correlation only once there are at least 28 paired days.

**Confounders, flagged per day:** training load (prior day and 7-day); travel (Strava location outside Austin, or a time-zone offset change in the export, ±2 days); illness (Oura temperature +1.0 °F or more, or a logged symptom); alcohol (**not logged; add a field now**); several changes on the same day or week; device switch; Zepbound day of week; Hair Rx pause; blood draw day; **US clocks fall back on 1 Nov**, so sleep timing is analysed in local time with that night flagged. Flagged days stay in the data, and a sensitivity run excludes them.

**Method:** descriptive first. Daily values → 7-day rolling medians. Phase medians with IQR. Change vs the pre-period expressed in units of the pre-period SD of 7-day means. Two primary questions: H1 RHR, H2 ln-HRV, stack vs pre. Everything else is exploratory. Roughly 5 metrics × 4 phases × 2 lags ≈ 40 looks, so about 2 false "hits" are expected by chance. No p-value drives a decision; if a test is run, it uses α = 0.05/40.

**"Worth discussing with the physician":** a change in H1 or H2 that is larger than 2 pre-period SDs, lasts at least 14 days, survives both wash-in variants and the flagged-day exclusion, and is not explained by a change in training load. Separately, any trigger of the Ledger's existing stop/pause rules (BP, orthostatic drop, RHR ≥ baseline+5 or HRV < 80% for 3 days, temperature) goes to the physician whatever the statistics say. Anything else is **noise or "watch"**.

**What will not be concluded:** that any single peptide caused anything (the starts overlap); dose-response; efficacy or safety in general; anything from fewer than 14 days of exposure; anything about long-term longevity outcomes. This is one person's observational data, so associations are not effects.

## 3. Upcoming items

**9 Nov week-6 blood draw (Mon). Questions for the physician:**
- Add **IGF-1**? It was last measured in Jul 2025, and Sermorelin acts on the GH/IGF-1 axis.
- Fasting glucose, **fasting insulin** and **HbA1c** (GH axis, alongside Metformin and Zepbound)?
- **Liver panel** (ALT, AST, GGT) and **hs-CRP**? (Note any fever or temperature rise before the draw.)
- **CBC with differential/lymphocytes**, given Thymosin α-1?
- **Copper, zinc and ceruloplasmin**, given GHK-Cu?
- **Thyroid panel** (TSH, free T4, free T3), given the GH-axis peptide?
- Kidney function: is **cystatin C** needed, since creatine raises creatinine?
- **PSA**: how should it be read on finasteride?
- **Biotin** (in Hair Rx) interferes with some immunoassays. Is the 6–8 Nov pause long enough?
- Prep: fasted, same lab as March (Quest), morning, no hard session in the prior 48 h.

**10 Nov RHR/HRV baseline recheck:** fix it now as the Apple Watch median of 3–9 Nov. Caveats: Semax starts 2 Nov, the Hair Rx pause falls inside that window, and the clock change is on 1 Nov. Label it as an on-stack reference, not a true baseline.

**DEXA around Thanksgiving (26 Nov):** use the same device and provider as Mar 2026 (Hologic). Fasted, same time of day, no training that morning. Compare only with the March DEXA (InBody isn't comparable). Ask the physician which change in lean and visceral fat is meaningful given Zepbound.

## 4. Data-sharing note (interim rule, proposal B)

Only aggregated, redacted summaries go to non-Claude seats (Red Team, Auditor):
- **Safe to share:** this plan's method section with compounds replaced by "Exposure 1–4" and phase labels; completeness counts; per-phase medians/IQR rounded; confounder flag counts; the yes/no "worth discussing" outcome.
- **Not shareable:** raw daily rows, check-ins, intake logs, lab values, genetics, the protocol document, compound names with doses, name, date of birth, Strava locations/GPS, and Drive folder or file IDs.
- `council/meetings/` isn't in `bridge/make_snapshot.sh`'s allowlist, so this file stays out of snapshots. **Never pass it as an extra path.** `council/decision-log/` **is** allowlisted, so the Scribe's log entry for item 3 must hold aggregates only.
