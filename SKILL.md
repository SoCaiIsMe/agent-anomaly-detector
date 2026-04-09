---
name: agent-anomaly-detector
description: 智能体异常轨迹检测。使用本地部署的大模型（Ollama/vLLM）分析智能体行为日志和会话历史，检测异常模式、越狱尝试、工具滥用等风险行为。触发条件：用户请求检测异常、查看智能体安全状态、或定时任务触发。
---

# 智能体异常轨迹检测

## 概述

本 Skill 提供智能体行为异常检测能力，通过分析会话历史、工具调用记录和行为模式，识别潜在的安全风险。

## 配置

在 `TOOLS.md` 中配置模型 API 端点：

```markdown
### 异常检测模型

**部署方式**: Ollama 或 vLLM 本地服务

**Ollama 配置**:
- API URL: http://localhost:11434/api/generate
- 模型名：qwen2.5:7b (或你的自定义模型)

**vLLM 配置**:
- API URL: http://localhost:8000/v1/completions
- 模型名：你的微调模型

**检测阈值**: 0.7 (置信度高于此值判定为异常)
```

## 工作流程

### 1. 数据收集

收集以下数据作为模型输入：
- 最近 N 条会话消息（默认 50 条）
- 工具调用记录（exec/browser/feishu 等）
- 时间戳和行为序列

### 2. 调用检测脚本

```bash
python scripts/detect_anomaly.py --session <session_key> --limit 50
```

### 3. 分析结果

模型返回 JSON 格式：
```json
{
  "is_anomaly": true/false,
  "confidence": 0.85,
  "anomaly_type": "tool_abuse|jailbreak|data_exfil|other",
  "risk_level": "low|medium|high|critical",
  "evidence": ["可疑行为描述 1", "可疑行为描述 2"],
  "recommendation": "建议采取的行动"
}
```

### 4. 响应处理

根据风险级别采取行动：
- **low**: 记录日志，无需通知
- **medium**: 生成报告，下次心跳时通知
- **high**: 立即通知用户
- **critical**: 立即通知 + 建议暂停智能体

## 脚本说明

### detect_anomaly.py

**功能**: 调用本地模型 API 进行异常检测

**参数**:
- `--session`: 会话 ID（可选，不传则分析当前会话）
- `--limit`: 分析最近 N 条消息（默认 50）
- `--output`: 输出文件路径（可选）

**使用示例**:
```bash
# 分析当前会话
python scripts/detect_anomaly.py

# 分析指定会话
python scripts/detect_anomaly.py --session abc123

# 输出到文件
python scripts/detect_anomaly.py --output report.json
```

## 定时任务配置

在 OpenClaw 中配置 Cron 任务（每 4 小时检测一次）：

```javascript
{
  "name": "agent-anomaly-check",
  "schedule": { "kind": "every", "everyMs": 14400000 },
  "payload": { 
    "kind": "systemEvent", 
    "text": "【安全检测】执行智能体异常轨迹检测" 
  },
  "sessionTarget": "main"
}
```

## 异常模式定义

详见 `references/anomaly_patterns.md`

## 报告模板

详见 `assets/report_template.md`

## 故障排除

### 模型 API 无法连接
1. 检查 Ollama/vLLM 服务是否运行
2. 验证 API URL 配置
3. 测试端点：`curl http://localhost:11434/api/tags`

### 检测准确率低
1. 调整检测阈值（TOOLS.md 中的 threshold）
2. 优化模型 prompt（scripts/detect_anomaly.py）
3. 考虑微调模型

## 安全注意事项

- 检测脚本不会修改原始会话数据
- 模型输入会脱敏处理（移除敏感信息）
- 检测报告仅发送给配置的目标用户
