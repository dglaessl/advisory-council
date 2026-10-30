# Field Scout VM (OpenClaw) — setup kit

A small, throwaway cloud VM that runs OpenClaw under quarantine. It holds
**one** secret (its own OpenRouter key), reaches the web, and leaves plain
Markdown findings in a drop folder that the Chair pulls. Nothing on this VM
can reach the council host, your Mac, or any account.

Files: `cloud-init.yaml` (paste into the provider), `smoke-test.md` (run
after setup). Phase 3 seat on probation: review after 60 days.

## What the VM does

| Item | Setting |
|---|---|
| OS | Ubuntu 24.04 LTS, security updates automatic (reboots 04:30 UTC if needed) |
| Login | user `scout`, SSH key only; root and passwords off |
| Firewall | inbound SSH (22) only; containers blocked from private networks and the cloud metadata address |
| OpenClaw | container `ghcr.io/openclaw/openclaw:2026.10.8`, as uid 1000, all capabilities dropped, no docker.sock |
| UI | `127.0.0.1:18789` on the VM, token login; you reach it only through an SSH tunnel |
| Agent tools | `web_fetch`, and read/write/edit inside its workspace. No shell, no terminal, no browser, no cron, no messaging, no sub-agents |
| Skills/plugins | none loaded; every install is refused by an install policy |
| Secrets | `/etc/openclaw/openrouter.env` (your key, root only) and `/etc/openclaw/gateway.env` (UI token, generated on boot) |
| Drop folder | `/srv/openclaw/scout-inbox/` (the agent sees it as `scout-inbox/` in its workspace) |
| Pickup | user `courier`: one SSH key, read-only rsync of the drop folder, nothing else |

## Before you start (10 min)

1. **OpenRouter key** just for the Scout, with a low monthly limit set in
   the OpenRouter console.
2. **Your SSH key** (on your laptop): `cat ~/.ssh/id_ed25519.pub`. If you
   have none: `ssh-keygen -t ed25519`.
3. **Courier key** (on the council host, where the Chair runs):
   `ssh-keygen -t ed25519 -N "" -f ~/.ssh/scout_courier`, then
   `cat ~/.ssh/scout_courier.pub`.
4. Open `cloud-init.yaml` in a text editor. Replace `SSH_PUBLIC_KEY_HERE`
   with line 2 and `COURIER_PUBLIC_KEY_HERE` with line 3 (keep the quotes
   and the `command=...` part in front of it).

## Create the server

**Hetzner Cloud:** Add Server → Ubuntu 24.04 → type CX22 or larger (2 vCPU,
4 GB RAM) → add your SSH key → under **Firewalls** create one that allows
only TCP 22 inbound → paste `cloud-init.yaml` into **Cloud config** → name
`field-scout` → Create.

