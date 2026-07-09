# OpenClaw 与 Home Assistant API 对接

更新时间：2026-07-09

## 当前状态

Home Assistant 已部署到阿里云服务器，并完成首次初始化。

已确认：

- HA 地址：`http://123.57.64.73:8123`
- 服务器本机地址：`http://localhost:8123`
- 管理员用户名：`ricky`
- Long-Lived Access Token：已生成，但不写入仓库。
- `/api/states` 已能返回实体 JSON。

## 为什么要验证 API

OpenClaw 后续不应该直接操作 Home Assistant 页面，而是通过 HA REST API 完成：

- 读取实体状态。
- 根据自然语言选择实体。
- 调用 HA 服务控制设备。
- 返回执行结果和失败原因。

因此在开发 OpenClaw Skill 前，必须先确认 HA API 地址和 Token 可用。

## 临时 API 测试

在服务器终端中执行。不要把 Token 写进命令历史以外的文件，也不要提交到 GitHub。

```bash
export HA_URL="http://localhost:8123"
export HA_TOKEN="paste-token-here"
```

测试 API 状态：

```bash
curl -sS -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  "$HA_URL/api/"
```

预期返回：

```json
{"message":"API running."}
```

测试实体列表：

```bash
curl -sS -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  "$HA_URL/api/states" | head -c 1000
```

预期返回 JSON 数组，包含 `entity_id`、`state`、`attributes` 等字段。

## 使用项目脚本验证

项目提供脚本：

```text
scripts/check-ha-api.py
```

执行：

```bash
cd /opt/ha-openclaw-iot
export HA_URL="http://localhost:8123"
export HA_TOKEN="paste-token-here"
python3 scripts/check-ha-api.py
```

脚本会检查：

1. `/api/` 是否返回 API 状态。
2. `/api/states` 是否能读取实体。
3. 当前实体数量。
4. 前 10 个实体 ID 和状态。

## Token 记录规则

不要把以下内容写入 GitHub：

- Home Assistant Long-Lived Access Token
- 管理员密码
- OpenClaw API Key
- `.env`
- `secrets.yaml`

后续如果需要让 OpenClaw 程序长期运行，应把 Token 放到服务器环境变量或未提交的本地配置文件中。

## 下一步

1. 选择一个可控实体或创建 MQTT 虚拟实体。
2. 编写最小 OpenClaw HA Skill：自然语言 -> 实体 ID -> HA 服务调用。
3. 增加安全规则，先禁止 `lock`、关键 `switch`、`alarm_control_panel` 等高风险 domain。

## 创建第一个演示实体

如果当前还没有真实智能设备，可以先创建一个 Home Assistant 虚拟开关：

```text
input_boolean.openclaw_demo_light
```

它的作用是模拟“灯”的开关状态，用来验证 OpenClaw 到 HA API 的完整控制链路。

服务器执行：

```bash
cd /opt/ha-openclaw-iot
curl -fsSL https://raw.githubusercontent.com/Ricky15625102053-oss/ha-openclaw-iot/main/scripts/install-demo-entities.sh -o scripts/install-demo-entities.sh
bash scripts/install-demo-entities.sh
```

脚本会做四件事：

1. 备份 `configuration.yaml`。
2. 追加 `input_boolean.openclaw_demo_light`。
3. 重启 Home Assistant 容器。
4. 等待 Home Assistant Web 页面恢复响应。

执行完成后，使用 Token 检查实体是否存在：

```bash
curl -sS -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  "$HA_URL/api/states/input_boolean.openclaw_demo_light"
```

测试打开虚拟灯：

```bash
curl -sS -X POST -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"input_boolean.openclaw_demo_light"}' \
  "$HA_URL/api/services/input_boolean/turn_on"
```

测试关闭虚拟灯：

```bash
curl -sS -X POST -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"input_boolean.openclaw_demo_light"}' \
  "$HA_URL/api/services/input_boolean/turn_off"
```
