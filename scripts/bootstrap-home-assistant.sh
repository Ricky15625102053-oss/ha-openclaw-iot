#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/ha-openclaw-iot}"
HA_DIR="$PROJECT_DIR/home-assistant"
COMPOSE_FILE="$HA_DIR/compose.yaml"

echo "[1/7] Checking system"
if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root."
  exit 1
fi

if [ -f /etc/os-release ]; then
  . /etc/os-release
  echo "Detected system: ${PRETTY_NAME:-unknown}"
else
  echo "Cannot read /etc/os-release"
  exit 1
fi

echo "[2/7] Installing Docker prerequisites"
apt update
apt install -y ca-certificates curl gnupg

install_docker_from_ubuntu_repo() {
  echo "Trying Ubuntu repository Docker packages"
  apt install -y docker.io docker-compose-v2
}

install_docker_from_official_repo() {
  echo "Trying Docker official repository packages"
  install -m 0755 -d /etc/apt/keyrings
  if [ ! -f /etc/apt/keyrings/docker.asc ]; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  fi
  chmod a+r /etc/apt/keyrings/docker.asc

  CODENAME="${UBUNTU_CODENAME:-${VERSION_CODENAME:-}}"
  if [ -z "$CODENAME" ]; then
    echo "Cannot detect Ubuntu codename."
    return 1
  fi

  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $CODENAME stable" > /etc/apt/sources.list.d/docker.list
  apt update
  apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
}

echo "[4/7] Installing Docker Engine and Compose plugin"
if ! command -v docker >/dev/null 2>&1; then
  install_docker_from_ubuntu_repo || install_docker_from_official_repo
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose v2 is not available."
  echo "Please install docker-compose-v2 or docker-compose-plugin, then rerun this script."
  exit 1
fi

systemctl enable --now docker

echo "[5/7] Preparing Home Assistant directory"
mkdir -p "$HA_DIR/config"

if [ ! -f "$COMPOSE_FILE" ]; then
  cat > "$COMPOSE_FILE" <<'YAML'
services:
  homeassistant:
    container_name: homeassistant
    image: ghcr.io/home-assistant/home-assistant:stable
    restart: unless-stopped
    privileged: true
    network_mode: host
    environment:
      TZ: Asia/Shanghai
    volumes:
      - ./config:/config
      - /etc/localtime:/etc/localtime:ro
      - /run/dbus:/run/dbus:ro
YAML
fi

echo "[6/7] Starting Home Assistant"
cd "$HA_DIR"
docker compose up -d

echo "[7/7] Checking status"
docker ps --filter name=homeassistant
ss -tulpn | grep ':8123' || true

cat <<'EOF'

Home Assistant startup command completed.

Next checks:
1. Confirm Aliyun security group allows inbound TCP 8123.
2. Open http://123.57.64.73:8123 in the browser.
3. If the page is not ready yet, wait 2-5 minutes and check:
   docker logs --tail 100 homeassistant

EOF
