#!/usr/bin/env python3
"""
简单的 API 测试脚本（修复编码问题）
"""

import json
import sys
import requests

def test_models():
    """测试 /v1/models 端点"""
    print("测试 /v1/models 端点...")
    
    url = "http://211.87.232.207:8001/v1/models"
    
    try:
        response = requests.get(url, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("成功！返回数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            # 检查模型
            models = data.get('data', [])
            print(f"\n可用模型 ({len(models)} 个):")
            
            for model in models:
                model_id = model.get('id', 'unknown')
                print(f"  - {model_id}")
                
                if 'trajad' in model_id:
                    print(f"    ✅ 找到 trajad 模型")
        else:
            print(f"错误: {response.text}")
            
    except Exception as e:
        print(f"连接失败: {e}")

def test_completions():
    """测试 Completions 接口"""
    print("\n测试 Completions 接口...")
    
    url = "http://211.87.232.207:8001/v1/completions"
    model = "trajad"
    
    payload = {
        "model": model,
        "prompt": "Hello, are you working? Please respond in Chinese.",
        "max_tokens": 50,
        "temperature": 0.1,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("成功！响应:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 提取回复
            choices = result.get('choices', [])
            if choices:
                text = choices[0].get('text', '')
                print(f"\n模型回复: {text}")
        else:
            print(f"错误: {response.text}")
            
    except Exception as e:
        print(f"API 调用失败: {e}")

def main():
    print("vLLM API 测试")
    print("=" * 50)
    
    # 检查 requests 库
    try:
        import requests
    except ImportError:
        print("错误: requests 库未安装")
        print("请运行: pip install requests")
        return
    
    # 运行测试
    test_models()
    test_completions()
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()