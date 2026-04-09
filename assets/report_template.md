# 🔍 智能体异常检测报告

**生成时间**: {{timestamp}}  
**检测模型**: {{model}}  
**分析消息数**: {{messages_analyzed}}

---

## 📊 检测摘要

| 项目 | 结果 |
|------|------|
| 是否异常 | {{is_anomaly}} |
| 风险级别 | **{{risk_level}}** |
| 置信度 | {{confidence}} |
| 异常类型 | {{anomaly_type}} |

---

## 📋 证据

{{#each evidence}}
- {{this}}
{{/each}}

---

## 💡 建议

{{recommendation}}

---

## 📝 详细分析

{{summary}}

---

## 🔧 后续操作

根据风险级别建议采取以下行动：

- **🟢 none/low**: 无需操作，继续监控
- **🟡 medium**: 审查会话历史，关注后续行为
- **🟠 high**: 与用户确认，必要时暂停智能体
- **🔴 critical**: 立即暂停智能体，进行全面审查

---

*此报告由 Agent Anomaly Detector Skill 自动生成*
