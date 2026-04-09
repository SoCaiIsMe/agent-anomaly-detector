# 贡献指南

感谢您对 Agent Anomaly Detector 项目的关注！我们欢迎各种形式的贡献。

## 🚀 如何贡献

### 1. 报告问题
- 使用 GitHub Issues 报告 bug 或提出功能建议
- 在报告前，请先搜索是否已有类似问题
- 提供详细的问题描述、复现步骤和期望结果

### 2. 提交代码
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 3. 改进文档
- 修正错别字或语法错误
- 补充缺失的文档
- 翻译文档到其他语言
- 改进示例代码

## 📝 开发环境设置

### 1. 克隆仓库
```bash
git clone https://github.com/yourusername/agent-anomaly-detector.git
cd agent-anomaly-detector
```

### 2. 安装依赖
```bash
# 安装基础依赖
pip install -e .

# 安装开发依赖
pip install -e ".[dev]"
```

### 3. 配置环境
```bash
# 复制配置文件模板
cp config/.env.example .env

# 编辑 .env 文件，设置你的配置
```

## 🧪 运行测试

### 单元测试
```bash
pytest tests/
```

### 代码检查
```bash
# 代码格式化
black scripts/ tests/

# 代码检查
flake8 scripts/ tests/

# 类型检查
mypy scripts/
```

## 🎯 代码规范

### Python 代码风格
- 遵循 PEP 8 规范
- 使用 Black 进行代码格式化
- 使用类型注解
- 编写文档字符串

### 提交信息规范
使用 Conventional Commits 格式：
- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具变动

示例：
```
feat: 添加 vLLM 模型支持
fix: 修复编码问题
docs: 更新快速开始指南
```

### 分支命名规范
- `feature/` - 新功能开发
- `bugfix/` - bug 修复
- `hotfix/` - 紧急修复
- `docs/` - 文档更新
- `refactor/` - 代码重构

## 🔧 项目结构

```
agent-anomaly-detector/
├── scripts/           # 核心脚本
├── config/            # 配置文件模板
├── docs/              # 文档
├── references/        # 参考文档
├── assets/            # 资源文件
├── tests/             # 测试文件
├── utils/             # 实用工具
└── test_nouse/        # 归档的不必要文件
```

## 🐛 调试技巧

### 1. 启用调试日志
```bash
export ANOMALY_DEBUG=true
python scripts/detect_anomaly.py --input tests/test_session.json
```

### 2. 查看详细输出
```bash
python scripts/detect_anomaly.py --verbose --input tests/test_session.json
```

### 3. 测试特定功能
```bash
# 测试连接
python tests/test_connection.py

# 测试检测功能
python tests/test_anomaly_detection.py
```

## 📚 学习资源

### 相关技术
- [OpenClaw 文档](https://docs.openclaw.ai)
- [vLLM 文档](https://docs.vllm.ai)
- [Ollama 文档](https://ollama.ai)
- [Python requests 库](https://docs.python-requests.org)

### 安全相关
- [AI 安全最佳实践](https://github.com/openclaw/security-guidelines)
- [异常检测模式](references/anomaly_patterns.md)

## 🤝 行为准则

请遵守我们的行为准则：
- 尊重他人，保持友好
- 建设性讨论，避免人身攻击
- 帮助新人，分享知识
- 遵守开源协议

## 📄 许可证

本项目使用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢所有为项目做出贡献的人！您的每一份贡献都让项目变得更好。

---

如有问题，请通过 GitHub Issues 或 Discussions 联系我们。