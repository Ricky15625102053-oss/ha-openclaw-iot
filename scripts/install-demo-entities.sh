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
TMP_CONFIG="$(mktemp)"
awk -v begin="$MARKER_BEGIN" -v end="$MARKER_END" '
  $0 == begin { skip = 1; next }
  $0 == end { skip = 0; next }
  skip != 1 { print }
' "$CONFIG_FILE" > "$TMP_CONFIG"
cat "$TMP_CONFIG" > "$CONFIG_FILE"
rm -f "$TMP_CONFIG"

cat >> "$CONFIG_FILE" <<'YAML'

# BEGIN ha-openclaw demo entities
input_boolean:
  openclaw_demo_light:
    name: OpenClaw Demo Light
    icon: mdi:lightbulb
  huawei_fan:
    name: Huawei Demo Fan
    icon: mdi:fan

input_number:
  huawei_ac_temperature:
    name: Huawei AC Target Temperature
    min: 16
    max: 30
    step: 1
    unit_of_measurement: "°C"
    icon: mdi:air-conditioner
# END ha-openclaw demo entities
YAML
echo "Demo entities block refreshed."

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
  input_boolean.huawei_fan
  input_number.huawei_ac_temperature

Next API checks:
  curl -sS -H "Authorization: Bearer $HA_TOKEN" \
    -H "Content-Type: application/json" \
    "$HA_URL/api/states/input_boolean.openclaw_demo_light"

EOF
