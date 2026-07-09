# 部署文档

更新时间：2026-07-09

## 服务器信息

- 云服务商：阿里云
- 公网 IP：123.57.64.73
- 规格：2 核 CPU / 2 GB 内存
- 系统：Ubuntu 26.04 LTS
- 登录用户：root

## Home Assistant 部署方式

本项目采用 Home Assistant Container，也就是用 Docker Compose 在已有 Ubuntu 服务器上运行 Home Assistant。

已准备文件：

```text
home-assistant/compose.yaml
scripts/bootstrap-home-assistant.sh
```

服务器执行位置建议：

```bash
cd /opt/ha-openclaw-iot/home-assistant
docker compose up -d
```

访问地址：

```text
http://123.57.64.73:8123
```

## 部署前必须确认

### 1. 阿里云安全组

进入阿里云控制台，确认入方向开放：

| 端口 | 用途 |
| --- | --- |
| 22 | 服务器远程登录 |
| 8123 | Home Assistant Web 页面 |

`80` 和 `443` 可以后续配置域名或 HTTPS 时再使用。

### 2. 服务器基础状态

登录服务器后先执行：

```bash
cat /etc/os-release
free -h
df -h
ss -tulpn
```

确认：

- 当前用户是 `root`。
- 磁盘空间充足。
- 内存约 2 GB，建议后续创建 2 GB swap。
- 当前还没有服务占用 `8123`。

## 一键部署脚本

项目提供脚本：

```text
scripts/bootstrap-home-assistant.sh
```

用途：

- 安装 Docker。
- 安装 Docker Compose 插件。
- 创建 `/opt/ha-openclaw-iot/home-assistant/config`。
- 复制或写入 Home Assistant Compose 文件。
- 启动 Home Assistant。
- 检查容器和端口状态。

在服务器项目根目录执行：

```bash
bash scripts/bootstrap-home-assistant.sh
```

如果还没有把项目放到服务器，可以手动创建目录：

```bash
mkdir -p /opt/ha-openclaw-iot
```

然后通过 Git、压缩包或 Workbench 文件上传，把本项目内容放进去。

## 手动部署步骤

如果不使用脚本，可以按下面步骤执行。

### 1. 安装 Docker

```bash
apt update
apt install -y docker.io docker-compose-v2
systemctl enable --now docker
docker --version
docker compose version
```

说明：Ubuntu 26.04 上优先使用系统软件源里的 Docker 和 Compose v2。这样比直接依赖 Docker 官方源更稳，因为官方源可能暂时没有同步新系统代号。

### 2. 启动 Home Assistant

```bash
cd /opt/ha-openclaw-iot/home-assistant
docker compose up -d
```

### 3. 检查运行状态

```bash
docker ps
ss -tulpn | grep 8123
docker logs --tail 100 homeassistant
```

看到 `homeassistant` 容器运行，并且 `8123` 端口监听后，浏览器访问：

```text
http://123.57.64.73:8123
```

## 部署后操作

首次打开 Home Assistant 后：

1. 创建管理员账号。
2. 设置位置、地区和时区。
3. 进入设置页面查看设备与服务。
4. 生成 Long-Lived Access Token。
5. 把 Token 保存在本机安全位置，不要写入 GitHub 或公开文档。

## 常见问题

### 页面打不开

按顺序检查：

1. `docker ps` 是否能看到 `homeassistant`。
2. `ss -tulpn | grep 8123` 是否有监听。
3. 阿里云安全组是否开放 `8123`。
4. 浏览器地址是否是 `http://123.57.64.73:8123`。

### Docker 镜像拉取慢或失败

可能是服务器到 GitHub Container Registry 网络不稳定。可以稍后重试：

```bash
docker compose pull
docker compose up -d
```

### 服务器内存不足

2 GB 内存可以跑原型，但建议创建 swap。后续可执行：

```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

## 后续待确认

- 安全组端口。
- OpenClaw 部署方式。
- 可用于演示的真实设备或 MQTT 虚拟设备。
