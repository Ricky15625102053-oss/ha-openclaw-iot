#!/usr/bin/env python3
"""Minimal natural-language-to-Home-Assistant control demo."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


DEVICE_MAP = {
    "演示灯": {
        "entity_id": "input_boolean.openclaw_demo_light",
        "domain": "input_boolean",
        "sensitive": False,
    },
    "demo light": {
        "entity_id": "input_boolean.openclaw_demo_light",
        "domain": "input_boolean",
        "sensitive": False,
    },
}

ACTION_MAP = {
    "打开": "turn_on",
    "开启": "turn_on",
    "开": "turn_on",
    "turn on": "turn_on",
    "关闭": "turn_off",
    "关掉": "turn_off",
    "关": "turn_off",
    "turn off": "turn_off",
}

BLOCKED_DOMAINS = {"lock", "alarm_control_panel"}


def parse_intent(text: str) -> tuple[str, dict[str, object], str]:
    normalized = text.strip().lower()

    action = ""
    for keyword, service in ACTION_MAP.items():
        if keyword in normalized:
            action = service
            break

    if not action:
        raise ValueError("无法识别动作。当前只支持打开或关闭。")

    device: dict[str, object] | None = None
    matched_name = ""
    for name, info in DEVICE_MAP.items():
        if name in normalized:
            device = info
            matched_name = name
            break

    if not device:
        raise ValueError("无法识别设备。当前只支持：演示灯。")

    return matched_name, device, action


def safety_check(device: dict[str, object], action: str) -> None:
    domain = str(device["domain"])
    if domain in BLOCKED_DOMAINS:
        raise ValueError(f"拒绝执行：{domain} 属于高风险 domain。")

    if device.get("sensitive") and action == "turn_off":
        raise ValueError("拒绝执行：敏感设备不允许直接关闭。")


def ha_request(base_url: str, token: str, path: str, payload: dict[str, str] | None = None):
    url = base_url.rstrip("/") + path
    data = None
    method = "GET"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        method = "POST"

    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Control a Home Assistant demo entity.")
    parser.add_argument("command", help='Natural language command, for example: "打开演示灯"')
    args = parser.parse_args()

    base_url = os.environ.get("HA_URL", "http://localhost:8123")
    token = os.environ.get("HA_TOKEN")
    if not token:
        print("Missing HA_TOKEN environment variable.", file=sys.stderr)
        return 2

    try:
        matched_name, device, action = parse_intent(args.command)
        safety_check(device, action)
        entity_id = str(device["entity_id"])
        domain = str(device["domain"])
        print(f"识别设备: {matched_name} -> {entity_id}")
        print(f"识别动作: {action}")
        print("安全检查: 通过")

        result = ha_request(
            base_url,
            token,
            f"/api/services/{domain}/{action}",
            {"entity_id": entity_id},
        )
        state = ha_request(base_url, token, f"/api/states/{entity_id}")
    except ValueError as exc:
        print(f"无法执行: {exc}", file=sys.stderr)
        return 1
    except urllib.error.HTTPError as exc:
        print(f"HA API HTTP error: {exc.code} {exc.reason}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Cannot reach HA API: {exc.reason}", file=sys.stderr)
        return 1

    print(f"HA 服务调用结果: {json.dumps(result, ensure_ascii=False)}")
    print(f"当前状态: {state.get('state')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
