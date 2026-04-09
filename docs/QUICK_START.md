# vLLM 异常检测快速启动指南

## 5分钟快速配置

### 1. 准备配置文件

```bash
# 进入技能目录
cd skills/agent-anomaly-detector

# 复制配置文件模板
copy .env.vllm .env
```

### 2. 编辑配置文件

用文本编辑器打开 `.env` 文件，修改以下配置：

```ini
# 设置 vLLM 为 API 提供商
ANOMALY_API_PROVIDER=vllm

# 设置你的 Ubuntu 服务器 IP 地址
ANOMALY_VLLM_URL=http://192.168.1.100:8000/v1/completions

# 模型名称（与 vLLM 服务器上的模型一致）
ANOMALY_MODEL=qwen2.5:7b

# 检测阈值
ANOMALY_THRESHOLD=0.7
```

### 3. 一键运行测试

双击 `run_detection.bat` 或运行：

```bash
# 测试连接
python test_vllm_api.py

# 或直接运行检测
python scripts/detect_anomaly.py --input test_session.json
```

## Ubuntu 服务器 vLLM 配置

### 启动 vLLM 服务

在 Ubuntu 服务器上：

```bash
# 1. 安装 vLLM（如果尚未安装）
pip install vllm

# 2. 下载模型（如果需要）
# 确保有足够的磁盘空间

# 3. 启动 vLLM 服务（允许远程访问）
vllm serve qwen2.5:7b \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.9

# 或使用 nohup 后台运行
nohup vllm serve qwen2.5:7b --host 0.0.0.0 --port 8000 > vllm.log 2>&1 &
```

### 验证服务运行

```bash
# 在服务器上检查
curl http://localhost:8000/v1/models

# 在 Windows 上测试
curl http://<服务器IP>:8000/v1/models
```

## 常见问题

### 1. 连接失败

```bash
# 检查网络连通性
ping <服务器IP>

# 检查端口
telnet <服务器IP> 8000

# 检查防火墙
# Ubuntu: sudo ufw allow 8000/tcp
```

### 2. 模型未找到

```bash
# 检查 vLLM 支持的模型
vllm serve --help

# 尝试其他模型
ANOMALY_MODEL=Qwen/Qwen2.5-7B-Instruct
```

### 3. 响应超时

```bash
# 增加超时时间
# 在 .env 中添加：
ANOMALY_TIMEOUT=120
```

## 进阶使用

### 1. 定时检测

创建 Windows 计划任务运行检测脚本。

### 2. 集成 OpenClaw

修改 `openclaw_integration.py` 实现真正的 OpenClaw API 集成。

### 3. 自定义模型

在 vLLM 服务器上使用自定义微调模型。

## 性能优化

### 1. 批处理检测

```bash
# 同时检测多个会话
python scripts/batch_detect.py --sessions session1.json session2.json
```

### 2. 结果缓存

实现缓存机制避免重复分析。

### 3. 异步调用

使用异步请求提高并发性能。

## 监控日志

### 查看 vLLM 日志

```bash
# 在 Ubuntu 服务器上
tail -f vllm.log

# 或查看系统日志
journalctl -u vllm -f
```

### 查看检测日志

```bash
# 在 Windows 上
python scripts/detect_anomaly.py --input test.json 2>&1 | tee detection.log
```

## 安全建议

1. **使用内网 IP**：避免暴露到公网
2. **配置防火墙**：只允许特定 IP 访问
3. **定期更新**：保持 vLLM 和模型更新
4. **监控资源**：关注 GPU 内存使用

## 获取帮助

如有问题，检查：
1. `test_vllm_api.py` 的输出
2. vLLM 服务器日志
3. Windows 防火墙设置