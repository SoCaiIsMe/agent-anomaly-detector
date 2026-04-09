# Agent Anomaly Detector Skill

智能体异常轨迹检测 Skill - 使用本地大模型检测智能体行为异常

## 📁 目录结构

```
agent-anomaly-detector/
├── SKILL.md                    # Skill 主文档（OpenClaw 加载）
├── README.md                   # 项目主文档
├── scripts/
│   ├── detect_anomaly.py       # 主检测脚本
│   ├── openclaw_integration_fixed.py # OpenClaw集成脚本
│   └── openclaw_integration.py # 原始集成脚本
├── references/
│   └── anomaly_patterns.md     # 异常模式定义
├── assets/
│   └── report_template.md      # 报告模板
├── config/
│   ├── .env.example            # 环境变量配置示例
│   ├── .env.vllm               # vLLM配置示例
│   └── TOOLS_CONFIG.md         # TOOLS.md配置示例
├── docs/
│   ├── QUICK_START.md          # 快速开始指南
│   └── REMOTE_SETUP.md         # 远程服务器设置指南
├── tests/
│   ├── test_session.json       # 测试数据
│   ├── test_anomaly_detection.py # 完整测试脚本
│   └── simple_test.py          # 简单测试脚本
├── utils/
│   ├── run_detection.bat       # 主运行脚本
│   ├── run_openclaw_detection.bat # OpenClaw检测脚本
│   └── check_python.ps1        # Python检查脚本
└── test_nouse/                 # 不使用的测试文件（归档）
```

## 🚀 快速开始

### 步骤 1: 配置模型服务

**Ollama** (推荐):
```bash
# 安装 Ollama: https://ollama.ai
ollama pull qwen2.5:7b
ollama serve
```

**vLLM**:
```bash
pip install vllm
python -m vllm.entrypoints.api_server --model your-model --port 8000
```

### 步骤 2: 安装 Python 依赖

```bash
cd skills/agent-anomaly-detector/scripts
pip install requests
```

### 步骤 3: 配置 TOOLS.md

将 `TOOLS_CONFIG.md` 中的配置复制到你的 `TOOLS.md` 文件中。

### 步骤 4: 测试运行

```bash
python detect_anomaly.py --input ../test_session.json
```

### 步骤 5: 配置定时任务 (可选)

使用 OpenClaw cron 配置定时检测。

## 📖 使用方式

### 手动触发

在会话中说：
- "检测当前会话是否有异常"
- "运行异常轨迹检测"
- "检查智能体安全状态"

### 定时任务

配置 Cron 每 4 小时自动检测。

### API 调用

```bash
python detect_anomaly.py --session <session_key> --output report.json
```

## ⚙️ 配置选项

### 环境变量配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `ANOMALY_API_PROVIDER` | ollama | API 提供商 (ollama/vllm) |
| `ANOMALY_OLLAMA_URL` | http://localhost:11434/api/generate | Ollama API 地址 |
| `ANOMALY_VLLM_URL` | http://localhost:8000/v1/completions | vLLM API 地址 |
| `ANOMALY_MODEL` | qwen2.5:7b | 模型名称 |
| `ANOMALY_THRESHOLD` | 0.7 | 检测阈值 |
| `ANOMALY_TEMPERATURE` | 0.1 | 生成温度 |
| `ANOMALY_MAX_TOKENS` | 1024 | 最大token数 |
| `ANOMALY_TIMEOUT` | 60 | API超时时间(秒) |

### vLLM 服务器配置示例

```ini
# .env.vllm 配置示例
ANOMALY_API_PROVIDER=vllm
ANOMALY_VLLM_URL=http://192.168.1.100:8000/v1/completions
ANOMALY_MODEL=trajad
ANOMALY_THRESHOLD=0.7
ANOMALY_TEMPERATURE=0.1
ANOMALY_MAX_TOKENS=1024
ANOMALY_TIMEOUT=60
```

### 服务器端 vLLM 启动命令

```bash
# Ubuntu 服务器
vllm serve qwen2.5:7b \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.9

# 或使用 nohup 后台运行
nohup vllm serve qwen2.5:7b --host 0.0.0.0 --port 8000 > vllm.log 2>&1 &
```

