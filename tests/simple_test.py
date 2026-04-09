#!/usr/bin/env python3
"""
简单的 vLLM API 测试脚本
"""

import json
import sys

# 尝试导入 requests
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("警告：requests 库未安装")

def test_with_requests():
    """使用 requests 库测试"""
    print("🔍 使用 requests 测试 vLLM API")
    
    # 配置
    vllm_url = "http://211.87.232.207:8001/v1/completions"
    model = "trajad"
    
    # 测试 Completions
    print(f"\n1. 测试 Completions 接口...")
    print(f"   URL: {vllm_url}")
    print(f"   模型: {model}")
    
    payload = {
        "model": model,
        "prompt": "Hello, are you working? Please respond in Chinese.",
        "max_tokens": 50,
        "temperature": 0.1,
        "stream": False
    }
    
    try:
        response = requests.post(vllm_url, json=payload, timeout=30)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 成功！")
            print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 提取回复
            choices = result.get('choices', [])
            if choices:
                text = choices[0].get('text', '')
                print(f"\n   🤖 模型回复: {text}")
            return True
        else:
            print(f"   ❌ 失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def test_without_requests():
    """没有 requests 库时的替代方案"""
    print("⚠️  requests 库未安装，无法进行 API 测试")
    print("\n替代方案：")
    print("1. 安装 requests: pip install requests")
    print("2. 使用 curl 命令测试:")
    print(f'   curl -X POST http://211.87.232.207:8001/v1/completions \\')
    print(f'     -H "Content-Type: application/json" \\')
    print(f'     -d \'{{"model": "trajad", "prompt": "Hello", "max_tokens": 50}}\'')
    return False

def main():
    print("=" * 60)
    print("[测试] trajad 模型简单测试")
    print("=" * 60)
    
    print(f"服务器: http://211.87.232.207:8001")
    print(f"模型: trajad")
    print("-" * 60)
    
    if HAS_REQUESTS:
        success = test_with_requests()
    else:
        success = test_without_requests()
    
    print("\n" + "=" * 60)
    if success:
        print("[成功] 测试成功！系统配置正确")
        print("\n下一步：运行异常检测")
        print("python scripts/detect_anomaly.py --input test_session.json")
    else:
        print("[警告] 测试失败或需要安装依赖")
    
    print("=" * 60)

if __name__ == "__main__":
    main()