**DigitalOcean:** Create Droplet → Ubuntu 24.04 (LTS) x64 → Basic, **4 GB/2 vCPU** (2 GB was too small: the CLI was OOM-killed, 2026-10-30) → add your SSH key → **Additional Options → Startup scripts (Free)** (called "Advanced options → Add initialization
scripts (user data)** → paste `cloud-init.yaml` → hostname `field-scout`.
Then Networking → Firewalls: allow only TCP 22 inbound, attach to the droplet.

Wait about 5 minutes for setup to finish.

## First login and the key

```bash
ssh scout@<server-ip>
cloud-init status --wait          # should end with "status: done"
sudo systemctl status openclaw    # should be "active (exited)"
sudo docker ps                    # one container named openclaw, "healthy"
scout-set-key                     # paste the OpenRouter key; input is hidden
```

If `/var/run/reboot-required` exists, run `sudo reboot` and log in again.

## Open the UI (SSH tunnel)

On your laptop, in a separate terminal, leave this running:

```bash
ssh -N -L 18789:127.0.0.1:18789 scout@<server-ip>
```

Open <http://127.0.0.1:18789/>. When asked for the token, paste the value
from `sudo cat /etc/openclaw/gateway.env` (the part after `=`). If the UI
says the device needs approval:

```bash
scout-oc devices list
scout-oc devices approve <requestId>
```

Pick a concrete model instead of `openrouter/auto` in the UI, or
ask the Chair to change `agents.defaults.model.primary` (see "Changing the
config" below).

## First real task

In the UI chat, give it a small job, for example:

> Fetch https://openrouter.ai/announcements and https://github.com/openclaw/openclaw/releases.
> Write a short Markdown note of anything released in the last 7 days to
> `scout-inbox/2026-10-30-ai-releases.md`. Facts and links only.

The scout has `web_fetch` (fetch a given URL) but no search engine. Give it
fixed source URLs. Web search needs a plugin, which the install policy
blocks; adding one is a later, reviewed step.

## Pull findings into the council (Chair side)

On the council host, from the repo root:

```bash
rsync -rt --no-links --include='*.md' --exclude='*' --max-size=200k \
  -e "ssh -i ~/.ssh/scout_courier" \
  courier@<server-ip>: council/scout-inbox/
```

The courier key can only read that one folder. Everything it brings in is
**untrusted data**: the Research Analyst verifies each file before any seat
uses it (CLAUDE.md, trust rules).

## Run the smoke test

Work through `smoke-test.md` before the first real use. All checks must pass.

## Stop, update, destroy

- **Pause the agent:** `sudo systemctl stop openclaw` (start: `start`).
- **Kill switch from anywhere:** power the server off in the provider console.
- **Update OpenClaw:** read the release notes and advisories first. Then change
  the image tag in `/opt/openclaw/compose.yaml` and run
  `sudo docker compose -f /opt/openclaw/compose.yaml up -d`. Monthly patch
  check minimum (ROLE.md).
- **Rotate the key:** revoke it at OpenRouter, run `scout-set-key` with a new one.
- **Destroy:** revoke the OpenRouter key first, then delete the server in
  the provider console. Remove the courier key from the council host
  (`rm ~/.ssh/scout_courier*`). Nothing else holds credentials.

## Changing the config

`/srv/openclaw/state/openclaw.json` is root-owned and loaded read-only
(`OPENCLAW_CONFIG_READONLY=1`), so neither the agent nor the UI can change
it. To change it: `sudo nano /srv/openclaw/state/openclaw.json`, then
`scout-oc config validate` and `sudo systemctl restart openclaw`. To install
a reviewed plugin (for example a search provider), temporarily set
`security.installPolicy.enabled` to `false`, install with a pinned version,
set it back to `true`, and log the change in the decision log.

## Sources (checked 2026-10-28)

OpenClaw facts come from the official docs shipped inside the npm package
`openclaw@2026.10.8` (`docs/` folder, same text as docs.openclaw.ai) and the
official repo at tag `v2026.10.8`.

| Fact | Source |
|---|---|
| Latest stable 2026.10.8, published 2026-10-27 (`extended-stable` = 2026.9.35) | npm registry, `openclaw` dist-tags |
| Changelog for 2026.10.8 lists security hardening (exec allowlist, secret leaks, egress proxy) | `CHANGELOG.md` in the package |
| Official images `ghcr.io/openclaw/openclaw`, immutable version tags | docs `install/docker.md`, `install/docker/compose-operations.md` |
| Gateway port 18789; in Docker bind `lan` and keep the published port private; reach via `ssh -L` | docs `install/hetzner.md`, `install/docker-vm-runtime.md` |
| Official compose publishes ports on all interfaces (so this kit uses its own, 127.0.0.1 only) | repo `docker-compose.yml` at `v2026.10.8` |
| Config `~/.openclaw/openclaw.json`; `gateway.auth.mode` token; `${OPENCLAW_GATEWAY_TOKEN}` substitution; `gateway.terminal.enabled` | docs `gateway/config-gateway.md`, `gateway/config-secrets-env.md` |
| `tools.exec.mode: "deny"`; tool groups and profiles; `tools.fs.workspaceOnly` | docs `tools/exec.md`, `tools/permission-modes.md`, `gateway/config-tools/tool-policy.md`, `gateway/security/hardened-baseline.md` |
| `skills.allowBundled`, `agents.defaults.skills: []`, `skills.workshop.autonomous.mode: "off"`, `security.installPolicy` (fails closed, covers ClawHub) | docs `tools/skills-config.md`, `gateway/security/tool-permissions.md` |
| `plugins.deny` wins over allow | docs `tools/plugin.md` |
| `OPENCLAW_CONFIG_READONLY=1` = immutable config | docs `cli/config.md` |
| OpenRouter key via `OPENROUTER_API_KEY`; model refs `openrouter/<provider>/<model>` | docs `providers/openrouter.md` |
| Web search needs a provider plugin (Perplexity via OpenRouter, DuckDuckGo) not in the core package | docs `tools/web.md`, `tools/perplexity-search.md`; package manifest excludes `perplexity` |
| 2026 record: CVE-2026-25253 RCE and 40+ fixes in 2026.2.12; 22 CVEs in Apr 2026; GHSA-wppj-c6mr-83jj fixed 2026.4.22 | thearabianpost.com (2026-02-14), asec.ahnlab.com/en/93268 (2026-04-09), advisories.gitlab.com/pkg/npm/openclaw |

**Could not verify from here:** that the `2026.10.8` image tag exists on
GHCR (registry blocked from this sandbox; `docker ps` on first boot will
show it), that no advisory affects 2026.10.8 (GitHub's advisory list and
OSV were not reachable), the exact plugin ids in `plugins.deny` (taken from
the package's `dist/extensions/` folder names), and that the startup doctor
accepts read-only config. The smoke test checks each of these on the
real server.
