#!/usr/bin/env python3
"""
OpenClaw 集成脚本 - 修复版
通过读取 OpenClaw 会话文件获取会话历史，然后进行异常检测
"""

import argparse
import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("错误：需要安装 requests 库")
    print("运行：pip install requests")
    sys.exit(1)

# 导入检测模块
sys.path.append(str(Path(__file__).parent))
from detect_anomaly import (
    format_session_history, detect_with_ollama, detect_with_vllm,
    parse_model_response, determine_risk_level, DETECTION_PROMPT,
    OLLAMA_API_URL, VLLM_API_URL, MODEL_NAME, API_PROVIDER, DETECTION_THRESHOLD
)


def get_openclaw_session_history(session_key=None, limit=50):
    """
    通过读取 OpenClaw 会话文件获取会话历史
    
    参数:
        session_key: 会话键，格式如 "agent:main:main"
        limit: 返回最近 N 条消息
    
    返回:
        消息列表，格式: [{"role": "user|assistant", "content": "消息内容", "timestamp": "时间戳"}]
    """
    
    # OpenClaw 会话存储路径
    openclaw_dir = Path.home() / ".openclaw"
    sessions_file = openclaw_dir / "agents" / "main" / "sessions" / "sessions.json"
    
    if not sessions_file.exists():
        print(f"错误：会话文件不存在: {sessions_file}")
        return []
    
    try:
        # 读取 sessions.json
        with open(sessions_file, 'r', encoding='utf-8') as f:
            sessions_data = json.load(f)
        
        # 如果没有指定 session_key，使用当前会话
        if not session_key:
            # 尝试找到当前会话（通常是最近更新的）
            current_session = None
            latest_time = 0
            
            for key, session_info in sessions_data.items():
                updated_at = session_info.get('updatedAt', 0)
                if updated_at > latest_time:
                    latest_time = updated_at
                    current_session = key
            
            if current_session:
                session_key = current_session
                print(f"使用当前会话: {session_key}")
            else:
                print("错误：未找到当前会话")
                return []
        
        # 获取会话信息
        session_info = sessions_data.get(session_key)
        if not session_info:
            print(f"错误：未找到会话 {session_key}")
            return []
        
        # 获取会话文件路径
        session_file_path = session_info.get('sessionFile')
        if not session_file_path:
            print(f"错误：会话 {session_key} 没有 sessionFile 字段")
            return []
        
        session_file = Path(session_file_path)
        if not session_file.exists():
            print(f"错误：会话文件不存在: {session_file}")
            return []
        
        print(f"读取会话文件: {session_file}")
        
        # 解析 JSONL 格式的会话文件
        messages = parse_session_jsonl(session_file, limit)
        
        print(f"成功读取 {len(messages)} 条消息")
        return messages
        
    except Exception as e:
        print(f"读取会话历史时出错: {e}")
        import traceback
        traceback.print_exc()
        return []


def parse_session_jsonl(session_file, limit=50):
    """
    解析 OpenClaw 的 JSONL 格式会话文件
    
    JSONL 格式示例:
    {"type":"message","id":"...","timestamp":"...","message":{"role":"user","content":[{"type":"text","text":"..."}]}}
    {"type":"message","id":"...","timestamp":"...","message":{"role":"assistant","content":[{"type":"text","text":"..."}]}}
    """
    messages = []
    
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 只处理最后 limit*2 行（因为每条消息可能有多行）
        recent_lines = lines[-(limit*2):] if len(lines) > limit*2 else lines
        
        for line in recent_lines:
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                
                # 只处理消息类型
                if data.get('type') == 'message':
                    message_data = data.get('message', {})
                    role = message_data.get('role')
                    
                    if role in ['user', 'assistant']:
                        # 提取内容
                        content_parts = message_data.get('content', [])
                        text_content = extract_text_from_content(content_parts)
                        
                        if text_content:
                            # 获取时间戳
                            timestamp = data.get('timestamp', '')
                            
                            messages.append({
                                'role': role,
                                'content': text_content,
                                'timestamp': timestamp
                            })
                            
            except json.JSONDecodeError:
                continue
        
        # 返回最近 limit 条消息
        return messages[-limit:] if len(messages) > limit else messages
        
    except Exception as e:
        print(f"解析会话文件时出错: {e}")
        return []


