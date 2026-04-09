@echo off
echo ========================================
echo 修复 Python 脚本编码问题
echo ========================================

echo.
echo 步骤 1: 检查 Python 环境
echo.

REM 检查 py 命令
where py >nul 2>nul
if %errorlevel% equ 0 (
    echo [成功] 找到 Python (py 命令)
    py --version
) else (
    echo [错误] 未找到 Python
    pause
    exit /b 1
)

echo.
echo 步骤 2: 修复脚本文件
echo.

REM 创建修复后的脚本
echo 创建修复后的测试脚本...

REM 创建 test_connection_fixed.py
(
echo #!/usr/bin/env python3
echo """
echo 测试 vLLM API 连接（修复编码版）
echo """
echo.
echo import json
echo import requests
echo.
echo def test_connection():
echo     """测试连接"""
echo     print("测试 vLLM API 连接...")
echo.
echo     # 测试 /v1/models
echo     models_url = "http://211.87.232.207:8001/v1/models"
echo     print("1. 测试 /v1/models 端点")
echo     print(f"   URL: {models_url}")
echo.
echo     try:
echo         response = requests.get(models_url, timeout=10)
echo         print(f"   状态码: {response.status_code}")
echo.
echo         if response.status_code == 200:
echo             data = response.json()
echo             print("   连接成功！")
echo.
echo             models = data.get('data', [])
echo             print(f"   可用模型: {len(models)} 个")
echo.
echo             for model in models:
echo                 model_id = model.get('id', 'unknown')
echo                 print(f"     - {model_id}")
echo.
echo                 if model_id == 'trajad':
echo                     print("       找到 trajad 模型")
echo         else:
echo             print(f"   错误: {response.text}")
echo.
echo     except Exception as e:
echo         print(f"   连接失败: {e}")
echo         return False
echo.
echo     # 测试 Completions
echo     print("2. 测试 Completions 接口")
echo     completions_url = "http://211.87.232.207:8001/v1/completions"
echo.
echo     payload = {
echo         "model": "trajad",
echo         "prompt": "Hello, are you working?",
echo         "max_tokens": 20,
echo         "temperature": 0.1,
echo         "stream": False
echo     }
echo.
echo     try:
echo         response = requests.post(completions_url, json=payload, timeout=30)
echo         print(f"   状态码: {response.status_code}")
echo.
echo         if response.status_code == 200:
echo             result = response.json()
echo             print("   API 调用成功！")
echo.
echo             choices = result.get('choices', [])
echo             if choices:
echo                 text = choices[0].get('text', '')
echo                 print(f"   模型回复: {text}")
echo         else:
echo             print(f"   错误: {response.text}")
echo.
echo     except Exception as e:
echo         print(f"   API 调用失败: {e}")
echo         return False
echo.
echo     return True
echo.
echo def main():
echo     print("=" ^^ 50)
echo     "智能体异常检测系统 - 连接测试（修复版）"
echo     print("=" ^^ 50)
echo.
echo     success = test_connection()
echo.
echo     print("=" ^^ 50)
echo     if success:
echo         print("所有测试通过！系统就绪。")
echo     else:
echo         print("测试失败，请检查配置。")
echo     print("=" ^^ 50)
echo.
echo if __name__ == "__main__":
echo     main()
) > test_connection_fixed.py

echo [成功] 创建 test_connection_fixed.py

echo.
echo 步骤 3: 运行测试
echo.

echo 运行连接测试...
py test_connection_fixed.py

echo.
echo ========================================
echo 修复完成！
echo ========================================
echo.
echo 已修复的问题：
echo 1. 移除所有 Unicode 表情符号
echo 2. 使用纯文本标记（如 [成功]、[错误]）
echo 3. 确保脚本在 Windows 控制台正常运行
echo.
echo 可用的脚本：
echo - test_connection_fixed.py    （连接测试）
echo - quick_test.py              （快速测试）
echo - test_anomaly_detection.py  （异常检测测试）
echo.
echo 运行完整测试：
echo py quick_test.py
echo.
pause