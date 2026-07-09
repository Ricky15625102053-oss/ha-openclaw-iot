# HA + OpenClaw IoT Interop

基于 Home Assistant 与 OpenClaw 的第三方生态智能家居互联互通演示项目。

## 项目目标

- 使用 Home Assistant 统一接入多品牌、多协议智能家居设备。
- 使用 OpenClaw 解析自然语言指令并调用 Home Assistant REST API。
- 实现单设备控制、多设备场景联动和跨生态设备状态同步。

## 当前状态

当前已经完成 Home Assistant 服务器部署、首次初始化和 REST API Token 生成。

已验证：

- `homeassistant` 容器可运行。
- `8123` 端口可访问。
- Home Assistant `/api/states` 能返回实体 JSON。

## 目录结构

```text
ha-openclaw-iot/
  docs/
    architecture.md
    deployment.md
    device-integration.md
    demo-scenes.md
    home-assistant-installation-notes.md
    openclaw-ha-api.md
  home-assistant/
    compose.yaml
    config/
  scripts/
    bootstrap-home-assistant.sh
    check-ha-api.py
```

## 下一步

在阿里云服务器中使用 HA Token 验证 API：

```bash
export HA_URL="http://localhost:8123"
export HA_TOKEN="paste-token-here"
python3 scripts/check-ha-api.py
```

验证成功后，继续开发 OpenClaw 到 Home Assistant REST API 的最小控制链路。

注意：Home Assistant Token、服务器密码、OpenClaw API Key 等敏感信息不要提交到 GitHub。
