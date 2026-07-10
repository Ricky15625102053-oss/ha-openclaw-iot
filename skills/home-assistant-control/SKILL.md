---
name: home-assistant-control
description: Safely control the HA OpenClaw demo Home Assistant entities through the local project scripts.
metadata:
  openclaw:
    emoji: "🏠"
    requires:
      bins:
        - python3
        - curl
---

# Home Assistant Control

Use this skill when the user asks to control the HA OpenClaw demo smart-home devices.

This skill is intentionally limited to the project demo entities. Do not control locks, alarms, gas, high-power switches, door access, or other high-risk devices.

## Required Environment

The shell environment must provide:

```bash
HA_URL="http://localhost:8123"
HA_TOKEN="<Home Assistant long-lived access token>"
```

Never print, store, or commit `HA_TOKEN`.

## Safe Demo Entities

Only these entities are in scope:

```text
input_boolean.openclaw_demo_light
input_boolean.huawei_fan
input_number.huawei_ac_temperature
```

## Preferred Command

From the project root on the server:

```bash
cd /opt/ha-openclaw-iot
python3 scripts/local-asr-text-demo.py "<natural language command>"
```

Examples:

```bash
python3 scripts/local-asr-text-demo.py "打开华为风扇"
python3 scripts/local-asr-text-demo.py "关闭华为风扇"
python3 scripts/local-asr-text-demo.py "把华为空调调到24度"
python3 scripts/local-asr-text-demo.py "温度跳到20度"
python3 scripts/local-asr-text-demo.py "太热了"
```

## Before Executing

1. Confirm the command is about the demo Home Assistant devices.
2. Confirm `HA_TOKEN` is present in the current environment.
3. Refuse any command that targets sensitive or unknown devices.
4. If the demo entities are missing, ask the user to run:

```bash
cd /opt/ha-openclaw-iot
bash scripts/install-demo-entities.sh
```

## Status Checks

Use Home Assistant REST API checks when needed:

```bash
curl -sS -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  "$HA_URL/api/states/input_boolean.huawei_fan"
```

```bash
curl -sS -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  "$HA_URL/api/states/input_number.huawei_ac_temperature"
```

## Safety Refusals

Refuse or ask for a safer implementation if the user requests:

- unlocking doors
- disabling alarms
- controlling gas devices
- controlling unknown switches
- exposing Home Assistant or OpenClaw to the public internet
- storing tokens in GitHub, Obsidian, or project files
