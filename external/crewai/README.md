# CrewAI strategy panels: run kit (seat 7)

Three crews that turn a Bridge task envelope into a structured analysis for the Chair.
**Analysis only (R1).** No crew publishes, changes prices, contacts anyone, pays, or deletes anything.

| Crew | Seat | Roles (in order) | Script |
|---|---|---|---|
| Venture | `venture-crew` | market researcher → customer analyst → positioning strategist → pricing analyst | `crews/venture.py` |
| Hospitality | `hospitality-crew` | market comps → pricing → listing editor → agency-performance reviewer | `crews/hospitality.py` |
| Career & Offers | `career-crew` | AI-market scout → domain-fit analyst → offer designer → pricing analyst | `crews/career.py` |

## What a run does

1. `run.sh` validates the envelope on your Mac with the repo's `bridge/bridge.py validate`.
2. The container validates it again (bridge.py is copied into the image at build time;
   if it is ever missing, `_common.py` falls back to a mirror of its rules) and checks the
   seat matches the crew and the permission is R0/R1.
3. Files named in `input_context` are read **only** from the input folder, as data. URLs
   and `memory:` keys are listed but not fetched.
4. Four agents run in sequence. The last one returns JSON validated against a pydantic model.
5. Output in `<out>/<task_id>__<seat>/`:
   - `reply.json`: Bridge reply format (`task_id`, `status`, `output`, `notes`); `output` is the
     result JSON as a string. `status` is `needs_daniel` when the employment check says `conflict`,
     `failed` on errors.
   - `result.json`: memo, findings (each with a source or "model knowledge, unverified"),
     assumptions, confidence, open questions, `actions_requiring_daniel`,
     **`employment_conflict_check`**, plus `options` / `proposals` / `offers`.
   - `memo.md`: short memo for the Chair.

Every crew's final step fills `employment_conflict_check` (`clear` / `needs_review` / `conflict`,
plus outside-field, employer resources, IP-assignment and non-compete/non-solicit risk, and
clauses to check). The venture and career crews also check each option or offer, and the
overall status is the worst of them. It is a screen, not legal advice. The employer's field
comes from `CREW_EMPLOYER_FIELD` (the default text names the field, not the company).
The hospitality crew forces `needs_daniel_approval: true` on every proposal.

## One-time setup on your Mac

1. Docker Desktop installed and running (BuildKit is on by default; `--build-context` needs it).
2. An **OpenRouter key just for the crews**, with a monthly credit limit set on the key in
   OpenRouter's key settings.
3. Env file **outside the repo**, readable only by you:
   ```bash
   mkdir -p ~/.config/council
   printf 'OPENROUTER_API_KEY=%s\n' 'sk-or-...' > ~/.config/council/crewai.env
   chmod 600 ~/.config/council/crewai.env
   ```
   `run.sh` refuses the file if it is not `600` or sits inside the repo, and reads only the
   `OPENROUTER_API_KEY` line from it.
4. Build the image (the first `run.sh` call does this too):
   ```bash
   cd ~/path/to/advisory-council/external/crewai
   ./run.sh venture examples/venture-envelope.json --dry-run --build
   ```

## Running a crew

```bash
./run.sh <venture|hospitality|career> path/to/envelope.json [--dry-run] [--out DIR] [--input DIR]
```

- Output goes to `~/council/crewai-out` unless you pass `--out`.
- The input folder defaults to the envelope's own folder. Put the files listed in
  `input_context` there under the same relative paths. `run.sh` refuses to mount the repo
  root or your home folder.
- Model: `CREW_MODEL` (default `openrouter/openai/gpt-6-luna`). The format is
  `openrouter/<org>/<model>`, with `<org>/<model>` exactly as OpenRouter lists it. Anything not
  starting with `openrouter/`, or naming Anthropic/Claude, is refused (CLAUDE.md requires a
  non-Anthropic model for this seat). Example: `CREW_MODEL=openrouter/google/gemini-3.8-flash ./run.sh ...`.
- Replies are final: re-running the same `task_id` is refused. Send a new attempt (`-02`).
- To hand the result to the Chair: `python3 bridge/bridge.py reply <seat> <out>/<task>/reply.json`
  (after the task was sent and claimed through the Bridge as usual).

### Container limits (set in `run.sh`)

Input folder read-only at `/in`, output folder at `/out`, nothing else mounted, no
`docker.sock`, no published ports. Also `--read-only` root filesystem, `--cap-drop ALL`,
`no-new-privileges`, non-root user, 2 GB memory, 256 processes. Only `OPENROUTER_API_KEY` is
passed in, by name, so the value does not show up in `ps`. Dry runs use `--network none`.
CrewAI telemetry and tracing are switched off (`OTEL_SDK_DISABLED`, `CREWAI_DISABLE_TELEMETRY`,
`CREWAI_DISABLE_TRACKING`, `CREWAI_TRACING_ENABLED=false`, as read by crewai-core 1.15.33).
Real runs need outbound HTTPS to `openrouter.ai`. If you want to restrict egress further, do it
in Docker Desktop or with a proxy.

