#!/usr/bin/env python3
"""
测试 vLLM API 连接
"""

import json
import requests

def test_connection():
    """测试连接"""
    print("测试 vLLM API 连接...")
    
    # 测试 /v1/models
    models_url = "http://211.87.232.207:8001/v1/models"
    print(f"1. 测试 {models_url}")
    
    try:
        response = requests.get(models_url, timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 连接成功！")
            
            models = data.get('data', [])
            print(f"   可用模型: {len(models)} 个")
            
            for model in models:
                model_id = model.get('id', 'unknown')
                print(f"     - {model_id}")
                
                if model_id == 'trajad':
                    print(f"       ✅ 找到 trajad 模型")
        else:
            print(f"   ❌ 错误: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return False
    
    # 测试 Completions
    print(f"\n2. 测试 Completions 接口")
    completions_url = "http://211.87.232.207:8001/v1/completions"
    
    payload = {
        "model": "trajad",
        "prompt": "Hello, are you working?",
        "max_tokens": 20,
        "temperature": 0.1,
        "stream": False
    }
    
    try:
        response = requests.post(completions_url, json=payload, timeout=30)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ API 调用成功！")
            
            choices = result.get('choices', [])
            if choices:
                text = choices[0].get('text', '')
                print(f"   模型回复: {text}")
        else:
            print(f"   ❌ 错误: {response.text}")
            
    except Exception as e:
        print(f"   ❌ API 调用失败: {e}")
        return False
    
    return True

def main():
    print("=" * 50)
    print("智能体异常检测系统 - 连接测试")
    print("=" * 50)
    
    success = test_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 所有测试通过！系统就绪。")
    else:
        print("❌ 测试失败，请检查配置。")
    
    print("=" * 50)

if __name__ == "__main__":
    main()