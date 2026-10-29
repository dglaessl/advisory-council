#!/usr/bin/env bash
# Build a sanitized, read-only reference snapshot for an agent container.
#
# Allowlist-based: only the paths listed below (plus any extra paths you pass)
# are included, and only as committed in git HEAD. Mailboxes, ID reservations,
# replies, secrets and anything not allowlisted are excluded even if tracked.
#
# Usage: bridge/make_snapshot.sh <output.tar.gz> [extra/allowed/path ...]
# Then:  tar -xzf <output.tar.gz> -C ~/council/repo-snapshot --strip-components=1
set -euo pipefail

out="${1:?usage: make_snapshot.sh <output.tar.gz> [extra paths...]}"; shift || true
cd "$(git rev-parse --show-toplevel)"

allow=(
  CLAUDE.md README.md SETUP.md
  bridge
  external
  .claude/agents
  council/decision-log
  council/checkpoints/TEMPLATE.md
)
allow+=("$@")

# Hard denylist, checked AFTER archiving, regardless of the allowlist.
deny_re='(^|/)(\.env[^/]*|.*\.(key|pem))$|^advisory-council/council/(inbox|outbox|ids|scout-inbox)/'

existing=()
for p in "${allow[@]}"; do
  if git cat-file -e "HEAD:$p" 2>/dev/null; then existing+=("$p"); else echo "skip (not in HEAD): $p" >&2; fi
done

git archive --format=tar.gz --prefix=advisory-council/ -o "$out" HEAD -- "${existing[@]}"

members=$(tar -tzf "$out")
if echo "$members" | grep -E "$deny_re" >/dev/null; then
  echo "REFUSED: snapshot contains denied material:" >&2
  echo "$members" | grep -E "$deny_re" >&2
  rm -f "$out"
  exit 1
fi
echo "snapshot: $out ($(echo "$members" | grep -cv '/$') files)"
echo "$members" | grep -v '/$' | sed 's/^/  /'
