#!/usr/bin/env python3
"""
运行最终的 OpenClaw 集成测试
"""

import os
import sys
from pathlib import Path

# 设置工作目录
script_dir = Path(__file__).parent
os.chdir(script_dir)

# 设置环境变量
os.environ["ANOMALY_API_PROVIDER"] = "vllm"
os.environ["ANOMALY_VLLM_URL"] = "http://211.87.232.207:8001/v1/completions"
os.environ["ANOMALY_MODEL"] = "trajad"
os.environ["ANOMALY_THRESHOLD"] = "0.7"
os.environ["ANOMALY_TEMPERATURE"] = "0.1"
os.environ["ANOMALY_MAX_TOKENS"] = "1024"
os.environ["ANOMALY_TIMEOUT"] = "60"

print("=" * 60)
print("OpenClaw 异常检测集成 - 最终测试")
print("=" * 60)

print("\n环境变量配置:")
print(f"  API 提供商: {os.environ.get('ANOMALY_API_PROVIDER')}")
print(f"  服务器地址: {os.environ.get('ANOMALY_VLLM_URL')}")
print(f"  模型名称: {os.environ.get('ANOMALY_MODEL')}")

# 导入并运行主函数
sys.path.append("scripts")

print("\n导入模块...")
try:
    from openclaw_integration_fixed import main
    
    print("开始运行异常检测...")
    print("-" * 40)
    
    # 模拟命令行参数
    sys.argv = ["openclaw_integration_fixed.py", "--limit", "10"]
    
    # 运行主函数
    main()
    
except Exception as e:
    print(f"运行出错: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)