def extract_text_from_content(content_parts):
    """
    从 OpenClaw 消息内容中提取文本
    
    OpenClaw 消息格式:
    content: [
        {"type": "text", "text": "文本内容"},
        {"type": "toolCall", "id": "...", "name": "...", "arguments": {...}},
        {"type": "toolResult", "toolCallId": "...", "content": [...]}
    ]
    """
    if not content_parts:
        return ""
    
    text_parts = []
    
    for part in content_parts:
        part_type = part.get('type')
        
        if part_type == 'text':
            text = part.get('text', '')
            if text:
                text_parts.append(text)
        
        elif part_type == 'toolCall':
            # 工具调用，格式化为文本
            tool_name = part.get('name', 'unknown')
            text_parts.append(f"[工具调用: {tool_name}]")
        
        elif part_type == 'toolResult':
            # 工具结果，提取文本内容
            tool_content = part.get('content', [])
            if isinstance(tool_content, list):
                for content_item in tool_content:
                    if isinstance(content_item, dict) and content_item.get('type') == 'text':
                        text = content_item.get('text', '')
                        if text:
                            # 限制长度
                            text = text[:200] + "..." if len(text) > 200 else text
                            text_parts.append(f"[工具结果: {text}]")
            elif isinstance(tool_content, str):
                text = tool_content[:200] + "..." if len(tool_content) > 200 else tool_content
                text_parts.append(f"[工具结果: {text}]")
    
    return " ".join(text_parts)


def get_current_session_key():
    """
    获取当前会话的键
    
    通过环境变量或查找最近更新的会话
    """
    # 尝试从环境变量获取
    env_vars = ["OPENCLAW_SESSION_KEY", "SESSION_KEY", "CURRENT_SESSION"]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"从环境变量获取会话键: {var}={value}")
            return value
    
    # 如果没有环境变量，查找最近更新的会话
    openclaw_dir = Path.home() / ".openclaw"
    sessions_file = openclaw_dir / "agents" / "main" / "sessions" / "sessions.json"
    
    if not sessions_file.exists():
        return None
    
    try:
        with open(sessions_file, 'r', encoding='utf-8') as f:
            sessions_data = json.load(f)
        
        current_session = None
        latest_time = 0
        
        for key, session_info in sessions_data.items():
            updated_at = session_info.get('updatedAt', 0)
            if updated_at > latest_time:
                latest_time = updated_at
                current_session = key
        
        if current_session:
            print(f"找到最近更新的会话: {current_session}")
            return current_session
        
    except Exception as e:
        print(f"查找当前会话时出错: {e}")
    
    return None


