#!/usr/bin/env python3
"""
测试 OpenClaw 集成功能
"""

import json
import sys
from pathlib import Path

# 添加脚本目录到路径
sys.path.append(str(Path(__file__).parent / "scripts"))

from openclaw_integration_fixed import (
    get_openclaw_session_history,
    get_current_session_key,
    parse_session_jsonl,
    extract_text_from_content
)

def test_session_parsing():
    """测试会话解析功能"""
    print("测试会话解析功能...")
    
    # 测试 extract_text_from_content
    print("\n1. 测试 extract_text_from_content:")
    
    # 测试文本内容
    text_content = [
        {"type": "text", "text": "你好，这是一个测试消息"}
    ]
    result = extract_text_from_content(text_content)
    print(f"   文本内容: {result}")
    assert result == "你好，这是一个测试消息"
    
    # 测试工具调用
    tool_content = [
        {"type": "toolCall", "id": "call_123", "name": "exec", "arguments": {"command": "ls"}}
    ]
    result = extract_text_from_content(tool_content)
    print(f"   工具调用: {result}")
    assert "[工具调用: exec]" in result
    
    # 测试混合内容
    mixed_content = [
        {"type": "text", "text": "我将执行命令"},
        {"type": "toolCall", "id": "call_456", "name": "exec", "arguments": {"command": "pwd"}},
        {"type": "toolResult", "toolCallId": "call_456", "content": [{"type": "text", "text": "/home/user"}]}
    ]
    result = extract_text_from_content(mixed_content)
    print(f"   混合内容: {result}")
    assert "我将执行命令" in result
    assert "[工具调用: exec]" in result
    assert "[工具结果:" in result
    
    print("   [通过] 内容提取测试通过")

def test_current_session():
    """测试获取当前会话"""
    print("\n2. 测试获取当前会话:")
    
    session_key = get_current_session_key()
    if session_key:
        print(f"   当前会话键: {session_key}")
        
        # 测试获取会话历史
        messages = get_openclaw_session_history(session_key, limit=5)
        print(f"   获取到 {len(messages)} 条消息")
        
        if messages:
            print(f"   最后一条消息:")
            last_msg = messages[-1]
            print(f"     角色: {last_msg.get('role')}")
            print(f"     内容: {last_msg.get('content', '')[:100]}...")
            print(f"     时间: {last_msg.get('timestamp', '')}")
    else:
        print("   未找到当前会话")
    
    print("   [完成] 当前会话测试完成")

def test_session_file_parsing():
    """测试会话文件解析"""
    print("\n3. 测试会话文件解析:")
    
    # 查找会话文件
    openclaw_dir = Path.home() / ".openclaw"
    sessions_file = openclaw_dir / "agents" / "main" / "sessions" / "sessions.json"
    
    if sessions_file.exists():
        print(f"   找到会话索引文件: {sessions_file}")
        
        try:
            with open(sessions_file, 'r', encoding='utf-8') as f:
                sessions_data = json.load(f)
            
            print(f"   共有 {len(sessions_data)} 个会话")
            
            # 显示前几个会话
            for i, (key, info) in enumerate(list(sessions_data.items())[:3]):
                print(f"   {i+1}. {key}")
                print(f"      最后更新: {info.get('updatedAt', 0)}")
                print(f"      会话文件: {info.get('sessionFile', '无')}")
                
        except Exception as e:
            print(f"   读取会话文件时出错: {e}")
    else:
        print(f"   会话文件不存在: {sessions_file}")
    
    print("   [完成] 会话文件解析测试完成")

def test_integration():
    """测试完整集成"""
    print("\n4. 测试完整集成流程:")
    
    # 导入并测试主要函数
    from openclaw_integration_fixed import run_openclaw_detection
    
    print("   运行 OpenClaw 集成检测...")
    
    # 使用测试模式（不实际调用模型）
    print("   注意：这是测试模式，不会实际调用模型")
    print("   要实际运行检测，请使用: python scripts/openclaw_integration_fixed.py")
    
    # 测试获取会话历史
    session_key = get_current_session_key()
    if session_key:
        messages = get_openclaw_session_history(session_key, limit=3)
        print(f"   测试获取 {len(messages)} 条消息成功")
        
        if messages:
            print(f"   示例消息格式:")
            for i, msg in enumerate(messages[:2]):
                print(f"     {i+1}. {msg.get('role')}: {msg.get('content', '')[:50]}...")
    else:
        print("   无法获取当前会话，使用测试数据")
    
    print("   [完成] 集成测试完成")

def main():
    print("OpenClaw 集成功能测试")
    print("=" * 60)
    
    # 运行测试
    test_session_parsing()
    test_current_session()
    test_session_file_parsing()
    test_integration()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("\n下一步:")
    print("1. 运行完整检测: python scripts/openclaw_integration_fixed.py")
    print("2. 分析指定会话: python scripts/openclaw_integration_fixed.py --session agent:main:main")
    print("3. 保存报告: python scripts/openclaw_integration_fixed.py --output report.json")
    print("=" * 60)

if __name__ == "__main__":
    main()