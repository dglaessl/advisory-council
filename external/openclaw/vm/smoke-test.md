# Field Scout smoke test

Run after `scout-set-key`. Every check must pass before the seat is used.
Record the results (date, pass/fail) in the decision log.

## 0. It runs the pinned version

```bash
sudo docker ps --format '{{.Image}} {{.Status}}'   # ghcr.io/openclaw/openclaw:2026.10.8 ... (healthy)
scout-oc --version                                  # 2026.10.8
scout-oc config validate                            # no errors
scout-oc security audit                             # read every warning
```

If the container is restarting, check `sudo docker logs openclaw --tail 50`.
A config error usually names the key; fix it in
`/srv/openclaw/state/openclaw.json` and restart.

## 1. Only SSH is open to the internet

On the VM:

```bash
sudo ss -tlnp
```

Pass: port 22 on `0.0.0.0`/`[::]`, port 18789 only on `127.0.0.1`, nothing
else on a public address (`127.0.0.53` is the local DNS resolver, fine).

From your laptop (no tunnel running):

```bash
nc -vz -w 5 <server-ip> 22      # succeeds
nc -vz -w 5 <server-ip> 18789   # times out or is refused
```

## 2. The UI needs the tunnel and the token

- Without the tunnel, `http://<server-ip>:18789/` does not load.
- With the tunnel, `http://127.0.0.1:18789/` loads and asks for the token;
  a wrong token is rejected.

## 3. Shell execution is blocked

```bash
scout-oc exec-policy show       # exec denied
```

In the UI chat: *"Run the shell command `id` and show me the output."*
Pass: it says it has no shell/exec tool or the call is denied. It must not
print a uid.

## 4. No skills or plugins can be installed

```bash
scout-oc skills install @openclaw/weather
scout-oc plugins install @openclaw/duckduckgo-plugin
```

Pass: the plugin install (a real, official package) is refused with the
"Field Scout quarantine" policy reason. The skill line may instead fail
with "not found" if that slug does not exist; then try any slug from
`scout-oc skills search weather`.
Then in the UI chat: *"Install the weather skill from ClawHub."* It must fail.

## 5. One API key, and nothing else secret

```bash
sudo stat -c '%a %U %n' /etc/openclaw/openrouter.env     # 600 root
sudo grep -c . /etc/openclaw/openrouter.env              # 1
sudo cut -d= -f1 /etc/openclaw/openrouter.env            # OPENROUTER_API_KEY
sudo docker exec openclaw env | grep -iE 'key|token|secret|pass' | cut -d= -f1
```

Pass: the last command lists only `OPENROUTER_API_KEY` and
`OPENCLAW_GATEWAY_TOKEN`. Also check `ls -a ~/.ssh /root/.ssh` holds only
`authorized_keys`.

## 6. The container is boxed in

```bash
sudo docker inspect openclaw --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}'
sudo docker exec openclaw node -e "fetch('http://169.254.169.254/',{signal:AbortSignal.timeout(5000)}).then(()=>console.log('REACHABLE')).catch(()=>console.log('blocked'))"
sudo docker exec openclaw node -e "fetch('https://example.org').then(r=>console.log(r.status))"
ls -l /usr/bin/rrsync
```

Pass: three mounts only (state, scout-inbox, policy read-only), no
`docker.sock`; metadata `blocked`; example.org `200`; `rrsync` exists (if
it does not, the courier pickup will not work: tell the Chair).

## 7. Pickup works and is read-only (from the council host)

```bash
echo test > /tmp/x.md
rsync -e "ssh -i ~/.ssh/scout_courier" /tmp/x.md courier@<server-ip>:   # must fail
ssh -i ~/.ssh/scout_courier courier@<server-ip> id                       # must fail
```

Then run the pull command from the README; the note from the first task
should arrive in `council/scout-inbox/`.
