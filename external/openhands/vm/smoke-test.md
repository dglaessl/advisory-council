# Lead Engineer smoke test

Run after `builder-set-keys`. All checks must pass before the seat takes
real work. Record the results in the decision log.

## 1. Only SSH is open

```bash
sudo ss -tlnp
```

Pass: port 22 on a public address; nothing else except `127.0.0.53`
(DNS) and, only if you started the UI, `127.0.0.1:8000`. From your laptop,
`nc -vz -w 5 <server-ip> 8000` must fail.

## 2. Keys: one per file, none inside the agent

```bash
sudo stat -c '%a %U %n' /etc/openhands/*.env    # openrouter/github: 600 builder
sudo cut -d= -f1 /etc/openhands/openrouter.env   # LLM_API_KEY (one line)
sudo cut -d= -f1 /etc/openhands/github.env       # GH_TOKEN (one line)
docker run --rm --env-file /etc/openhands/openrouter.env --env-file /etc/openhands/model.env \
  --entrypoint env openhands-runner:1.16.0 | cut -d= -f1 | grep -iE 'key|token|secret'
```

Pass: the last command prints only `LLM_API_KEY`, with no `GH_TOKEN`.

## 3. The container is boxed in

```bash
docker run --rm --entrypoint python openhands-runner:1.16.0 -c \
 "import urllib.request as u
try: u.urlopen('http://169.254.169.254/', timeout=5); print('REACHABLE')
except Exception: print('blocked')"
docker run --rm --entrypoint id openhands-runner:1.16.0     # uid=1000(agent)
```

Pass: `blocked`, and the agent is not root. While a task runs,
`docker inspect oh-<task_id> --format '{{range .Mounts}}{{.Source}}{{println}}{{end}}'`
lists only the work, out and state folders (no `docker.sock`).

## 4. The token is limited to one repo

```bash
export GH_TOKEN="$(sed -n 's/^GH_TOKEN=//p' /etc/openhands/github.env)"
gh api repos/<you>/advisory-council --jq .full_name                # works
gh api repos/<you>/<some-other-private-repo> --jq .full_name       # 404
gh api repos/<you>/advisory-council/actions/permissions            # 403 (no admin)
unset GH_TOKEN
```

## 5. `main` is protected (needs the ruleset)

```bash
export GH_TOKEN="$(sed -n 's/^GH_TOKEN=//p' /etc/openhands/github.env)"
cd /tmp && git -c credential.helper='!gh auth git-credential' clone https://github.com/<you>/advisory-council.git t && cd t
git -c user.name=test -c user.email=test@invalid commit --allow-empty -m "protection test"
git -c credential.helper='!gh auth git-credential' push origin HEAD:main   # must be rejected
cd /tmp && rm -rf t && unset GH_TOKEN
```

## 6. End to end: a tiny real task

```bash
cat > task.txt <<'EOF'
In bridge/tests/test_bridge.py add one unit test that checks a task id
containing "../" is rejected by the envelope validation in bridge/bridge.py.
Do not change bridge/bridge.py. Run: python3 -m unittest discover -s bridge/tests
All tests must pass.
EOF
oh-task <you>/advisory-council 2026-10-30-add-unit-test-01 task.txt
```

Pass:
- exit code 0, a diff touching only `bridge/tests/test_bridge.py`;
- answering `y` creates a **draft** PR from `council/2026-10-30-add-unit-test-01`
  into `main`, with test output in its description;
- `main` on GitHub is unchanged, and no PR was merged.

Then hand the PR to the Evaluator (CLAUDE.md: the Chair merges only after
Evaluator sign-off).
