# CrewAI — Strategy Panels (Phase 3)

**Seats:** `venture-crew`, `hospitality-crew`, `career-crew` · **Max permission:** R1

Run on a **non-Anthropic** model (cheaper open-weight is fine for routine
runs; see the cost notes in the decision log).

## Crews
| Crew | Roles (in order) | Serves |
|---|---|---|
| Venture | market researcher → customer analyst → positioning strategist → pricing analyst | side business (longevity/health niche) |
| Hospitality | market comps analyst → pricing analyst → listing editor → agency-performance reviewer | Casa La Fonte |
| Career & Offers | AI-market scout → domain-fit analyst → offer designer → pricing analyst | long-term horizon |

## Contract
- Each crew is one Python entry point (`crews/<crew>.py`) that takes a
  Bridge envelope and returns JSON: `{"memo": "...", "findings": [...],
  "assumptions": [...], "confidence": "..."}`.
- Analysis only. Crews never publish listings, change prices, contact the
  agency, guests or customers, or touch payment systems.
- Career & Offers Crew: every offer includes an employment-conflict check
  (outside-work, IP, non-compete) before it is proposed.
- No guest personal data goes into the Hospitality Crew.
