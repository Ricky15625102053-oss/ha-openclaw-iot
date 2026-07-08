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

