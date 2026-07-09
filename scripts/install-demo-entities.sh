#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/ha-openclaw-iot}"
HA_CONFIG_DIR="${HA_CONFIG_DIR:-$PROJECT_DIR/home-assistant/config}"
CONFIG_FILE="$HA_CONFIG_DIR/configuration.yaml"
BACKUP_FILE="$CONFIG_FILE.bak.$(date +%Y%m%d-%H%M%S)"
MARKER_BEGIN="# BEGIN ha-openclaw demo entities"
MARKER_END="# END ha-openclaw demo entities"

echo "[1/5] Checking Home Assistant config directory"
if [ ! -d "$HA_CONFIG_DIR" ]; then
  echo "Home Assistant config directory not found: $HA_CONFIG_DIR" >&2
  exit 1
fi

mkdir -p "$HA_CONFIG_DIR"
touch "$CONFIG_FILE"

echo "[2/5] Backing up configuration.yaml"
cp "$CONFIG_FILE" "$BACKUP_FILE"
echo "Backup created: $BACKUP_FILE"

echo "[3/5] Adding demo entities if missing"
if grep -Fq "$MARKER_BEGIN" "$CONFIG_FILE"; then
  echo "Demo entities block already exists. No duplicate block added."
else
  cat >> "$CONFIG_FILE" <<'YAML'

# BEGIN ha-openclaw demo entities
input_boolean:
  openclaw_demo_light:
    name: OpenClaw Demo Light
    icon: mdi:lightbulb
# END ha-openclaw demo entities
YAML
fi

echo "[4/5] Restarting Home Assistant container"
if docker ps --format '{{.Names}}' | grep -Fxq homeassistant; then
  docker restart homeassistant
else
  echo "homeassistant container is not running. Start it before checking entities." >&2
  exit 1
fi

echo "[5/5] Waiting for Home Assistant API"
for attempt in $(seq 1 60); do
  if curl -fsS "http://localhost:8123" >/dev/null 2>&1; then
    echo "Home Assistant is responding."
    break
  fi

  if [ "$attempt" -eq 60 ]; then
    echo "Home Assistant did not respond within 120 seconds. Check logs:" >&2
    echo "docker logs --tail 100 homeassistant" >&2
    exit 1
  fi

  sleep 2
done

cat <<'EOF'

Demo entity setup completed.

Expected entity:
  input_boolean.openclaw_demo_light

Next API checks:
  curl -sS -H "Authorization: Bearer $HA_TOKEN" \
    -H "Content-Type: application/json" \
    "$HA_URL/api/states/input_boolean.openclaw_demo_light"

EOF
