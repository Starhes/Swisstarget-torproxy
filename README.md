# SwissTargetPrediction Tor Reverse Proxy

[![Build and Push Docker Image](https://github.com/Starhes/Swisstarget-torproxy/actions/workflows/docker-build.yml/badge.svg)](https://github.com/Starhes/Swisstarget-torproxy/actions/workflows/docker-build.yml)

使用 Tor 网络反向代理 [SwissTargetPrediction](https://swisstargetprediction.ch/)，自动规避网站速率限制。遇到 403/404/429 错误时自动切换 IP。

## Docker 镜像

```bash
docker pull ghcr.io/starhes/swisstarget-torproxy:latest
```

## 功能特性

- 🔄 通过 Tor 网络代理所有请求
- 🔀 遇到 403/404/429 错误自动切换 IP
- 📡 提供 API 端点手动管理 IP
- 🐳 Docker 一键部署

## 快速开始

### 使用 Docker Compose（推荐）

```bash
# 克隆或进入项目目录
cd Swisstarget-torproxy

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f proxy
```

服务启动后访问 http://localhost:5000/ 即可使用代理。

### 手动运行（需要本地 Tor）

1. **安装 Tor**
   
   Windows: 下载并安装 [Tor Expert Bundle](https://www.torproject.org/download/tor/)
   
   Linux:
   ```bash
   sudo apt install tor
   ```

2. **配置 Tor Control**
   
   编辑 `torrc` 文件，添加：
   ```
   ControlPort 9051
   HashedControlPassword YOUR_HASHED_PASSWORD
   ```
   
   生成密码哈希：
   ```bash
   tor --hash-password your_password
   ```

3. **安装 Python 依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   export TOR_CONTROL_PASSWORD=your_password
   ```

5. **启动代理服务**
   ```bash
   python proxy_server.py
   ```

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/health` | GET | 健康检查，验证 Tor 连接 |
| `/api/current-ip` | GET | 获取当前 Tor 出口 IP |
| `/api/switch-ip` | POST | 手动切换 IP |
| `/*` | ALL | 反向代理到 swisstargetprediction.ch |

### 示例

```bash
# 健康检查
curl http://localhost:5000/api/health

# 获取当前 IP
curl http://localhost:5000/api/current-ip

# 切换 IP
curl -X POST http://localhost:5000/api/switch-ip

# 访问代理站点首页
curl http://localhost:5000/
```

## 配置说明

通过环境变量配置：

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `TOR_SOCKS_HOST` | 127.0.0.1 | Tor SOCKS 代理地址 |
| `TOR_SOCKS_PORT` | 9050 | Tor SOCKS 代理端口 |
| `TOR_CONTROL_HOST` | 127.0.0.1 | Tor 控制端口地址 |
| `TOR_CONTROL_PORT` | 9051 | Tor 控制端口 |
| `TOR_CONTROL_PASSWORD` | - | Tor 控制密码 |
| `PROXY_HOST` | 0.0.0.0 | 代理服务监听地址 |
| `PROXY_PORT` | 5000 | 代理服务监听端口 |

## 自动 IP 切换

当请求目标网站返回以下状态码时，系统会自动切换 Tor 电路获取新 IP 并重试：

- **403** - Forbidden（被禁止访问）
- **404** - Not Found（可能是 IP 被封）
- **429** - Too Many Requests（速率限制）

每个请求最多重试 3 次（可在 `config.py` 中配置）。

## 项目结构

```
Swisstarget-torproxy/
├── config.py           # 配置文件
├── tor_client.py       # Tor 客户端封装
├── proxy_server.py     # Flask 反向代理服务
├── requirements.txt    # Python 依赖
├── Dockerfile          # Docker 镜像配置
├── docker-compose.yml  # Docker Compose 编排
└── README.md           # 说明文档
```

## 注意事项

- Tor 网络速度较慢，请耐心等待响应
- 频繁切换 IP 可能导致 Tor 网络不稳定
- 请遵守目标网站的使用条款
- 仅用于学术研究目的
