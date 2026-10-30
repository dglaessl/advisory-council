# Lead Engineer VM (OpenHands) — setup kit

A separate cloud VM where OpenHands does larger builds. It works on a fresh
clone, on branch `council/<task_id>`, and ends with a **draft pull request**.
It never merges and never pushes to `main`. Phase 2 seat.

Files: `cloud-init.yaml` (paste into the provider), `smoke-test.md` (run
after setup).

## How a task runs

```
oh-task OWNER/REPO TASK_ID task.txt
  1. fresh clone on the VM; branch council/TASK_ID
  2. OpenHands CLI, headless, in a throwaway container:
       sees the checkout and an output folder only
       (no .git metadata, no GitHub token, no docker.sock, no home folder)
  3. back on the VM: commit, show you the diff summary, ask "push? [y/N]"
  4. push council/TASK_ID, open a draft PR with the agent's PR.md
```

Why this shape: headless OpenHands approves every action itself (its docs
say this cannot be turned off), so the container is the safety line. The
GitHub token stays outside it, in the script that pushes. The push always
targets `refs/heads/council/<task_id>`, never `main`.

| Item | Setting |
|---|---|
| OS | Ubuntu 24.04 LTS, security updates automatic (no automatic reboot, so a long build is not cut off) |
| Login | user `builder`, SSH key only; root and passwords off |
| Firewall | inbound SSH (22) only; containers blocked from private networks and the cloud metadata address |
| Agent | OpenHands CLI 1.16.0 in local image `openhands-runner:1.16.0`, as uid 1000, all capabilities dropped, 4 GB RAM cap |
| Optional UI | Agent Canvas 1.34.0 on `127.0.0.1:8000`, off by default, no GitHub token |
| Secrets | `/etc/openhands/openrouter.env` (`LLM_API_KEY`) and `/etc/openhands/github.env` (`GH_TOKEN`), each one line, `chmod 600` |
| Model | `/etc/openhands/model.env` (not secret): `LLM_MODEL=openrouter/<provider>/<model>` |

## Before you start (15 min)

1. **OpenRouter key** just for the Lead Engineer, with a monthly limit.
2. **Your SSH key**: `cat ~/.ssh/id_ed25519.pub`; paste it over
   `SSH_PUBLIC_KEY_HERE` in `cloud-init.yaml`.
3. **Model.** Pick a strong coding model at <https://openrouter.ai/models>
   and edit `LLM_MODEL` in `cloud-init.yaml` (format
   `openrouter/<provider>/<model>`, e.g. `openrouter/anthropic/claude-sonnet-4.5`).
   You can change it later in `/etc/openhands/model.env`.
4. **GitHub token** (fine-grained, one repo at a time). GitHub → Settings →
   Developer settings → Personal access tokens → **Fine-grained tokens** →
   Generate new token:
   - Expiration: 30 days.
   - Repository access: **Only select repositories** → the one repo.
   - Repository permissions: **Contents: Read and write**, **Pull requests:
     Read and write**. Metadata: Read-only is added automatically.
   - Leave everything else at "No access": no Administration, no Workflows,
     no Secrets, no account permissions.
   For a different repo, create a new token and run `builder-set-keys github`.
5. **Protect `main`** on that repo (below).

## Branch protection for `main`

GitHub → repo → Settings → Rules → **Rulesets** → New branch ruleset:

- Name `protect-main`, Enforcement **Active**, Target: **default branch**.
- **Bypass list: empty** (rules then apply to you and your token too).
- Turn on: **Restrict deletions**, **Block force pushes**, **Require a pull
  request before merging** (required approvals: 0, because the PRs are
  opened with your own token and GitHub does not let you approve your own
  PR), and **Require status checks to pass** once the repo has CI.

Result: nothing reaches `main` except a merged PR. OpenHands never merges.
Per CLAUDE.md only the Chair merges, after Evaluator sign-off (and Quant &
Risk sign-off for trading code). Rulesets on **private** repos need GitHub
Pro (or a Team plan). Without it, the only guard is `oh-task` itself. The
agent never holds the token, but a stolen token could still push to `main`.

## Create the server

**Hetzner Cloud:** Add Server → Ubuntu 24.04 → **CX32 or larger (4 vCPU,
8 GB)** → your SSH key → firewall allowing only TCP 22 inbound → paste
`cloud-init.yaml` into **Cloud config** → name `lead-engineer`.

