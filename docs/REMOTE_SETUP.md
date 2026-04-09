# 远程 Ollama API 配置指南

## 概述

本文档指导如何配置 agent-anomaly-detector 技能使用远程 Ollama 服务器。

## 架构

```
本地 OpenClaw → HTTP API → 远程 Ollama 服务器
     ↓                          ↓
检测脚本 ←─────── 模型响应 ←─── 模型推理
```

## 配置步骤

### 1. 远程服务器设置

在远程服务器上：

```bash
# 1. 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. 下载模型
ollama pull qwen2.5:7b

# 3. 启动服务（确保可远程访问）
ollama serve
# 或使用 systemd 服务
sudo systemctl enable ollama
sudo systemctl start ollama

# 4. 检查服务状态
curl http://localhost:11434/api/tags
```

### 2. 网络配置

确保远程服务器可访问：

```bash
# 测试连接（从本地机器）
ping <远程服务器IP>
telnet <远程服务器IP> 11434

# 如果需要，配置防火墙
# Ubuntu/Debian:
sudo ufw allow 11434/tcp
# CentOS/RHEL:
sudo firewall-cmd --add-port=11434/tcp --permanent
sudo firewall-cmd --reload
```

### 3. 本地配置

在本地 OpenClaw 环境中：

```bash
# 1. 复制环境配置文件
cd skills/agent-anomaly-detector
cp .env.example .env

# 2. 编辑 .env 文件
# 设置远程服务器 IP 地址
ANOMALY_OLLAMA_URL=http://192.168.1.100:11434/api/generate
```

### 4. 测试连接

```bash
# 运行连接测试
python test_remote_api.py

# 如果成功，应该看到：
# ✅ 连接成功！
# ✅ 模型响应正常
```

### 5. 运行异常检测

```bash
# 使用测试数据
python scripts/detect_anomaly.py --input test_session.json

# 输出示例 JSON 报告
python scripts/detect_anomaly.py --input test_session.json --output report.json
```

## 安全建议

### 1. 网络层安全

```bash
# 使用内网 IP
ANOMALY_OLLAMA_URL=http://10.0.0.100:11434/api/generate

# 或使用 VPN
ANOMALY_OLLAMA_URL=http://vpn-server:11434/api/generate
```

### 2. 认证保护（如果需要）

```bash
# 方法1：IP 白名单
# 在远程服务器配置防火墙，只允许特定 IP 访问

# 方法2：反向代理 + 认证
# 使用 nginx 添加 Basic Auth
location /api/ {
    proxy_pass http://localhost:11434;
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
}

# 然后在 .env 中添加：
ANOMALY_OLLAMA_URL=http://user:password@server:11434/api/generate
```

### 3. 传输加密

```bash
# 使用 HTTPS（需要配置 SSL 证书）
ANOMALY_OLLAMA_URL=https://server.example.com:11434/api/generate
```

## 故障排除

### 连接失败

```bash
# 1. 检查网络连通性
ping <服务器IP>

# 2. 检查端口是否开放
telnet <服务器IP> 11434

# 3. 检查防火墙
sudo ufw status

# 4. 检查 Ollama 服务
sudo systemctl status ollama
```

### 模型不可用

```bash
# 1. 检查模型是否已下载
ollama list

# 2. 重新下载模型
ollama pull qwen2.5:7b

# 3. 检查磁盘空间
df -h
```

### 响应超时

```bash
# 1. 增加超时时间
# 在 .env 中添加：
ANOMALY_TIMEOUT=120

# 2. 检查网络延迟
ping <服务器IP>
```

## 性能优化

### 1. 模型选择

```bash
# 轻量级模型（响应更快）
ollama pull qwen2.5:3b

# 在 .env 中配置：
ANOMALY_MODEL=qwen2.5:3b
```

### 2. 批处理

```bash
# 同时检测多个会话
python scripts/batch_detect.py --sessions session1.json session2.json
```

### 3. 缓存机制

考虑实现结果缓存，避免重复分析相同会话。

## 监控

### 1. 日志记录

```bash
# 查看 Ollama 日志
journalctl -u ollama -f

# 查看检测脚本日志
python scripts/detect_anomaly.py --input test.json 2>&1 | tee detection.log
```

### 2. 健康检查

```bash
# 定期检查 API 可用性
curl -f http://<服务器IP>:11434/api/tags || echo "API 不可用"
```

## 下一步

1. **集成 OpenClaw API**：完成 `openclaw_integration.py` 的实际实现
2. **定时任务**：配置 Cron 定期运行检测
3. **通知系统**：集成钉钉/Telegram 通知
4. **仪表板**：创建 Web 界面查看检测结果