#!/usr/bin/env bash
# Run one council CrewAI strategy panel in Docker. Analysis only.
#
#   ./run.sh <venture|hospitality|career> path/to/envelope.json [options]
#
# Options:
#   --dry-run          stub LLM, no API key, no network (--network none)
#   --out DIR          output folder (default: ~/council/crewai-out)
#   --input DIR        read-only input folder (default: the envelope's folder)
#   --build            (re)build the image first
#   --with-search      build/run with optional web search (needs SERPER_API_KEY in the env file)
#
# Environment (non-secret): CREW_MODEL (default openrouter/openai/gpt-6-luna),
#   CREW_TEMPERATURE, CREW_EMPLOYER_FIELD, CREW_ENV_FILE (default ~/.config/council/crewai.env)
#
# The container gets: the input folder read-only at /in, the output folder at /out,
# and OPENROUTER_API_KEY (real runs only). No other mounts, no docker.sock, no ports.
set -euo pipefail

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$KIT_DIR/../.." && pwd)"
IMAGE="council-crewai:1.15.33"
ENV_FILE="${CREW_ENV_FILE:-$HOME/.config/council/crewai.env}"

usage() { sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }
die() { echo "run.sh: $*" >&2; exit 1; }

[[ $# -ge 2 ]] || usage
CREW="$1"; ENVELOPE="$2"; shift 2
case "$CREW" in venture|hospitality|career) ;; *) die "unknown crew '$CREW'";; esac

DRY_RUN=0; BUILD=0; SEARCH=0; OUT_DIR="$HOME/council/crewai-out"; IN_DIR=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --build) BUILD=1 ;;
    --with-search) SEARCH=1 ;;
    --out) OUT_DIR="${2:?}"; shift ;;
    --input) IN_DIR="${2:?}"; shift ;;
    *) die "unknown option '$1'" ;;
  esac
  shift
done

[[ -f "$ENVELOPE" && ! -L "$ENVELOPE" ]] || die "envelope '$ENVELOPE' is not a regular file"
ENVELOPE_ABS="$(cd "$(dirname "$ENVELOPE")" && pwd)/$(basename "$ENVELOPE")"
IN_DIR="$(cd "${IN_DIR:-$(dirname "$ENVELOPE_ABS")}" && pwd)"
case "$ENVELOPE_ABS" in "$IN_DIR"/*) ;; *) die "envelope must be inside the input folder ($IN_DIR)";; esac
ENVELOPE_REL="${ENVELOPE_ABS#"$IN_DIR"/}"
case "$IN_DIR" in "$REPO_DIR"|"$HOME"|/) die "refusing to mount '$IN_DIR' as input; use a dedicated folder";; esac
mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"

# 1. Validate on the host with the repo's bridge.py (stdlib only).
python3 "$REPO_DIR/bridge/bridge.py" validate "$ENVELOPE_ABS" >/dev/null \
  || die "envelope failed bridge.py validation"

# 2. Build the image if needed.
if [[ $BUILD -eq 1 ]] || ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  docker build --build-context "bridge=$REPO_DIR/bridge" \
    --build-arg "WITH_SEARCH=$SEARCH" -t "$IMAGE" "$KIT_DIR"
fi

DOCKER_ARGS=(
  run --rm
  --read-only --tmpfs /tmp:rw,size=256m
  --cap-drop ALL --security-opt no-new-privileges
  --pids-limit 256 --memory 2g --cpus 2
  --user "$(id -u):$(id -g)"
  --mount "type=bind,source=$IN_DIR,target=/in,readonly"
  --mount "type=bind,source=$OUT_DIR,target=/out"
  -e "CREW_MODEL=${CREW_MODEL:-openrouter/openai/gpt-6-luna}"
  -e "CREW_TEMPERATURE=${CREW_TEMPERATURE:-0.3}"
)
[[ -n "${CREW_EMPLOYER_FIELD:-}" ]] && DOCKER_ARGS+=(-e "CREW_EMPLOYER_FIELD=$CREW_EMPLOYER_FIELD")

read_key() {  # read one KEY=value line from the env file, nothing else
  grep -E "^$1=" "$ENV_FILE" | tail -n1 | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//'
}

if [[ $DRY_RUN -eq 1 ]]; then
  DOCKER_ARGS+=(--network none)
  CREW_ARGS=(--dry-run)
else
  [[ -f "$ENV_FILE" ]] || die "env file $ENV_FILE not found (see README: chmod 600, outside the repo)"
  case "$(cd "$(dirname "$ENV_FILE")" && pwd)/" in "$REPO_DIR"/*) die "env file must live outside the repo";; esac
  PERMS="$(stat -c '%a' "$ENV_FILE" 2>/dev/null || stat -f '%Lp' "$ENV_FILE")"  # GNU, then macOS
  [[ "$PERMS" == "600" ]] || die "env file $ENV_FILE must be chmod 600 (is $PERMS)"
  OPENROUTER_API_KEY="$(read_key OPENROUTER_API_KEY)"
  [[ -n "$OPENROUTER_API_KEY" ]] || die "OPENROUTER_API_KEY missing in $ENV_FILE"
  export OPENROUTER_API_KEY   # passed by name, so the value never appears in `ps`
  DOCKER_ARGS+=(-e OPENROUTER_API_KEY)
  if [[ $SEARCH -eq 1 ]]; then
    SERPER_API_KEY="$(read_key SERPER_API_KEY)"
    [[ -n "$SERPER_API_KEY" ]] || die "--with-search needs SERPER_API_KEY in $ENV_FILE"
    export SERPER_API_KEY
    DOCKER_ARGS+=(-e SERPER_API_KEY -e CREW_ENABLE_SEARCH=1)
  fi
  CREW_ARGS=()
fi

exec docker "${DOCKER_ARGS[@]}" "$IMAGE" "$CREW" "/in/$ENVELOPE_REL" \
  --out /out --input-dir /in ${CREW_ARGS[@]+"${CREW_ARGS[@]}"}
