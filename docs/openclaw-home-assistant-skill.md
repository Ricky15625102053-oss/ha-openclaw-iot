# OpenClaw Home Assistant Skill Setup

This document explains how to install the project-local Home Assistant control skill into OpenClaw.

## Current Goal

The project has already verified:

- Home Assistant runs on the server.
- Home Assistant REST API works.
- OpenClaw Gateway runs locally on `127.0.0.1:18789`.
- The project demo script can control Home Assistant demo entities.

The next goal is to make OpenClaw aware of the Home Assistant control workflow through a local skill.

## Why Use a Local Skill

OpenClaw skills are markdown instruction files stored in directories that contain `SKILL.md`. According to the OpenClaw skills documentation, OpenClaw loads workspace skills and managed local skills such as `~/.openclaw/skills`.

Using a local project skill is safer than installing an unknown third-party smart-home skill because:

- the allowed entities are explicit
- high-risk devices are refused
- secrets stay outside GitHub
- the skill calls the existing project script
- the workflow is easy to audit

## Install On Server

Run this on the server after pulling the latest repository version:

```bash
cd /opt/ha-openclaw-iot
git pull

mkdir -p ~/.openclaw/skills/home-assistant-control
cp skills/home-assistant-control/SKILL.md ~/.openclaw/skills/home-assistant-control/SKILL.md

openclaw skills list | grep -i home-assistant || true
openclaw gateway restart
openclaw gateway status
```

## Required Runtime Variables

Before asking OpenClaw to control Home Assistant, the runtime must have `HA_URL` and `HA_TOKEN`. For manual terminal tests you can export them:

```bash
export HA_URL="http://localhost:8123"
export HA_TOKEN="your-home-assistant-token"
```

Do not store the token in GitHub or this repository.

Use a single-line token value. Do not put the closing quote on a later line. If you want to avoid displaying the token in the terminal, use:

```bash
read -r -s -p "HA token: " HA_TOKEN
echo
export HA_TOKEN
```

If the token accidentally contains a newline, Python HTTP clients may fail with:

```text
ValueError: Invalid header value b'Bearer ...\n'
```

For OpenClaw Gateway execution, create a root-only local env file on the server. This file is not part of Git:

```bash
export HA_URL="http://localhost:8123"
unset HA_TOKEN
read -r -s -p "New HA token: " HA_TOKEN
echo
printf 'HA_URL=%q\nHA_TOKEN=%q\n' "$HA_URL" "$HA_TOKEN" > /root/.ha-openclaw.env
chmod 600 /root/.ha-openclaw.env
```

The project wrapper script reads that local file:

```bash
scripts/run-ha-demo-command.sh "turn on fan"
```

## Demo Test Commands

First confirm the project script still works:

```bash
cd /opt/ha-openclaw-iot
scripts/run-ha-demo-command.sh "turn on fan"
scripts/run-ha-demo-command.sh "set temperature to 20c"
scripts/run-ha-demo-command.sh "turn off fan"
```

Then start a new OpenClaw session and ask it to use the Home Assistant control skill for safe demo entities only.

## Safety Scope

Allowed demo entities:

```text
input_boolean.openclaw_demo_light
input_boolean.huawei_fan
input_number.huawei_ac_temperature
```

Forbidden targets:

- locks
- alarms
- gas devices
- unknown switches
- public internet exposure
- token storage
