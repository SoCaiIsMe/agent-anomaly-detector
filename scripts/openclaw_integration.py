#!/usr/bin/env python3
"""
OpenClaw 集成脚本
通过 OpenClaw API 获取会话历史，然后进行异常检测
"""

import argparse
import json
import os
import sys
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


def get_openclaw_session_history(session_key, limit=50):
    """
    通过 OpenClaw API 获取会话历史
    
    注意：这个函数需要 OpenClaw Gateway 正在运行
    并且有权限访问 sessions_history API
    """
    # OpenClaw Gateway API 地址
    gateway_url = os.getenv("OPENCLAW_GATEWAY_URL", "http://localhost:3000")
    
    # 这里需要根据实际 OpenClaw 配置调整
    # 实际实现可能需要认证或使用不同的 API 端点
    
    print(f"警告：OpenClaw API 集成尚未完全实现")
    print(f"当前会话: {session_key}")
    print(f"限制: {limit} 条消息")
    
    # 返回空列表，实际实现需要调用 OpenClaw API
    return []


def run_openclaw_detection(session_key=None, limit=50):
    """执行 OpenClaw 集成检测"""
    print(f"开始 OpenClaw 异常检测...")
    print(f"会话: {session_key or '当前会话'}")
    print(f"模型: {MODEL_NAME} ({API_PROVIDER})")
    print("-" * 50)
    
    # 获取会话历史
    if session_key:
        messages = get_openclaw_session_history(session_key, limit)
    else:
        # 当前会话 - 需要特殊处理
        print("分析当前会话...")
        messages = []
    
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
    title = f"🔍 智能体异常检测警报 - {risk_level.upper()}"
    
    message = f"""
{title}

📊 风险级别: {risk_level.upper()}
🏷️  异常类型: {result.get('anomaly_type', 'none')}
📈 置信度: {result.get('confidence', 0):.2%}

📋 证据:
{chr(10).join(f'• {ev}' for ev in result.get('evidence', []))}

💡 建议: {result.get('recommendation', '无')}

⏰ 检测时间: {result.get('timestamp', 'N/A')}
📊 分析消息数: {result.get('messages_analyzed', 0)}
    """
    
    print(f"准备发送 {channel} 通知...")
    print(message)
    
    # 实际发送逻辑需要根据 OpenClaw 的 message 工具实现
    print("通知发送功能需要 OpenClaw message 工具集成")


def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw 集成异常检测",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python openclaw_integration.py
  python openclaw_integration.py --session abc123
  python openclaw_integration.py --notify dingtalk
        """
    )
    
    parser.add_argument(
        "--session", "-s",
        help="会话 ID（不传则分析当前会话）"
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
        sys.exit(1)
    
    # 输出结果
    print("\n" + "=" * 60)
    print("🔍 OpenClaw 异常检测报告")
    print("=" * 60)
    
    risk_level = result.get("risk_level", "unknown")
    icons = {
        "none": "✅",
        "low": "🟢",
        "medium": "🟡",
        "high": "🟠",
        "critical": "🔴"
    }
    
    print(f"\n{icons.get(risk_level, '❓')} 风险级别：{risk_level.upper()}")
    print(f"📊 异常置信度：{result.get('confidence', 0):.2%}")
    print(f"🏷️  异常类型：{result.get('anomaly_type', 'none')}")
    
    if result.get("session_key"):
        print(f"🔑 会话 ID：{result['session_key']}")
    
    # 发送通知
    if args.notify != "none":
        send_notification(result, args.notify)
    
    # 保存报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n报告已保存：{args.output}")
    
    # 根据风险级别设置退出码
    if risk_level in ["high", "critical"]:
        sys.exit(2)
    elif risk_level == "medium":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()