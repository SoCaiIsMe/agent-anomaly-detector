# TOOLS.md 配置示例

将以下内容添加到你的 `TOOLS.md` 文件中：

```markdown
### 异常检测模型

**部署方式**: Ollama 本地服务

**配置**:
- API Provider: ollama
- API URL: http://localhost:11434/api/generate
- 模型名：qwen2.5:7b (或你的微调模型)
- 检测阈值：0.7

**环境变量** (可选，覆盖默认配置):
```bash
export ANOMALY_API_PROVIDER=ollama
export ANOMALY_OLLAMA_URL=http://localhost:11434/api/generate
export ANOMALY_MODEL=qwen2.5:7b
export ANOMALY_THRESHOLD=0.7
```

**vLLM 配置** (如使用 vLLM):
```bash
export ANOMALY_API_PROVIDER=vllm
export ANOMALY_VLLM_URL=http://localhost:8000/v1/completions
```

**测试连接**:
```bash
# Ollama
curl http://localhost:11434/api/tags

# vLLM
curl http://localhost:8000/v1/models
```
```

---

# 使用说明

## 1. 安装依赖

```bash
cd C:\Users\zhang\.openclaw\workspace\skills\agent-anomaly-detector\scripts
pip install requests
```

## 2. 启动模型服务

**Ollama**:
```bash
# 拉取模型
ollama pull qwen2.5:7b

# 启动服务（通常自动启动）
ollama serve
```

**vLLM**:
```bash
python -m vllm.entrypoints.api_server \
    --model your-model-path \
    --host 0.0.0.0 \
    --port 8000
```

## 3. 测试检测脚本

```bash
# 创建测试数据
echo '{"messages":[{"role":"user","content":"test","timestamp":"2026-03-17"}]}' > test_session.json

# 运行检测
python detect_anomaly.py --input test_session.json

# 查看报告
python detect_anomaly.py --input test_session.json --output report.json
```

## 4. 配置定时任务

在 OpenClaw 中运行以下命令添加 Cron 任务：

```javascript
// 每 4 小时检测一次
{
  "name": "agent-anomaly-check",
  "schedule": { "kind": "every", "everyMs": 14400000 },
  "payload": { 
    "kind": "systemEvent", 
    "text": "【安全检测】执行智能体异常轨迹检测，运行：python C:\\Users\\zhang\\.openclaw\\workspace\\skills\\agent-anomaly-detector\\scripts\\detect_anomaly.py"
  },
  "sessionTarget": "main"
}
```

## 5. 手动触发检测

在会话中直接说：
- "检测当前会话是否有异常"
- "运行异常轨迹检测"
- "检查智能体安全状态"

Skill 会自动触发检测流程。