### Web search (optional, off by default)

The crews work without search: facts they can't source are labelled "model knowledge,
unverified". To enable Serper search for the first agent of each crew:
add `SERPER_API_KEY=...` to the same env file, then `./run.sh <crew> <envelope> --build --with-search`.
This installs `crewai-tools==1.15.33` and passes `SERPER_API_KEY` too. Search results are treated
as data. This is the only case where a second key enters the container.

## Smoke tests

Run each one. It must print `done: wrote /out/...` and create `reply.json`, `result.json` and `memo.md`.

```bash
# 1. Pipeline, no key, no network (placeholder content)
./run.sh venture     examples/venture-envelope.json     --dry-run --out /tmp/crew-smoke
./run.sh hospitality examples/hospitality-envelope.json --dry-run --out /tmp/crew-smoke
./run.sh career      examples/career-envelope.json      --dry-run --out /tmp/crew-smoke

# 2. Guards: each must fail with a clear message
CREW_MODEL=openrouter/anthropic/claude-x ./run.sh venture examples/venture-envelope.json   # non-Anthropic guard
sed 's/"R1"/"R2"/' examples/venture-envelope.json > /tmp/bad.json && ./run.sh venture /tmp/bad.json --dry-run --input /tmp   # R1 cap

# 3. Real run (costs a few cents; uses your key). Copy the example to a new task ID first:
mkdir -p ~/council/crew-in/notes && cp examples/notes/* ~/council/crew-in/notes/
sed 's/smoke-01/smoke-02/' examples/hospitality-envelope.json > ~/council/crew-in/hospitality.json
./run.sh hospitality ~/council/crew-in/hospitality.json
cat ~/council/crewai-out/2026-10-29-hospitality-smoke-02__hospitality-crew/memo.md
```

Check the real output: the memo is short, every proposal has `needs_daniel_approval: true`,
findings have sources or say "unverified", and `employment_conflict_check` is filled in.
Replace the sample notes in `examples/notes/` with your own (no guest personal data).

Unit tests (no Docker; the dry-run tests need `pip install -r requirements.txt` in a venv):
```bash
python3 -m unittest discover -s tests -v
```

## Files

| File | Purpose |
|---|---|
| `crews/_common.py` | envelope validation, context loading, LLM / stub LLM, output models, reply writing |
| `crews/{venture,hospitality,career}.py` | one entry point per crew |
| `crews/dispatch.py` | container entry point (`dispatch.py <crew> ...`) |
| `Dockerfile`, `.dockerignore`, `run.sh` | container build and hardened run |
| `requirements.txt` | `crewai==1.15.33`; `constraints.txt` pins all transitive versions |
| `requirements-search.txt` | optional `crewai-tools==1.15.33` |
| `examples/` | one valid envelope per crew, plus sample notes |
| `tests/test_crews.py` | envelope, context, model-guard, reply and dry-run tests |

## Sources and verification (checked 2026-10-28)

| Fact | Source |
|---|---|
| crewai 1.15.33 is the latest release (uploaded 2026-10-28T20:53 UTC); requires Python >=3.10,<3.14 | PyPI JSON API, https://pypi.org/pypi/crewai/json |
| crewai-tools 1.15.33 is the latest | https://pypi.org/pypi/crewai-tools/json |
| OpenRouter is a **native** provider in crewai 1.15.x: model string `openrouter/<org>/<model>`, key from `OPENROUTER_API_KEY`, base URL `https://openrouter.ai/api/v1`; litellm is now an optional extra and is not needed | installed source: `crewai/llm.py` (`SUPPORTED_NATIVE_PROVIDERS`), `crewai/llms/providers/openai_compatible/completion.py` |
| Telemetry switches: `OTEL_SDK_DISABLED`, `CREWAI_DISABLE_TELEMETRY`, `CREWAI_DISABLE_TRACKING`; tracing: `CREWAI_TRACING_ENABLED` | installed source: `crewai_core/telemetry.py`, `crewai/events/listeners/tracing/` |
| `openai/gpt-6-luna` is an OpenRouter model ID | https://openrouter.ai/models/openai/gpt-6-luna (search result, 2026-10-28) |

**Tested here (Linux sandbox, 2026-10-28):** all three crews in `--dry-run`, both directly with
Python 3.13 and through `run.sh` in the container (read-only root, no network, bridge.py
validator); the guards above; a real run with a fake key, which reached the OpenRouter call
and wrote a valid `failed` reply. 11 unit tests pass.

**Not verified:**
- No real model call was made (no key, and the sandbox can't reach OpenRouter). The first real
  run is smoke test 3.
- Docker Hub was blocked here, so the image was built on a stand-in Python 3.13 base, not
  `python:3.13-slim`, and only on x86_64. Your Mac's first build (arm64, real base) is untested.
- docs.crewai.com was not reachable from here. The OpenRouter format comes from the installed
  1.15.33 source, not the docs page.
- crewai ships releases almost daily (1.15.31–1.15.33 came out on 2026-10-27/28). Bump the pin
  on purpose, rerun the tests, and regenerate `constraints.txt` with `pip freeze`.
