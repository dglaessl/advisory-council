# Goose: Toolsmith (seat 3) run kit

Goose builds and tests the council's MCP servers and recipes. It is the only seat
allowed to touch files on your Mac, **only inside `~/council/goose-work`, and only
with your approval for each action** (R3). It never touches credentials, brokerage,
payments, messaging, publishing, account settings or deletion.

| File | Purpose |
|---|---|
| `goose-council.sh` | launcher: approve mode, safe permissions, Developer extension only, work folder, clean environment |
| `recipes/council-smoke.yaml` | smoke test: one file written, approval prompts, `.gooseignore` decoy check |
| `recipes/council-healthcheck.yaml` | read-only: Hermes and Agent Zero running and bound to 127.0.0.1 (one `docker ps`) |
| `recipes/mcp-server-scaffold.yaml` | build and test a small read-only MCP server (Python, `mcp==2.3.0`) |
| `templates/permission.yaml` | the tool permissions the launcher restores before every run |
| `templates/gooseignore` | global ignore file for credentials and agent data |
| `templates/config.example.yaml` | the council's `config.yaml` keys |

## 1. Install (macOS)

Goose moved from Block to the Agentic AI Foundation (AAIF). The packages keep the
`block-goose` names. Use the **CLI** for council recipes; Desktop is optional.

```bash
brew install block-goose-cli          # CLI (Homebrew listed 1.56.0 on 2026-10-28)
goose --version                       # expect 1.56.0 or newer; this kit was tested on 1.57.0
```
To pin the exact tested version instead of Homebrew:
```bash
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh \
  | GOOSE_VERSION=1.57.0 CONFIGURE=false bash      # installs to ~/.local/bin
```
Optional Desktop app: `brew install --cask block-goose`.

Don't run `goose update` on its own schedule: update on purpose, then rerun the smoke test.

## 2. OpenRouter key with a spend cap

1. Create a **separate** OpenRouter key named `goose-toolsmith`, and set a credit limit on
   the key (OpenRouter key settings). Use it for nothing else.
2. `goose configure` → **Configure Providers** → **OpenRouter** → paste the key (goose
   stores it in the macOS Keychain) → enter a model ID as OpenRouter lists it, e.g.
   `openai/gpt-6-luna`. CLAUDE.md allows any strong model for this seat.
3. Add the rest of `templates/config.example.yaml` to `~/.config/goose/config.yaml`.
   The one that matters is `GOOSE_MODE: approve`. The launcher refuses to run if the mode is
   anything else, and sets `GOOSE_MODE=approve` for its own runs anyway.

## 3. Approve every action

Goose has four modes: `auto` (the default: edits, runs and **deletes without asking**),
`approve` (Manual Approval), `smart_approve` (auto-approves what it thinks is low risk)
and `chat` (no tools). The council uses **`approve`**.

What testing on goose 1.57.0 showed (2026-10-28, with a local mock model):
- In approve mode, goose shows **Allow / Always Allow / Deny / Cancel** before a shell
  command. **Enter selects Allow.** Deny stops the command, and goose is told not to retry.
- **One "Always Allow" click is permanent:** goose writes the tool to
  `~/.config/goose/permission.yaml` (`always_allow: [shell]`), and every later shell command
  runs without asking. Making the file read-only does not stop this. **Never click Always
  Allow.** The launcher restores `templates/permission.yaml` before and after every run
  (keeping a timestamped backup) and warns you if it changed.
- Approve mode **cannot run headless.** `goose run` without `--interactive` stops with
  "Tool approval required in non-interactive mode" and runs nothing. So council recipes
  only run in a terminal you are watching. Don't schedule them, and don't switch to `auto`
  to make them run unattended.
