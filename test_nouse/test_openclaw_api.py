#!/usr/bin/env python3
"""
测试 OpenClaw API 连接和会话历史获取
"""

import json
import os
import subprocess
import sys
from pathlib import Path

def test_openclaw_cli():
    """测试 OpenClaw CLI 命令"""
    print("测试 OpenClaw CLI 命令...")
    
    # 1. 测试 sessions 命令
    print("\n1. 测试 sessions 命令:")
    try:
        result = subprocess.run(
            ["openclaw", "sessions", "--json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"  命令执行成功")
            print(f"  输出长度: {len(result.stdout)} 字符")
            
            # 尝试解析 JSON
            try:
                sessions = json.loads(result.stdout)
                print(f"  找到 {len(sessions)} 个会话")
                
                # 显示前几个会话
                for i, session in enumerate(sessions[:3]):
                    print(f"    {i+1}. {session.get('key', '未知')} - {session.get('label', '无标签')}")
                
                return sessions
            except json.JSONDecodeError as e:
                print(f"  JSON 解析失败: {e}")
                print(f"  原始输出前200字符: {result.stdout[:200]}")
        else:
            print(f"  命令执行失败: {result.stderr}")
            
    except Exception as e:
        print(f"  执行 sessions 命令时出错: {e}")
    
    return []

def test_gateway_api():
    """测试 Gateway API"""
    print("\n2. 测试 Gateway API:")
    
    gateway_url = "http://127.0.0.1:18789"
    
    # 尝试不同的 API 端点
    endpoints = [
        "/health",
        "/api/health",
        "/v1/health",
        "/status",
        "/api/status"
    ]
    
    for endpoint in endpoints:
        url = f"{gateway_url}{endpoint}"
        print(f"  测试 {url}...")
        
        try:
            # 使用 curl 或 requests
            import requests
            response = requests.get(url, timeout=5)
            print(f"    状态码: {response.status_code}")
            print(f"    内容类型: {response.headers.get('content-type', '未知')}")
            
            if response.status_code == 200:
                content = response.text[:100]
                print(f"    内容预览: {content}")
                
                # 检查是否是 JSON
                if 'application/json' in response.headers.get('content-type', ''):
                    data = response.json()
                    print(f"    JSON 数据: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
                    
        except ImportError:
            print(f"    requests 库未安装，跳过 HTTP 测试")
            break
        except Exception as e:
            print(f"    请求失败: {e}")

def explore_session_storage():
    """探索会话存储位置"""
    print("\n3. 探索会话存储:")
    
    # OpenClaw 可能存储会话的位置
    possible_paths = [
        Path.home() / ".openclaw" / "sessions.json",
        Path.home() / ".openclaw" / "sessions",
        Path.home() / ".openclaw" / "workspace" / "sessions",
        Path.home() / ".openclaw" / "agents" / "main" / "sessions",
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"  找到会话文件: {path}")
            
            if path.is_file():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read(500)
                        print(f"    文件内容预览: {content[:200]}...")
                except Exception as e:
                    print(f"    读取文件失败: {e}")
            elif path.is_dir():
                files = list(path.glob("*.json"))
                print(f"    目录中有 {len(files)} 个 JSON 文件")
                
                # 显示前几个文件
                for file in files[:3]:
                    print(f"      - {file.name}")
        else:
            print(f"  路径不存在: {path}")

def test_current_session():
    """测试获取当前会话"""
    print("\n4. 测试获取当前会话信息:")
    
    # 尝试通过环境变量获取当前会话
    env_vars = ["OPENCLAW_SESSION_KEY", "SESSION_KEY", "CURRENT_SESSION"]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"  环境变量 {var}: {value}")
    
    # 如果没有环境变量，尝试其他方法
    print("  当前会话获取方法需要进一步探索...")

def main():
    print("OpenClaw API 集成探索")
    print("=" * 60)
    
    # 测试 CLI 命令
    sessions = test_openclaw_cli()
    
    # 测试 Gateway API
    test_gateway_api()
    
    # 探索会话存储
    explore_session_storage()
    
    # 测试当前会话
    test_current_session()
    
    print("\n" + "=" * 60)
    print("探索完成")
    
    if sessions:
        print(f"\n建议：使用第一个会话进行测试:")
        if sessions:
            first_session = sessions[0]
            session_key = first_session.get('key')
            print(f"  会话键: {session_key}")
            print(f"  标签: {first_session.get('label', '无标签')}")
            print(f"  最后活动: {first_session.get('lastActivity', '未知')}")
    
    print("=" * 60)

if __name__ == "__main__":
    main()