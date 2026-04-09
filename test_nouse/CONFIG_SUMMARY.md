# 异常检测系统配置总结

## 🎯 服务器配置

### 基础信息
- **服务器地址**: `http://211.87.232.207:8001`
- **API 版本**: v1
- **模型类型**: vLLM + LoRA

### 模型信息
- **基座模型**: `/mnt/data2/zhangchong/models/Qwen3-8B`
- **LoRA 模型**: `trajad` (adapter 名称)
- **调用方式**: 直接使用 `model="trajad"`

### API 端点
1. **模型列表**: `GET /v1/models`
   - 返回两个模型：基座模型和 trajad adapter
   
2. **Chat Completions**: `POST /v1/chat/completions`
   - 推荐使用此接口
   - 支持 messages 格式
   
3. **Completions**: `POST /v1/completions`
   - 传统接口，也支持

## ⚙️ 本地配置

### 环境变量 (.env)
```ini
ANOMALY_API_PROVIDER=vllm
ANOMALY_VLLM_URL=http://211.87.232.207:8001/v1/completions
ANOMALY_MODEL=trajad
ANOMALY_THRESHOLD=0.7
ANOMALY_TEMPERATURE=0.1
ANOMALY_MAX_TOKENS=1024
ANOMALY_TIMEOUT=60
```

### 检测脚本配置
- **主脚本**: `scripts/detect_anomaly.py`
- **使用 Chat Completions 接口**
- **模型直接传递**: `model="trajad"`

## 🧪 测试方法

### 1. 基础连接测试
```bash
# 测试模型列表
curl http://211.87.232.207:8001/v1/models

# 运行完整测试
python test_trajad_vllm.py
```

### 2. 异常检测测试
```bash
# 使用测试数据
python scripts/detect_anomaly.py --input test_session.json

# 保存报告
python scripts/detect_anomaly.py --input test_session.json --output report.json
```

### 3. 一键测试 (Windows)
双击 `run_detection.bat`，选择选项 1

## 🔧 集成说明

### OpenClaw 集成
- **脚本**: `scripts/openclaw_integration.py`
- **状态**: 需要实现实际的 `sessions_history` API 调用
- **通知**: 支持钉钉/Telegram/WhatsApp 通知

### 定时任务
可配置 Cron 任务定期运行检测：
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

## 📊 输出格式

### 检测报告 JSON
```json
{
  "is_anomaly": true/false,
  "confidence": 0.85,
  "anomaly_type": "jailbreak|tool_abuse|data_exfil|prompt_injection|other",
  "risk_level": "low|medium|high|critical",
  "evidence": ["可疑行为描述"],
  "recommendation": "建议采取的行动",
  "summary": "简短总结",
  "timestamp": "2026-03-24T21:43:00",
  "model": "trajad",
  "messages_analyzed": 50
}
```

### 风险级别处理
- **low/none**: 记录日志，不通知
- **medium**: 生成报告，下次心跳通知
- **high**: 立即通知用户
- **critical**: 立即通知 + 建议暂停智能体

## 🚀 快速开始

### 第一步：验证连接
```bash
cd skills/agent-anomaly-detector
python test_trajad_vllm.py
```

### 第二步：运行检测
```bash
# 测试数据
python scripts/detect_anomaly.py --input test_session.json

# 或使用批处理
run_detection.bat
```

### 第三步：查看结果
检查生成的 `report.json` 文件

## 🔍 故障排除

### 常见问题
1. **连接失败**: 检查防火墙和网络连通性
2. **模型未找到**: 确认 `/v1/models` 返回 trajad
3. **JSON 解析失败**: 检查模型输出格式
4. **超时**: 增加 `ANOMALY_TIMEOUT` 值

### 调试命令
```bash
# 检查网络
ping 211.87.232.207
telnet 211.87.232.207 8001

# 测试 API
curl -v http://211.87.232.207:8001/v1/models
```

## 📈 性能优化

### 建议配置
- **温度**: 0.1 (低随机性，确保稳定输出)
- **最大令牌**: 1024 (足够返回完整 JSON)
- **超时**: 60秒 (考虑网络延迟)

### 监控指标
1. API 响应时间
2. 检测准确率
3. 误报率
4. 资源使用率

## 🔒 安全考虑

### 当前状态
- 使用公网 IP (211.87.232.207)
- 端口 8001 对外开放
- 无 API 密钥认证

### 建议改进
1. 使用内网或 VPN
2. 添加 API 密钥认证
3. 配置 IP 白名单
4. 启用 HTTPS

---

**配置完成时间**: 2026-03-24  
**最后测试**: 待运行 `test_trajad_vllm.py`  
**状态**: ✅ 配置就绪，等待测试