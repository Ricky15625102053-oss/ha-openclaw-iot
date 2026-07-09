#!/usr/bin/env python3
"""Check Home Assistant REST API connectivity without storing secrets."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def request_json(base_url: str, token: str, path: str):
    url = base_url.rstrip("/") + path
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        body = response.read().decode("utf-8")
        return json.loads(body)


def main() -> int:
    base_url = os.environ.get("HA_URL", "http://localhost:8123")
    token = os.environ.get("HA_TOKEN")

    if not token:
        print("Missing HA_TOKEN environment variable.", file=sys.stderr)
        print('Example: export HA_TOKEN="paste-token-here"', file=sys.stderr)
        return 2

    try:
        api_status = request_json(base_url, token, "/api/")
        states = request_json(base_url, token, "/api/states")
    except urllib.error.HTTPError as exc:
        print(f"HTTP error from Home Assistant: {exc.code} {exc.reason}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Cannot reach Home Assistant: {exc.reason}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Home Assistant returned non-JSON data: {exc}", file=sys.stderr)
        return 1

    print("Home Assistant API check passed.")
    print(f"API status: {api_status}")
    print(f"Entity count: {len(states)}")

    for entity in states[:10]:
        entity_id = entity.get("entity_id", "<unknown>")
        state = entity.get("state", "<unknown>")
        print(f"- {entity_id}: {state}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
