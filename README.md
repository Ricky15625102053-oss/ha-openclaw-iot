# HA + OpenClaw IoT Interop

基于 Home Assistant 与 OpenClaw 的第三方生态智能家居互联互通演示项目。

## 项目目标

- 使用 Home Assistant 统一接入多品牌、多协议智能家居设备。
- 使用 OpenClaw 解析自然语言指令并调用 Home Assistant REST API。
- 实现单设备控制、多设备场景联动和跨生态设备状态同步。

## 当前状态

当前已经准备好 Home Assistant 的 Docker Compose 部署文件和服务器启动脚本。

## 目录结构

```text
ha-openclaw-iot/
  docs/
    architecture.md
    deployment.md
    device-integration.md
    demo-scenes.md
    home-assistant-installation-notes.md
    operation-recording-rules.md
  home-assistant/
    compose.yaml
    config/
  scripts/
    bootstrap-home-assistant.sh
```

## 下一步

在阿里云服务器中确认安全组已开放 `8123` 后，登录服务器执行：

```bash
bash scripts/bootstrap-home-assistant.sh
```

部署成功后访问：

```text
http://123.57.64.73:8123
```

注意：Home Assistant Token、服务器密码、OpenClaw API Key 等敏感信息不要提交到 GitHub。

## 开发操作记录要求

本项目要求每次操作都记录到 Obsidian，并说明为什么做、目的是什么、具体怎么做、结果是什么。

详细规范见：

```text
docs/operation-recording-rules.md
```