def run_openclaw_detection(session_key=None, limit=50):
    """执行 OpenClaw 集成检测"""
    print("开始 OpenClaw 异常检测...")
    
    # 获取会话键
    if not session_key:
        session_key = get_current_session_key()
        if not session_key:
            print("错误：无法确定当前会话")
            return None
    
    print(f"会话: {session_key}")
    print(f"模型: {MODEL_NAME} ({API_PROVIDER})")
    print(f"限制: {limit} 条消息")
    print("-" * 50)
    
    # 获取会话历史
    messages = get_openclaw_session_history(session_key, limit)
    
    if not messages:
        print("警告：未获取到会话消息，使用测试数据")
        # 使用测试数据
        test_file = Path(__file__).parent / 'test_session.json'
        if test_file.exists():
            with open(test_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
            messages = test_data.get('messages', [])
        else:
            print("错误：测试数据文件也不存在")
            return None
    
    # 格式化历史
    session_text = format_session_history(messages, limit)
    
    # 构建检测 Prompt
    prompt = DETECTION_PROMPT.format(
        session_history=session_text,
        threshold=DETECTION_THRESHOLD
    )
    
    print(f"分析 {len(messages)} 条消息...")
    
    # 调用模型
    if API_PROVIDER == "vllm":
        response = detect_with_vllm(prompt)
    else:
        response = detect_with_ollama(prompt)
    
    if not response:
        print("检测失败：模型未响应")
        return None
    
    # 解析结果
    result = parse_model_response(response)
    
    if not result:
        print("解析模型响应失败")
        return None
    
    # 补充风险级别
    if "risk_level" not in result:
        result["risk_level"] = determine_risk_level(
            result.get("confidence", 0),
            result.get("anomaly_type", "none")
        )
    
    # 添加元数据
    result["timestamp"] = datetime.now().isoformat()
    result["model"] = MODEL_NAME
    result["messages_analyzed"] = len(messages)
    result["session_key"] = session_key
    
    return result


def print_report(result):
    """打印检测报告"""
    print("\n" + "=" * 60)
    print("[检测] OpenClaw 异常检测报告")
    print("=" * 60)
    
    is_anomaly = result.get("is_anomaly", False)
    risk_level = result.get("risk_level", "unknown")
    
    # 风险级别文本
    risk_text = {
        "none": "[正常]",
        "low": "[低风险]",
        "medium": "[中风险]",
        "high": "[高风险]",
        "critical": "[严重风险]"
    }
    
    print(f"\n{risk_text.get(risk_level, '[未知]')} 风险级别：{risk_level.upper()}")
    print(f"[置信度] 异常置信度：{result.get('confidence', 0):.2%}")
    print(f"[类型] 异常类型：{result.get('anomaly_type', 'none')}")
    
    if result.get("session_key"):
        print(f"[会话] 会话 ID：{result['session_key']}")
    
    if result.get("evidence"):
        print(f"\n[证据] 证据:")
        for i, ev in enumerate(result["evidence"], 1):
            print(f"   {i}. {ev}")
    
    if result.get("recommendation"):
        print(f"\n[建议] 建议：{result['recommendation']}")
    
    print(f"\n[摘要] 摘要：{result.get('summary', 'N/A')}")
    print(f"\n[时间] 检测时间：{result.get('timestamp', 'N/A')}")
    print(f"[数量] 分析消息数：{result.get('messages_analyzed', 0)}")
    print("=" * 60)


def send_notification(result, channel="dingtalk"):
    """
    发送检测结果通知
    
    支持的通知渠道：
    - dingtalk: 钉钉
    - telegram: Telegram
    - whatsapp: WhatsApp
    - email: 邮件
    """
    risk_level = result.get("risk_level", "unknown")
    
    # 根据风险级别决定是否发送通知
    if risk_level in ["low", "none"]:
        print("风险级别低，不发送通知")
        return
    
    # 构建通知消息
    title = f"智能体异常检测警报 - {risk_level.upper()}"
    
    message = f"""
{title}

风险级别: {risk_level.upper()}
异常类型: {result.get('anomaly_type', 'none')}
置信度: {result.get('confidence', 0):.2%}

证据:
{chr(10).join(f'• {ev}' for ev in result.get('evidence', []))}

建议: {result.get('recommendation', '无')}

检测时间: {result.get('timestamp', 'N/A')}
分析消息数: {result.get('messages_analyzed', 0)}
会话: {result.get('session_key', '未知')}
    """
    
    print(f"准备发送 {channel} 通知...")
    print(message)
    
    # 实际发送逻辑需要根据 OpenClaw 的 message 工具实现
    print("通知发送功能需要 OpenClaw message 工具集成")


def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw 集成异常检测 - 修复版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python openclaw_integration_fixed.py
  python openclaw_integration_fixed.py --session agent:main:main
  python openclaw_integration_fixed.py --limit 100
  python openclaw_integration_fixed.py --output report.json
        """
    )
    
    parser.add_argument(
        "--session", "-s",
        help="会话键（格式如 agent:main:main，不传则使用当前会话）"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=50,
        help="分析最近 N 条消息（默认 50）"
    )
    parser.add_argument(
        "--notify", "-n",
        choices=["dingtalk", "telegram", "whatsapp", "email", "none"],
        default="none",
        help="发送通知到指定渠道"
    )
    parser.add_argument(
        "--output", "-o",
        help="输出文件路径（JSON 格式报告）"
    )
    
    args = parser.parse_args()
    
    # 运行检测
    result = run_openclaw_detection(
        session_key=args.session,
        limit=args.limit
    )
    
    if result is None:
        print("检测失败")
        sys.exit(1)
    
    # 打印报告
    print_report(result)
    
    # 发送通知
    if args.notify != "none":
        send_notification(result, args.notify)
    
    # 保存报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n报告已保存：{args.output}")
    
    # 根据风险级别设置退出码
    risk_level = result.get("risk_level", "none")
    if risk_level in ["high", "critical"]:
        sys.exit(2)
    elif risk_level == "medium":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()