# Red Team security pass on the new seats (2026-10-31)
*Agent Zero, red-team profile (GPT). Read-only. Task 2026-10-31-redteam-seat-security-01. Summarized by the Chair; the full text is in Agent Zero chat dCYDKkrD.*

**Verdict:** proceed with changes. Isolate Goose before any sensitive work, and close the gaps in credentials, network egress and repository integrity.

| # | Sev | Finding | Fix |
|---|---|---|---|
| 1 | H | Goose isn't sandboxed. Daniel's approval is the only boundary, and an approved shell command runs with his full user access. `templates/gooseignore` still claims it covers the shell. | Run Goose extensions in a container or under a dedicated macOS user, with only the work folder mounted and restricted egress. Correct the template. |
| 2 | H | OpenHands has open internet egress. A prompt injection, or a malicious test that the agent runs, could send checkout files and `LLM_API_KEY` out. | Keep the model key in a broker outside the agent, and restrict egress to an allowlist of destinations. |
| 3 | H | Confidential files are still in git history, reachable with the host-side GitHub token. This is not a direct leak path for the agent itself, since `.git` and the token are kept out of its container. | Give the builder a token for a sanitized repo only, or purge the history. |
| 4 | H | `main` has no branch protection. The wrapper stages every change and continues even after the agent exits with an error. | Add a ruleset on `main`, fail closed on a non-zero exit, and enforce which paths a task may change. |
| 5 | M | CrewAI can leak the context it's given through model or search traffic, and can be steered by injected text. The Docker network is open. | Use a minimal folder per task, an egress allowlist, and review of the output. |
| 6 | M | The VM egress rules don't cover 172.16.0.0/12, IPv6, or inbound traffic to the host. | Fix the rules and test them, and keep the Scout disabled. |
| 7 | M | The OAuth key Goose created has no spending cap. | Set a $15 cap and revoke the unused key. |

**Sound as found:** non-root containers, no docker.sock mounts, UIs bound to localhost, Goose's permission reset, and the Scout's install quarantine.
