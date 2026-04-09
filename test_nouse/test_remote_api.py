#!/usr/bin/env python3
"""
测试远程 Ollama API 连接
"""

import os
import sys
import json
from pathlib import Path

try:
    import requests
except ImportError:
    print("错误：需要安装 requests 库")
    print("运行：pip install requests")
    sys.exit(1)


def load_env_config():
    """从 .env 文件加载配置"""
    env_file = Path(__file__).parent / '.env'
    
    config = {
        'api_provider': 'ollama',
        'ollama_url': 'http://localhost:11434/api/generate',
        'model': 'qwen2.5:7b',
        'threshold': 0.7
    }
    
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'ANOMALY_API_PROVIDER':
                            config['api_provider'] = value
                        elif key == 'ANOMALY_OLLAMA_URL':
                            config['ollama_url'] = value
                        elif key == 'ANOMALY_MODEL':
                            config['model'] = value
                        elif key == 'ANOMALY_THRESHOLD':
                            try:
                                config['threshold'] = float(value)
                            except ValueError:
                                pass
    
    return config


def test_ollama_connection(api_url):
    """测试 Ollama API 连接"""
    print(f"测试连接: {api_url}")
    
    try:
        # 测试 /api/tags 端点
        tags_url = api_url.replace('/api/generate', '/api/tags')
        print(f"获取模型列表: {tags_url}")
        
        response = requests.get(tags_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        models = data.get('models', [])
        
        print("✅ 连接成功！")
        print(f"可用模型: {len(models)} 个")
        
        for model in models:
            print(f"  - {model.get('name', 'unknown')}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败：无法连接到 {api_url}")
        print("请检查：")
        print("1. 远程服务器是否运行 Ollama 服务")
        print("2. IP 地址和端口是否正确")
        print("3. 防火墙是否允许访问")
        return False
        
    except Exception as e:
        print(f"❌ 连接失败：{e}")
        return False


def test_model_availability(api_url, model_name):
    """测试模型是否可用"""
    print(f"\n测试模型: {model_name}")
    
    try:
        # 发送一个简单的测试请求
        payload = {
            "model": model_name,
            "prompt": "Hello, are you working?",
            "stream": False,
            "options": {
                "temperature": 0.1,
            }
        }
        
        response = requests.post(api_url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        response_text = result.get('response', '')
        
        print(f"✅ 模型响应正常")
        print(f"响应: {response_text[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ 模型测试失败：{e}")
        return False


def main():
    print("🔍 远程 Ollama API 连接测试")
    print("=" * 50)
    
    # 加载配置
    config = load_env_config()
    
    print(f"API 提供商: {config['api_provider']}")
    print(f"Ollama URL: {config['ollama_url']}")
    print(f"模型: {config['model']}")
    print(f"阈值: {config['threshold']}")
    print("-" * 50)
    
    if config['api_provider'] != 'ollama':
        print(f"⚠️  当前配置的 API 提供商是 {config['api_provider']}，不是 ollama")
        print("请修改 .env 文件中的 ANOMALY_API_PROVIDER=ollama")
        return
    
    # 测试连接
    if not test_ollama_connection(config['ollama_url']):
        return
    
    # 测试模型
    if not test_model_availability(config['ollama_url'], config['model']):
        return
    
    print("\n" + "=" * 50)
    print("✅ 所有测试通过！")
    print("\n下一步：")
    print("1. 运行异常检测测试：python scripts/detect_anomaly.py --input test_session.json")
    print("2. 配置 OpenClaw 集成")
    print("3. 设置定时检测任务")


if __name__ == "__main__":
    main()