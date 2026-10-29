# CrewAI — Strategy Panels (Phase 3)

**Seats:** `venture-crew`, `hospitality-crew`, `career-crew` · **Max permission:** R1

Run on a **non-Anthropic** model (cheaper open-weight is fine for routine
runs; see the cost notes in the decision log).

## Crews
| Crew | Roles (in order) | Serves |
|---|---|---|
| Venture | market researcher → customer analyst → positioning strategist → pricing analyst | side business (focus not settled; longevity/health was one first idea) |
| Hospitality | market comps analyst → pricing analyst → listing editor → agency-performance reviewer | Casa La Fonte |
| Career & Offers | AI-market scout → domain-fit analyst → offer designer → pricing analyst | long-term horizon |

## Contract
- Each crew is one Python entry point (`crews/<crew>.py`) that takes a
  Bridge envelope and returns JSON: `{"memo": "...", "findings": [...],
  "assumptions": [...], "confidence": "...", "employment_conflict_check": {...}, ...}`
  as a Bridge reply (`reply.json`) plus `memo.md`. Run kit and details: `README.md`.
- Analysis only. Crews never publish listings, change prices, contact the
  agency, guests or customers, or touch payment systems.
- Every crew's final step fills an employment-conflict check; the Career &
  Offers and Venture crews check each offer/option (outside-work, IP,
  non-compete) before it is proposed.
- No guest personal data goes into the Hospitality Crew.
