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
if HA_TOKEN is not None:
    HA_TOKEN = HA_TOKEN.strip()

STATE_ENTITIES = [
    "input_boolean.huawei_fan",
    "input_number.huawei_ac_temperature",
]


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


def contains_any(text: str, words: list[str]) -> bool:
    return any(word in text for word in words)


def plan_actions(text: str) -> list[dict[str, object]]:
    normalized = text.strip().lower().replace("　", " ")
    actions: list[dict[str, object]] = []
    temperature = parse_temperature(normalized)

    mentions_ac = (
        "空调" in normalized
        or "ac" in normalized
        or temperature is not None
        or contains_any(normalized, ["温度", "制冷", "太热", "有点热", "太冷"])
    )
    mentions_fan = "风扇" in normalized or "fan" in normalized or "吹风" in normalized

    if not mentions_ac and not mentions_fan:
        raise ValueError("没有识别到设备。当前 demo 支持：华为空调、华为风扇；也可以直接说温度。")

    if contains_any(normalized, ["关闭", "关掉", "关上", "停掉", "停止", "turn off"]):
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

    if contains_any(normalized, ["打开", "开启", "启动", "开一下", "turn on"]):
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
            temperature = temperature or 26
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

    if contains_any(normalized, ["太热", "有点热", "热了"]):
        actions.append(
            {
                "label": "根据偏热表达，将华为空调目标温度设为 24 度",
                "domain": "input_number",
                "service": "set_value",
                "entity_id": "input_number.huawei_ac_temperature",
                "payload": {
                    "entity_id": "input_number.huawei_ac_temperature",
                    "value": 24,
                },
            }
        )
        return actions

    if contains_any(normalized, ["太冷", "有点冷", "冷了"]):
        actions.append(
            {
                "label": "根据偏冷表达，将华为空调目标温度设为 26 度",
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

    raise ValueError("没有识别到动作。示例：打开华为风扇、把温度调到 24 度、太热了。")


def execute_action(action: dict[str, object]):
    domain = str(action["domain"])
    service = str(action["service"])
    payload = action["payload"]
    return ha_request(f"/api/services/{domain}/{service}", payload)  # type: ignore[arg-type]


def print_states() -> None:
    for entity_id in STATE_ENTITIES:
        try:
            state = ha_request(f"/api/states/{entity_id}")
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                print(f"- {entity_id}: 未找到，请先重新执行 scripts/install-demo-entities.sh")
                continue
            raise
        print(f"- {entity_id}: {state.get('state')}")


def read_asr_text() -> str:
    print("ASR文本> ", end="", flush=True)
    raw = sys.stdin.buffer.readline()
    if not raw:
        raise EOFError
    return raw.decode("utf-8", errors="replace").strip()


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
    print("示例：打开华为风扇 / 把华为空调调到 24 度 / 温度跳到20度 / 太热了")
    print("输入 exit 退出。\n")

    while True:
        try:
            text = read_asr_text()
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
