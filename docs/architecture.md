# 系统架构

```text
用户自然语言/语音
        ↓
OpenClaw
        ↓
Home Assistant REST API
        ↓
多品牌、多协议智能家居设备
```

## 分层说明

- Home Assistant：设备接入层，负责接入米家、Zigbee、MQTT、温控器等设备。
- OpenClaw：AI 决策层，负责理解用户自然语言并转换为 HA 服务调用。
- GitHub：版本控制平台，负责保存项目代码、部署文件和文档。

