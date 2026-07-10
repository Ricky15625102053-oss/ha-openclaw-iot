#!/usr/bin/env python3
"""Local text-input demo that simulates post-ASR smart-home commands."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request


HA_URL = os.environ.get("HA_URL", "http://localhost:8123").rstrip("/")
HA_TOKEN = os.environ.get("HA_TOKEN")


def ha_request(path: str, payload: dict[str, object] | None = None):
    data = None
    method = "GET"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        method = "POST"

    request = urllib.request.Request(
        HA_URL + path,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {HA_TOKEN}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else None


def parse_temperature(text: str) -> int | None:
    match = re.search(r"(\d{2})\s*度", text)
    if not match:
        match = re.search(r"(\d{2})\s*°?c", text.lower())
    if not match:
        return None

    value = int(match.group(1))
    if value < 16 or value > 30:
        raise ValueError("空调温度只允许设置在 16 到 30 度之间。")
    return value


def plan_actions(text: str) -> list[dict[str, object]]:
    normalized = text.strip().lower()
    actions: list[dict[str, object]] = []

    mentions_ac = "空调" in normalized or "ac" in normalized
    mentions_fan = "风扇" in normalized or "fan" in normalized

    if not mentions_ac and not mentions_fan:
        raise ValueError("没有识别到设备。当前 demo 支持：华为空调、华为风扇。")

    if any(word in normalized for word in ["关闭", "关掉", "关上", "turn off"]):
        if mentions_fan:
            actions.append(
                {
                    "label": "关闭华为风扇",
                    "domain": "input_boolean",
                    "service": "turn_off",
                    "entity_id": "input_boolean.huawei_fan",
                    "payload": {"entity_id": "input_boolean.huawei_fan"},
                }
            )
        if mentions_ac:
            actions.append(
                {
                    "label": "关闭华为空调模拟状态",
                    "domain": "input_number",
                    "service": "set_value",
                    "entity_id": "input_number.huawei_ac_temperature",
                    "payload": {
                        "entity_id": "input_number.huawei_ac_temperature",
                        "value": 26,
                    },
                }
            )
        return actions

    if any(word in normalized for word in ["打开", "开启", "启动", "turn on"]):
        if mentions_fan:
            actions.append(
                {
                    "label": "打开华为风扇",
                    "domain": "input_boolean",
                    "service": "turn_on",
                    "entity_id": "input_boolean.huawei_fan",
                    "payload": {"entity_id": "input_boolean.huawei_fan"},
                }
            )
        if mentions_ac:
            temperature = parse_temperature(normalized) or 26
            actions.append(
                {
                    "label": f"设置华为空调目标温度为 {temperature} 度",
                    "domain": "input_number",
                    "service": "set_value",
                    "entity_id": "input_number.huawei_ac_temperature",
                    "payload": {
                        "entity_id": "input_number.huawei_ac_temperature",
                        "value": temperature,
                    },
                }
            )
        return actions

    temperature = parse_temperature(normalized)
    if mentions_ac and temperature is not None:
        actions.append(
            {
                "label": f"设置华为空调目标温度为 {temperature} 度",
                "domain": "input_number",
                "service": "set_value",
                "entity_id": "input_number.huawei_ac_temperature",
                "payload": {
                    "entity_id": "input_number.huawei_ac_temperature",
                    "value": temperature,
                },
            }
        )
        return actions

    raise ValueError("没有识别到动作。示例：打开华为风扇、把华为空调调到 24 度。")


def execute_action(action: dict[str, object]):
    domain = str(action["domain"])
    service = str(action["service"])
    payload = action["payload"]
    return ha_request(f"/api/services/{domain}/{service}", payload)  # type: ignore[arg-type]


def print_states() -> None:
    for entity_id in [
        "input_boolean.huawei_fan",
        "input_number.huawei_ac_temperature",
    ]:
        state = ha_request(f"/api/states/{entity_id}")
        print(f"- {entity_id}: {state.get('state')}")


def handle_text(text: str) -> None:
    print(f"\n[模拟 ASR 输出] {text}")
    actions = plan_actions(text)
    print("[意图解析]")
    for action in actions:
        print(f"- {action['label']} -> {action['domain']}.{action['service']}")

    print("[安全检查] 通过：当前 demo 只控制虚拟华为空调/风扇实体。")
    print("[执行结果]")
    for action in actions:
        execute_action(action)
        print(f"- 已执行：{action['label']}")

    print("[当前 HA 状态]")
    print_states()


def main() -> int:
    if not HA_TOKEN:
        print("Missing HA_TOKEN environment variable.", file=sys.stderr)
        return 2

    if len(sys.argv) > 1:
        handle_text(" ".join(sys.argv[1:]))
        return 0

    print("本地文字输入 demo：模拟麦克风 ASR 识别完成后的文本。")
    print("示例：打开华为风扇 / 把华为空调调到 24 度 / 打开华为空调和风扇")
    print("输入 exit 退出。\n")

    while True:
        try:
            text = input("ASR文本> ").strip()
        except EOFError:
            print()
            return 0

        if text.lower() in {"exit", "quit", "q"}:
            return 0
        if not text:
            continue

        try:
            handle_text(text)
        except (ValueError, urllib.error.URLError, urllib.error.HTTPError) as exc:
            print(f"[无法执行] {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
