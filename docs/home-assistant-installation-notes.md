# Home Assistant 安装说明

资料来源：

- https://www.home-assistant.io/installation/
- https://www.home-assistant.io/installation/linux
- https://www.home-assistant.io/installation/generic-x86-64
- https://developers.home-assistant.io/docs/api/rest/

## 1. 本项目选择的安装方式

Home Assistant 官方主要提供两类适合本项目理解的安装方式：

- Home Assistant Operating System：官方推荐给多数用户，适合专用硬件、虚拟机、树莓派、HA Green 等。
- Home Assistant Container：运行在已有 Linux + Docker 环境中，需要自己维护系统和更新。

本项目已有阿里云 Ubuntu 服务器，并且后续还要同时部署 OpenClaw、MQTT 等服务，所以采用 Home Assistant Container 更合适。

不建议当前下载 HA OS 镜像，因为 HA OS 会更适合“把整台机器变成 Home Assistant 专用主机”。阿里云服务器还需要承载课题项目的其他服务。

## 2. 已准备的项目资源

已在项目中准备 Docker Compose 文件：

```text
home-assistant/compose.yaml
```

配置目录：

```text
home-assistant/config
```

注意：`config` 目录中的运行数据、数据库、日志和 `secrets.yaml` 不应提交到 GitHub。

## 3. 服务器部署路径建议

在阿里云服务器上建议使用：

```text
/opt/ha-openclaw-iot
```

部署时进入：

```bash
cd /opt/ha-openclaw-iot/home-assistant
docker compose up -d
```

启动后访问：

```text
http://123.57.64.73:8123
```

如果打不开，优先检查：

1. Docker 容器是否运行。
2. 服务器是否监听 `8123` 端口。
3. 阿里云安全组是否放行 `8123`。
4. 浏览器访问地址是否是 `http://公网IP:8123`。

## 4. Home Assistant 和 OpenClaw 的连接点

Home Assistant 的 Web 页面和 REST API 默认都使用 `8123` 端口。

OpenClaw 后续需要调用：

```text
GET  /api/states
POST /api/services/{domain}/{service}
```

认证方式：

```text
Authorization: Bearer <Home Assistant Long-Lived Access Token>
```

长期访问令牌在 Home Assistant 页面登录后，从用户个人资料页生成。该令牌相当于控制 HA 的钥匙，不能写入 GitHub。

## 5. 当前部署限制

Home Assistant Container 没有 HA OS 的 Apps / Add-ons 能力，很多插件需要手动用 Docker 或 HACS 处理。

对本项目影响：

- 作为 HA + OpenClaw 原型验证，Container 足够。
- 如果后续需要 Zigbee2MQTT、MQTT Broker 等，可以再单独加 Docker 服务。
- 如果要用 HA OS 的插件生态，才需要考虑迁移到 HA OS 或专用硬件。

## 6. 小米和局域网设备提醒

如果 Home Assistant 部署在阿里云，而小米设备在家里局域网，默认不能直接发现和控制本地设备。

可选方案：

- 先用 MQTT 虚拟设备完成云端演示。
- 把 HA 部署在家庭局域网中。
- 用 Tailscale、ZeroTier、WireGuard 或 frp 打通云端和家庭网络。