- The recipes' own `extensions: developer` entry did **not** load the Developer tools under
  `--no-profile` in 1.57.0 (Developer is now a "platform" extension). The launcher adds it with
  `--with-builtin developer`, which gives exactly: shell, write, edit, tree, read_image (plus
  goose's internal load_skill and final-output tools).
- Goose 1.57.0's default profile also turns on Scheduler, Summon (subagents), Extension
  Manager, Apps and Top Of Mind. The launcher uses `--no-profile`, so recipes get none of
  them. If you use goose interactively outside the launcher, turn them off:
  `goose configure` → **Toggle Extensions**. Don't set up `goose gateway` (external
  messaging) or `goose schedule` for the council.

In Goose Desktop, the same setting is Settings → Chat → Mode → **Manual**.

## 4. Restrict it to the work folder

Goose has no built-in folder sandbox. The kit stacks these limits:
1. **Work folder:** the launcher `cd`s into `~/council/goose-work` (override with
   `GOOSE_WORK_DIR`; it refuses `$HOME` and `/`), and every recipe tells goose to stay inside it.
2. **Approval:** you see every shell, write and edit call before it runs. Read the path.
   Deny anything outside the work folder.
3. **`.gooseignore`:** the launcher installs `templates/gooseignore` as
   `~/.config/goose/.gooseignore` if you have none. It blocks `.env` files, keys, `~/.ssh`,
   `~/.aws`, `~/.config/council`, the agent data folders, Keychains and browser profiles for
   the Developer tools. Once this file exists, goose's built-in defaults (`.env`, `.env.*`,
   `secrets.*`) no longer apply, so the template restates them.
4. **Clean environment:** goose runs under `env -i` with only HOME, PATH, TERM, locale and
   `GOOSE_MODE=approve`. API keys or cloud credentials in your shell are not passed through.
   The ssh agent is passed only to the health check, for an ssh Docker context.
5. **Turn cap:** `--max-turns 25` (`GOOSE_COUNCIL_MAX_TURNS`).

For stronger isolation later, use a separate macOS user account for goose, or goose's
`--container` option (it runs extensions inside a container).

## 5. Run the recipes

```bash
cd ~/path/to/advisory-council/external/goose
mkdir -p ~/council/goose-work/smoke
echo "DECOY=not-a-secret" > ~/council/goose-work/smoke/.env.decoy   # for the ignore check

./goose-council.sh council-smoke
./goose-council.sh council-healthcheck                                 # on the machine running Docker
./goose-council.sh council-healthcheck --params docker_context=council # or via an ssh context
./goose-council.sh mcp-server-scaffold \
  --params server_name=ledger-reader \
  --params purpose="Read-only access to markdown files in ~/council/goose-work/ledger-export" \
  --params tools_spec="list_files(): names of .md files; read_file(name): text of one file, max 100 KB; read-only"
```

For the health check, the containers run on the council host (SETUP.md), so either run it
there or create a Docker context from your Mac once:
`docker context create council --docker host=ssh://USER@HOST` (you run that yourself, not goose).
The recipe runs exactly `docker --context <ctx> ps --all --no-trunc --format json` and
reports PASS only if `hermes` and `agent-zero` exist, are running, and every published port
is on 127.0.0.1 or ::1. Pass `--params hermes_name=...` / `agent_zero_name=...` if your
container names differ.

New MCP servers from the scaffold are **not registered anywhere**. Before using one: a Red
Team pass on its `SECURITY.md` and code, then you register it yourself.

### Smoke test checklist

`./goose-council.sh council-smoke` passes when:
- [ ] goose asks before each shell command and before writing `smoke/hello.txt` (choose Allow)
- [ ] `hello.txt` exists in `~/council/goose-work/smoke/` and nothing else changed
- [ ] the final JSON says `decoy_read_blocked: true` (`.gooseignore` works)
  - **Finding 2026-10-31 (goose 1.57.0, Sonnet 5.5): `.gooseignore` does not cover the
    shell tool.** A `cat` of `smoke/.env.decoy` ran and returned the file. The ignore file
    only guards the Developer read/write/edit tools. The real barrier for shell commands
    is your approval: **Deny any shell command that reads `.env`, key, credential or
    config files**, even inside the work folder. Keep real secrets out of the work folder.