**DigitalOcean:** Droplet → Ubuntu 24.04 (LTS) x64 → 8 GB / 4 vCPU → your SSH
key → **Additional Options → Startup scripts (Free)** → paste the file →
then a Cloud Firewall allowing only TCP 22 inbound.

Wait about 8 minutes (it builds the runner image on first boot).

## First login and keys

```bash
ssh builder@<server-ip>
cloud-init status --wait                          # "status: done"
docker run --rm openhands-runner:1.16.0 --version # prints the CLI version
builder-set-keys                                  # OpenRouter key, then GitHub token (hidden)
```

If `docker` says permission denied, log out and back in (group change).
If `/var/run/reboot-required` exists, `sudo reboot`.

## Give it a task

```bash
nano task.txt        # plain-English task, acceptance criteria included
oh-task <you>/advisory-council 2026-10-30-add-unit-test-01 task.txt
```

The task id uses the council format `YYYY-MM-DD-slug-NN` (same as
`bridge/bridge.py`). Watch progress from a second SSH session:
`tail -f /srv/openhands/out/<task_id>/events.jsonl`. When it finishes you
see the changed files and decide whether to push. Then review the draft PR
on GitHub. The Chair records it with `bridge.py reply`.

## Optional: the browser UI

```bash
sudo systemctl start openhands-canvas
# on your laptop:
ssh -N -L 8000:127.0.0.1:8000 builder@<server-ip>
```

Open <http://127.0.0.1:8000/canvas>, set the OpenRouter model and key under
Settings → LLM. Projects live in `/srv/openhands/canvas-projects`. The UI has
no GitHub token. Use it for exploration; use `oh-task` for real work.
Stop with `sudo systemctl stop openhands-canvas`.

## Stop, update, destroy

- **Stop a running task:** `docker stop oh-<task_id>`.
- **Update OpenHands:** change `openhands==1.16.0` in
  `/opt/openhands/runner/Dockerfile` and the tag in `/usr/local/bin/oh-task`,
  then `docker build -t openhands-runner:<new> /opt/openhands/runner`.
- **Rotate keys:** revoke at OpenRouter / GitHub, then `builder-set-keys`.
- **Clean up old tasks:** `sudo rm -rf /srv/openhands/{work,git,out,state}/<task_id>`.
- **Destroy:** revoke the GitHub token and the OpenRouter key first, then
  delete the server in the provider console.

## Sources (checked 2026-10-28)

| Fact | Source |
|---|---|
| CLI install `uv tool install openhands --python 3.12` (or pip); config in `~/.openhands/` | docs.openhands.dev `openhands/usage/cli/installation` (OpenHands/docs repo, `main`) |
| `--headless` needs `-t`/`-f`; always auto-approves, cannot be changed; `--json` JSONL output | docs `openhands/usage/cli/headless` |
| `--override-with-envs` with `LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL` | docs `openhands/usage/cli/command-reference`; CLI source `openhands_cli/stores/agent_store.py` (1.16.0) |
| Working dir = `OPENHANDS_WORK_DIR` or cwd; actions run where the CLI runs (no Docker needed for headless) | CLI source `openhands_cli/locations.py`, `setup.py` (1.16.0 wheel) |
| Latest CLI `openhands` 1.16.0 (2026-05-08), Python 3.12 only | PyPI `openhands` |
| OpenRouter model strings `openrouter/<provider>/<model>` (LiteLLM) | docs `openhands/usage/llms/openrouter` |
| Agent Canvas image `ghcr.io/openhands/agent-canvas`, `-p 127.0.0.1:8000:8000`, no docker.sock; "agent can run arbitrary shell commands inside the container" | docs `openhands/usage/agent-canvas/setup`, `.../backend-setup/docker` |
| Agent Canvas latest 1.34.0 (2026-10-27) | npm `@openhands/agent-canvas` |
| Legacy GUI (`openhands serve`, `docker.openhands.dev/openhands/openhands`) mounts `/var/run/docker.sock`: **not used here** | docs `openhands/usage/run-openhands/local-setup` |
| Fine-grained PATs, rulesets | GitHub docs (not fetched here; settings names as of Oct 2026 may differ slightly) |

**Could not verify from here:** that the image tag
`ghcr.io/openhands/agent-canvas:1.34.0` exists (GHCR blocked from this
sandbox; npm 1.34.0 exists); that CLI 1.16.0 headless runs cleanly with no
TTY in a container (the source suggests yes); the newest Agent Canvas line
may replace the CLI later; the exact OpenRouter model id. The smoke test
checks these on the real server.