## 📊 输出格式

### 检测报告 JSON 格式

```json
{
  "is_anomaly": true/false,
  "confidence": 0.0-1.0,
  "anomaly_type": "none|jailbreak|tool_abuse|data_exfil|prompt_injection|other",
  "risk_level": "none|low|medium|high|critical",
  "evidence": ["可疑行为描述 1", "可疑行为描述 2"],
  "recommendation": "建议采取的行动",
  "summary": "简短总结",
  "timestamp": "2026-03-24T21:43:00"
}
```

### 异常类型定义

1. **越狱尝试 (jailbreak)**: 用户试图绕过智能体安全限制
2. **工具滥用 (tool_abuse)**: 异常的工具调用模式，如频繁 exec、危险命令
3. **数据泄露 (data_exfil)**: 尝试获取或发送敏感信息
4. **提示注入 (prompt_injection)**: 试图注入恶意指令改变智能体行为
5. **其他异常 (other)**: 其他可疑但无法分类的行为

### 风险级别判定

| 级别 | 置信度 | 异常类型 | 响应动作 |
|------|--------|----------|----------|
| **none** | < 70% | 任何 | 仅记录日志 |
| **low** | 70-80% | other | 记录 + 标记会话 |
| **medium** | 70-85% | tool_abuse, prompt_injection | 生成报告，下次通知 |
| **high** | 80-90% | jailbreak, data_exfil | 立即通知用户 |
| **critical** | > 90% | jailbreak, data_exfil | 立即通知 + 建议暂停 |

## 🧪 测试方法

### 1. 基础连接测试

```bash
# 测试模型列表
curl http://192.168.1.100:8000/v1/models

# 运行完整测试
python test_anomaly_detection.py

# 运行简单测试
python simple_test.py
```

### 2. 异常检测测试

```bash
# 使用测试数据
python scripts/detect_anomaly.py --input test_session.json

# 保存报告
python scripts/detect_anomaly.py --input test_session.json --output report.json
```

### 3. 一键测试 (Windows)

双击 `run_detection.bat`，选择选项：
- 1: 测试 trajad 模型连接
- 2: 运行异常检测（测试数据）
- 3: 运行异常检测并保存报告

## 🔗 OpenClaw 集成

### 集成脚本

- `scripts/openclaw_integration_fixed.py` - 完整的 OpenClaw 集成
- `run_openclaw_detection.bat` - Windows 批处理文件

### 会话历史获取

脚本支持读取 OpenClaw 的会话文件：
- 会话索引: `C:\Users\zhang\.openclaw\agents\main\sessions\sessions.json`
- 会话文件: `C:\Users\zhang\.openclaw\agents\main\sessions\*.jsonl`

### 定时任务配置

在 OpenClaw 中配置 Cron 任务定期运行检测：

```javascript
{
  "name": "agent-anomaly-check",
  "schedule": { "kind": "every", "everyMs": 14400000 }, // 每4小时
  "payload": { 
    "kind": "systemEvent", 
    "text": "执行智能体异常轨迹检测" 
  },
  "sessionTarget": "main"
}
```

## 🔧 故障排除

### 1. 无法连接到模型 API

```bash
# 检查网络连通性
ping <服务器IP>

# 检查端口
telnet <服务器IP> 8000

# 检查防火墙
# Ubuntu: sudo ufw allow 8000/tcp

# 测试连接
curl http://<服务器IP>:8000/v1/models
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

### 4. 检测准确率低
- 调整阈值（ANOMALY_THRESHOLD）
- 优化 Prompt（detect_anomaly.py 中）
- 考虑微调模型
- 收集更多标注数据进行训练

### 5. 编码问题（Windows）
- 确保使用 UTF-8 编码保存文件
- 在批处理文件中添加 `chcp 65001`
- 使用 `check_python.ps1` 检查环境

## 📝 待办事项

- [ ] 集成 OpenClaw sessions_history API
- [ ] 添加飞书告警通知
- [ ] 支持批量会话分析
- [ ] 添加 Web UI 界面
