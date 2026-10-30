# Checkpoint: seat setup, Friday 2026-10-30 (morning session 05:02–06:33 CT)

## State
| Seat | Where | Status |
|---|---|---|
| Lead Engineer (OpenHands) | DigitalOcean droplet `field-engineer` (to be renamed `lead-engineer`), 64.23.254.254, SFO3, 4 GB/2 vCPU | Set up. Image `openhands-runner:1.16.0` built after a DNS fix; OpenHands CLI 1.16.0 runs; OpenRouter key and GitHub token stored (builder-only). **Pending:** reboot, smoke tests 1–4 and 6. |
| Field Scout (OpenClaw) | droplet `field-scout`, 137.184.124.63, SFO3, 2 GB/1 vCPU | **Parked**: `systemctl disable --now openclaw` (Daniel to confirm `docker ps` was empty). Passed: pinned image 2026.10.8, only 22 public / UI on 127.0.0.1, only the two expected env secrets. **Failed / unverified:** `scout-oc exec-policy show` exit 137 (OOM kill), plugin install refused with a generic error (not the quarantine reason). |
| Goose (Toolsmith) | Daniel's Mac | Not started |
| CrewAI (strategy panels) | Daniel's Mac (Docker) | Not started. Kit tests pass in the cloud (9 passed, 2 skipped). |
| Firewall | DigitalOcean `ssh-only` (inbound TCP 22) on both droplets | Active |
| Keys | OpenRouter: field-scout ($10), lead-engineer ($30), crewai ($15), goose ($15); GitHub fine-grained token (advisory-council only, 30 days) | Created by Daniel. One key was pasted into chat by mistake and was revoked and replaced. |

## Findings and kit fixes (committed)
- **DNS inside Docker failed** on DigitalOcean ("Temporary failure resolving deb.debian.org"), so the image build was the one failed cloud-init step. Fix: `"dns": ["1.1.1.1","8.8.8.8"]` in `/etc/docker/daemon.json`. Now in both kits.
- **Scout OOM:** the container's `mem_limit` is 3 GB on a 2 GB droplet with no swap, and `scout-oc` runs inside it. Kit now adds 2 GB swap and recommends a 4 GB droplet.
- DigitalOcean renamed "Advanced options → Add initialization scripts" to **"Additional Options → Startup scripts (Free)"**. READMEs updated.
- Hetzner rejected Daniel's US card. DigitalOcean was used instead.
- **Branch protection:** the OpenHands smoke test 5 pushes a test commit to `main` and expects rejection. Without a ruleset (private repos need GitHub Pro/Team) **it would land on main**. Skip test 5 until a ruleset exists; `oh-task` itself only pushes `council/<task_id>`.

## Tonight's runbook (Daniel at the keyboard, about 75 minutes)

### 1. Field Scout fix (on 137.184.124.63, as `scout`)
Fix the Scout in place, or resize it to 4 GB first (DigitalOcean → droplet → Resize → CPU and RAM only, about 1 minute of downtime).
```
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile && echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab
sudo python3 -c "import json;p='/etc/docker/daemon.json';d=json.load(open(p));d['dns']=['1.1.1.1','8.8.8.8'];json.dump(d,open(p,'w'),indent=2)"
sudo systemctl restart docker && sudo systemctl enable --now openclaw
free -m; sleep 20; sudo docker ps
scout-oc exec-policy show; echo "exit=$?"
scout-oc plugins install @openclaw/duckduckgo-plugin 2>&1 | tail -6
```
Pass: exec is denied, and the plugin install is refused with the "Field Scout quarantine" reason. Then UI via SSH tunnel and smoke tests 2–6. If anything still fails, disable again and leave it on probation.

### 2. Lead Engineer (on 64.23.254.254, as `builder`)
Reboot from the DigitalOcean dashboard (Power → off/on) or with `sudo reboot`. Then smoke tests 1–4 and 6 from `external/openhands/vm/smoke-test.md`, **skipping test 5**. Test 6 creates a draft PR that the Evaluator reviews.

### 3. CrewAI on the Mac
Put the key into an env file with hidden input, so it stays out of shell history:
```
mkdir -p ~/.config/council && bash -c 'read -rsp "CrewAI OpenRouter key: " K; echo; printf "OPENROUTER_API_KEY=%s\n" "$K" > ~/.config/council/crewai.env' && chmod 600 ~/.config/council/crewai.env
cd ~/council/repo-snapshot/external/crewai && ./run.sh venture examples/venture-envelope.json --dry-run --build
./run.sh venture examples/venture-envelope.json
```
Pass: the dry run writes reply.json, result.json and memo.md, and the real run returns `status` ok with `employment_conflict_check` filled.

### 4. Goose on the Mac
Follow `external/goose/README.md` sections 1–3: brew install, `goose configure` with the goose key, then **always launch through `goose-council.sh`**. Run `recipes/council-smoke.yaml`.

### 5. Red Team security pass
Agent Zero Red Team reviews the two cloud-init files, the four seats' smoke-test results, and the network exposure. The Auditor checks CLAUDE.md, SETUP.md and the kits for drift.

### 6. Chair afterwards
Update CLAUDE.md seat statuses, SETUP.md Phase 2, and a decision-log entry recording each seat as live, probation or pending. Refresh the snapshot.
