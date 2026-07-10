# 演示场景

## 场景 1：出门上班

用户输入：

```text
我要出门上班了
```

预期流程：

1. OpenClaw 解析用户意图为“离家场景”。
2. OpenClaw 查询 Home Assistant 设备列表。
3. OpenClaw 调用 Home Assistant 服务。
4. Home Assistant 关闭全屋灯光和非必要电器。
5. Home Assistant 保持冰箱、安防、网关等必要设备运行。

## 安全规则

- 不允许关闭冰箱。
- 夜间不自动解锁门锁。
- 涉及门锁、燃气、电源总闸等高风险设备时，需要二次确认。

## 场景 2：本地文字输入模拟语音识别

目标：先不用麦克风，直接在本地命令行输入“语音识别完成后的文字”，模拟用户已经说完话且 ASR 已经转成文本。

示例输入：

```text
打开华为风扇
把华为空调调到 24 度
温度跳到20度
太热了
打开华为空调和风扇
关闭华为风扇
```

当前使用虚拟实体模拟华为设备：

| 设备 | 模拟实体 | 作用 |
| --- | --- | --- |
| 华为风扇 | `input_boolean.huawei_fan` | 模拟开关 |
| 华为空调 | `input_number.huawei_ac_temperature` | 模拟目标温度 |

运行方式：

```bash
cd /opt/ha-openclaw-iot
export HA_URL="http://localhost:8123"
export HA_TOKEN="paste-token-here"
python3 scripts/local-asr-text-demo.py
```

脚本会显示：

```text
ASR文本>
```

在这里输入文字命令即可。这个界面相当于“麦克风识别之后的文本结果入口”。
