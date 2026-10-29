#!/usr/bin/env bash
# Launch a council goose recipe with approval required for every action.
#
#   ./goose-council.sh <recipe> [--params key=value ...]
#   ./goose-council.sh council-smoke
#   ./goose-council.sh council-healthcheck --params docker_context=council
#   ./goose-council.sh mcp-server-scaffold --params server_name=x --params purpose="..." --params tools_spec="..."
#
# What it enforces, every run:
#   - GOOSE_MODE=approve and an interactive terminal (goose asks before each shell/write/edit;
#     in approve mode goose refuses to run headless, so nothing runs unapproved)
#   - resets ~/.config/goose/permission.yaml to templates/permission.yaml (undoes any
#     earlier "Always Allow"; the old file is kept as a timestamped backup)
#   - installs templates/gooseignore as ~/.config/goose/.gooseignore if none exists
#   - --no-profile + only the Developer extension (no scheduler, subagents, extension
#     manager, apps or other extensions from your profile)
#   - runs in the work folder (default ~/council/goose-work) with a minimal environment
#     (your shell's API keys, cloud credentials and ssh agent are not passed through;
#     the ssh agent is passed only to council-healthcheck, for an ssh docker context)
#   - caps turns without your input (GOOSE_COUNCIL_MAX_TURNS, default 25)
set -euo pipefail

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="${GOOSE_WORK_DIR:-$HOME/council/goose-work}"
GOOSE_CFG="${XDG_CONFIG_HOME:-$HOME/.config}/goose"
MAX_TURNS="${GOOSE_COUNCIL_MAX_TURNS:-25}"
die() { echo "goose-council: $*" >&2; exit 1; }

[[ $# -ge 1 ]] || { sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }
NAME="${1%.yaml}"; shift
RECIPE="$KIT_DIR/recipes/$NAME.yaml"
[[ -f "$RECIPE" ]] || die "no recipe $RECIPE"
[[ -t 0 && -t 1 ]] || die "needs an interactive terminal (approve mode cannot run headless)"
GOOSE_BIN="$(command -v goose)" || die "goose not found on PATH (see README)"

for arg in "$@"; do  # the launcher owns work_dir
  case "$arg" in work_dir=*) die "work_dir is set by the launcher (GOOSE_WORK_DIR)";; esac
done

case "$WORK_DIR" in "$HOME"|"$HOME/"|/) die "refusing work folder '$WORK_DIR'";; esac
mkdir -p "$WORK_DIR"
WORK_DIR="$(cd "$WORK_DIR" && pwd)"

# Provider must be configured and must not be set to auto mode in config.
CFG="$GOOSE_CFG/config.yaml"
[[ -f "$CFG" ]] || die "no $CFG; run 'goose configure' first (see README)"
grep -Eq '^GOOSE_PROVIDER:' "$CFG" || die "GOOSE_PROVIDER missing in $CFG"
if grep -Eq '^GOOSE_MODE:' "$CFG" && ! grep -Eq '^GOOSE_MODE:[[:space:]]*"?approve"?[[:space:]]*$' "$CFG"; then
  die "GOOSE_MODE in $CFG is not 'approve'; set it to approve (see README)"
fi

# Reset tool permissions (undo any "Always Allow"), keeping a backup of a changed file.
mkdir -p "$GOOSE_CFG"
PERM="$GOOSE_CFG/permission.yaml"
if [[ -f "$PERM" ]] && ! cmp -s "$PERM" "$KIT_DIR/templates/permission.yaml"; then
  cp -p "$PERM" "$PERM.bak-$(date -u +%Y%m%dT%H%M%SZ)"
  echo "goose-council: permission.yaml had changed (backup kept); resetting to the council template" >&2
fi
cp "$KIT_DIR/templates/permission.yaml" "$PERM"

if [[ ! -f "$GOOSE_CFG/.gooseignore" ]]; then
  cp "$KIT_DIR/templates/gooseignore" "$GOOSE_CFG/.gooseignore"
  echo "goose-council: installed $GOOSE_CFG/.gooseignore" >&2
fi

ENV_KEEP=(HOME="$HOME" USER="${USER:-}" LOGNAME="${LOGNAME:-}" PATH="$PATH" TERM="${TERM:-xterm-256color}"
          LANG="${LANG:-en_US.UTF-8}" SHELL="${SHELL:-/bin/zsh}" TMPDIR="${TMPDIR:-/tmp}"
          GOOSE_MODE=approve GOOSE_TELEMETRY_ENABLED=false)
[[ -n "${XDG_CONFIG_HOME:-}" ]] && ENV_KEEP+=(XDG_CONFIG_HOME="$XDG_CONFIG_HOME")
if [[ "$NAME" == "council-healthcheck" && -n "${SSH_AUTH_SOCK:-}" ]]; then
  ENV_KEEP+=(SSH_AUTH_SOCK="$SSH_AUTH_SOCK")
fi

PARAMS=(--params "work_dir=$WORK_DIR")
[[ "$NAME" == "council-healthcheck" ]] && PARAMS=()   # this recipe takes no work_dir
while [[ $# -gt 0 ]]; do
  case "$1" in
    --params) PARAMS+=(--params "${2:?}"); shift 2 ;;
    *) die "unknown argument '$1' (use --params key=value)" ;;
  esac
done

cd "$WORK_DIR"
echo "goose-council: recipe=$NAME work=$WORK_DIR mode=approve max_turns=$MAX_TURNS" >&2
echo "goose-council: answer each prompt with Allow or Deny. Never choose 'Always Allow'." >&2
set +e
env -i "${ENV_KEEP[@]}" "$GOOSE_BIN" run --recipe "$RECIPE" "${PARAMS[@]}" \
  --no-profile --with-builtin developer --max-turns "$MAX_TURNS" --interactive \
  --name "council-$NAME-$(date -u +%Y%m%dT%H%M%SZ)"
rc=$?
set -e

if ! cmp -s "$PERM" "$KIT_DIR/templates/permission.yaml"; then
  echo "goose-council: WARNING: permissions changed during the run (an 'Always Allow'?):" >&2
  cat "$PERM" >&2
  cp "$KIT_DIR/templates/permission.yaml" "$PERM"
  echo "goose-council: reset to the council template" >&2
fi
exit $rc
