#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="${HA_OPENCLAW_ENV_FILE:-/root/.ha-openclaw.env}"

if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  set +a
fi

export HA_URL="${HA_URL:-http://localhost:8123}"

if [ -z "${HA_TOKEN:-}" ]; then
  echo "Missing HA_TOKEN. Create /root/.ha-openclaw.env or export HA_TOKEN before running." >&2
  exit 2
fi

exec /usr/bin/python3 "$PROJECT_DIR/scripts/local-asr-text-demo.py" "$@"
