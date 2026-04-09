#!/usr/bin/env python3
"""
测试 trajad LoRA 模型的 vLLM API 连接
"""

import os
import sys
import json
import requests
from pathlib import Path

def load_config():
    """加载配置"""
    config = {
        'vllm_url': 'http://211.87.232.207:8001/v1/completions',
        'chat_url': 'http://211.87.232.207:8001/v1/chat/completions',
        'models_url': 'http://211.87.232.207:8001/v1/models',
        'model': 'trajad',
        'timeout': 30
    }
    return config

def test_models_endpoint(config):
    """测试 /v1/models 端点"""
    print("[测试] 测试 /v1/models 端点...")
    print(f"URL: {config['models_url']}")
    
    try:
        response = requests.get(config['models_url'], timeout=config['timeout'])
        response.raise_for_status()
        data = response.json()
        
        print("[成功] 连接成功！")
        print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        # 检查模型列表
        models = data.get('data', [])
        print(f"\n可用模型 ({len(models)} 个):")
        
        model_found = False
        for model in models:
            model_id = model.get('id', 'unknown')
            print(f"  - {model_id}")
            if model_id == config['model']:
                model_found = True
        
        if model_found:
            print(f"\n[成功] 找到目标模型: {config['model']}")
        else:
            print(f"\n[警告] 未找到模型: {config['model']}")
            print(f"可用模型: {[m.get('id') for m in models]}")
        
        return True
        
    except Exception as e:
        print(f"[错误] 测试失败: {e}")
        return False

def test_chat_completions(config):
    """测试 Chat Completions 接口"""
    print(f"\n[测试] 测试 Chat Completions 接口...")
    print(f"URL: {config['chat_url']}")
    print(f"模型: {config['model']}")
    
    payload = {
        "model": config['model'],
        "messages": [
            {
                "role": "system",
                "content": "你是一个智能体安全检测专家。请用中文回答。"
            },
            {
                "role": "user",
                "content": "你好，请简单介绍一下你自己。"
            }
        ],
        "max_tokens": 100,
        "temperature": 0.1,
        "stream": False
    }
    
    try:
        response = requests.post(config['chat_url'], json=payload, timeout=config['timeout'])
        response.raise_for_status()
        result = response.json()
        
        print("[成功] Chat Completions 测试成功！")
        print(f"响应格式: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # 提取回复内容
        choices = result.get('choices', [])
        if choices:
            message = choices[0].get('message', {})
            content = message.get('content', '')
            if content:
                print(f"\n[模型] 模型回复: {content}")
        
        return True
        
    except Exception as e:
        print(f"[错误] Chat Completions 测试失败: {e}")
        
        # 尝试旧的 completions 接口
        print("\n尝试 Completions 接口...")
        return test_completions(config)

def test_completions(config):
    """测试 Completions 接口"""
    print(f"\n[测试] 测试 Completions 接口...")
    print(f"URL: {config['vllm_url']}")
    
    payload = {
        "model": config['model'],
        "prompt": "你好，请简单介绍一下你自己。",
        "max_tokens": 100,
        "temperature": 0.1,
        "stream": False
    }
    
    try:
        response = requests.post(config['vllm_url'], json=payload, timeout=config['timeout'])
        response.raise_for_status()
        result = response.json()
        
        print("[成功] Completions 测试成功！")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        choices = result.get('choices', [])
        if choices:
            text = choices[0].get('text', '')
            if text:
                print(f"\n[模型] 模型回复: {text}")
        
        return True
        
    except Exception as e:
        print(f"[错误] Completions 测试失败: {e}")
        return False

def test_anomaly_detection(config):
    """测试异常检测功能"""
    print(f"\n[测试] 测试异常检测功能...")
    
    # 加载测试数据
    test_file = Path(__file__).parent / 'test_session.json'
    if not test_file.exists():
        print("❌ 测试数据文件不存在")
        return False
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        # 构建检测 prompt
        messages = test_data.get('messages', [])
        session_text = "\n\n".join([
            f"[{msg.get('timestamp', '')}] {msg.get('role', 'unknown')}: {msg.get('content', '')[:500]}"
            for msg in messages
        ])
        
        detection_prompt = f"""请分析以下智能体会话历史，检测是否存在异常行为：

{session_text}

请以严格的 JSON 格式返回分析结果：
```json
{{
  "is_anomaly": true/false,
  "confidence": 0.0-1.0,
  "anomaly_type": "none|jailbreak|tool_abuse|data_exfil|prompt_injection|other",
  "risk_level": "none|low|medium|high|critical",
  "evidence": ["证据 1", "证据 2", ...],
  "recommendation": "具体建议",
  "summary": "简短总结"
}}
```"""
        
        # 尝试 Chat Completions 接口
        payload = {
            "model": config['model'],
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个智能体安全检测专家。请分析智能体会话历史，检测是否存在异常行为，并以严格的 JSON 格式返回结果。"
                },
                {
                    "role": "user",
                    "content": detection_prompt
                }
            ],
            "max_tokens": 1024,
            "temperature": 0.1,
            "stream": False
        }
        
        response = requests.post(config['chat_url'], json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        choices = result.get('choices', [])
        if choices:
            message = choices[0].get('message', {})
            content = message.get('content', '')
            
            if content:
                print("[成功] 异常检测测试成功！")
                
                # 尝试解析 JSON
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
                
                try:
                    detection_result = json.loads(json_str)
                    print(f"检测结果: {json.dumps(detection_result, ensure_ascii=False, indent=2)}")
                    return True
                except json.JSONDecodeError:
                    print(f"[警告] 检测完成但 JSON 解析失败")
                    print(f"响应内容: {content[:200]}...")
                    return True
        
        print("[错误] 异常检测测试失败")
        return False
        
    except Exception as e:
        print(f"[错误] 异常检测测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("[测试] trajad LoRA 模型 vLLM API 测试")
    print("=" * 60)
    
    config = load_config()
    
    print(f"服务器: http://211.87.232.207:8001")
    print(f"模型: {config['model']} (Qwen3-8B + LoRA)")
    print("-" * 60)
    
    # 测试各个端点
    all_passed = True
    
    if not test_models_endpoint(config):
        all_passed = False
    
    if not test_chat_completions(config):
        all_passed = False
    
    if not test_anomaly_detection(config):
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[成功] 所有测试通过！系统配置正确")
        print("\n下一步：")
        print("1. 运行完整检测：python scripts/detect_anomaly.py --input test_session.json")
        print("2. 查看报告：python scripts/detect_anomaly.py --input test_session.json --output report.json")
        print("3. 配置 OpenClaw 集成")
    else:
        print("[警告] 部分测试失败，请检查配置")
    
    print("=" * 60)

if __name__ == "__main__":
    main()