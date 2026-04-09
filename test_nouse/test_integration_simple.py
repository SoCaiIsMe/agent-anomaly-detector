#!/usr/bin/env python3
"""
简单测试 OpenClaw 集成
"""

import os
import sys
from pathlib import Path

# 设置环境变量
os.environ["ANOMALY_API_PROVIDER"] = "vllm"
os.environ["ANOMALY_VLLM_URL"] = "http://211.87.232.207:8001/v1/completions"
os.environ["ANOMALY_MODEL"] = "trajad"
os.environ["ANOMALY_THRESHOLD"] = "0.7"
os.environ["ANOMALY_TEMPERATURE"] = "0.1"
os.environ["ANOMALY_MAX_TOKENS"] = "1024"
os.environ["ANOMALY_TIMEOUT"] = "60"

print("环境变量已设置:")
print(f"ANOMALY_API_PROVIDER: {os.environ.get('ANOMALY_API_PROVIDER')}")
print(f"ANOMALY_VLLM_URL: {os.environ.get('ANOMALY_VLLM_URL')}")
print(f"ANOMALY_MODEL: {os.environ.get('ANOMALY_MODEL')}")

# 导入检测模块
sys.path.append(str(Path(__file__).parent / "scripts"))
from detect_anomaly import (
    OLLAMA_API_URL, VLLM_API_URL, MODEL_NAME, API_PROVIDER, DETECTION_THRESHOLD
)

print("\n检测模块配置:")
print(f"API_PROVIDER: {API_PROVIDER}")
print(f"MODEL_NAME: {MODEL_NAME}")
print(f"VLLM_API_URL: {VLLM_API_URL}")
print(f"OLLAMA_API_URL: {OLLAMA_API_URL}")

# 测试会话获取
from openclaw_integration_fixed import get_current_session_key, get_openclaw_session_history

print("\n测试会话获取:")
session_key = get_current_session_key()
if session_key:
    print(f"当前会话键: {session_key}")
    
    messages = get_openclaw_session_history(session_key, limit=3)
    print(f"获取到 {len(messages)} 条消息")
    
    if messages:
        print("最后3条消息:")
        for i, msg in enumerate(messages[-3:]):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:100]
            timestamp = msg.get('timestamp', '')[:19]
            print(f"  {i+1}. [{timestamp}] {role}: {content}...")
else:
    print("未找到当前会话")

print("\n测试完成")
print("\n要运行完整检测，请执行:")
print("python scripts/openclaw_integration_fixed.py")