- [ ] after the run, `~/.config/goose/permission.yaml` still matches `templates/permission.yaml`
- [ ] in a second run, choose **Deny** at the first prompt: the command must not run

Validate recipes after editing: `goose recipe validate recipes/<name>.yaml`.

## Hand-offs from the Chair

Envelopes for this seat use `target_seat: "toolsmith"`, `agent: "goose"`. Anything that acts
outside goose's sandbox is R3 and needs `approved_by_daniel: true` (bridge.py enforces this).
In Phase 2 you run the matching recipe by hand and paste the final JSON back to the Chair,
who records it with `bridge.py reply toolsmith ...`.

## Sources and verification (checked 2026-10-28)

| Fact | Source |
|---|---|
| Goose moved to the Agentic AI Foundation; repo `aaif-goose/goose`; install commands (`brew install block-goose-cli`, `brew install --cask block-goose`, `download_cli.sh` with `CONFIGURE=false`) | https://goose-docs.ai/docs/getting-started/installation |
| Homebrew `block-goose-cli` stable = 1.56.0 | https://formulae.brew.sh/formula/block-goose-cli |
| GitHub `stable` release = 1.57.0; `GOOSE_VERSION` pin in the install script | downloaded `download_cli.sh` and Linux binary from github.com/aaif-goose/goose/releases (`goose --version`) |
| Config file `~/.config/goose/config.yaml`; `GOOSE_PROVIDER`, `GOOSE_MODEL`, `GOOSE_MODE` (auto / approve / smart_approve / chat), `GOOSE_TELEMETRY_ENABLED`, `GOOSE_MAX_TURNS` | https://block.github.io/goose/docs/guides/config-files |
| Mode meanings, `/mode`, Desktop "Manual" | https://block.github.io/goose/docs/guides/goose-permissions |
| Per-tool permissions (Always Allow / Ask Before / Never Allow) | https://block.github.io/goose/docs/guides/tool-permissions |
| OpenRouter needs `OPENROUTER_API_KEY` | https://block.github.io/goose/docs/getting-started/providers |
| Recipe format (version, title, description, instructions, prompt, parameters, extensions, response.json_schema) | https://block.github.io/goose/docs/guides/recipes/recipe-reference and https://goose-docs.ai/docs/tutorials/recipes-tutorial |
| `goose run` flags (`--recipe`, `--params`, `--interactive`, `--no-profile`, `--with-builtin`, `--max-turns`, `--container`), `goose recipe validate` | https://goose-docs.ai/docs/guides/goose-cli-commands and `goose run --help` (1.57.0) |
| `.gooseignore` locations, defaults, Developer-only scope | https://goose-docs.ai/docs/guides/using-gooseignore |
| mcp 2.3.0 (2026-10-02): FastMCP renamed to `mcp.server.mcpserver.MCPServer`; in-process `mcp.client.Client(server)` for tests; pytest 9.2.0 | PyPI JSON API, plus a working test against the installed package |

**Tested here (Linux sandbox, goose 1.57.0, mock OpenAI-compatible model, 2026-10-28):** all three
recipes pass `goose recipe validate`; approve mode prompts before shell calls; Deny blocks;
headless approve mode refuses; "Always Allow" persists; the launcher refuses non-TTY runs,
restores permissions, installs `.gooseignore`, strips the environment and caps turns.

**Not verified:**
- No real model run and no run on macOS. OpenRouter setup through `goose configure` and Keychain
  storage come from the docs. The provider ID `openrouter` comes from the binary.
- Whether approve mode also prompts for `write`/`edit` (only shell was exercised; the
  permission template asks for all three) and whether `.gooseignore` patterns match absolute
  paths outside the work folder. The smoke test's decoy check covers the in-folder case.
- The docs disagree on whether approve mode asks for *all* tools or only "write" tools.
  Read-only tools such as `tree` may run without a prompt.
- The health check's interpretation of `docker ps` JSON is done by the model. Read its
  `ports` strings yourself the first time.
