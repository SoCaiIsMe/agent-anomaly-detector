@echo off
chcp 65001 >nul
echo 🔍 Python 环境简单检查
echo ========================================

echo.
echo 1. 检查 Python...
where python >nul 2>nul
if %errorlevel% equ 0 (
    echo ✅ Python 在 PATH 中
    python --version
) else (
    echo ❌ Python 不在 PATH 中
    echo 请安装 Python 3.8+
    echo 下载: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo 2. 检查 pip...
python -m pip --version >nul 2>nul
if %errorlevel% equ 0 (
    echo ✅ pip 已安装
    python -m pip --version
) else (
    echo ❌ pip 未安装
    echo 正在安装 pip...
    python -m ensurepip --default-pip
)

echo.
echo 3. 检查 requests 库...
python -c "import requests" 2>nul
if %errorlevel% equ 0 (
    echo ✅ requests 已安装
    python -c "import requests; print('版本: ' + requests.__version__)"
) else (
    echo ❌ requests 未安装
    echo 正在安装 requests...
    python -m pip install requests --user
)

echo.
echo 4. 测试 vLLM 连接...
python -c "
import requests
try:
    print('测试连接: http://211.87.232.207:8001/v1/models')
    response = requests.get('http://211.87.232.207:8001/v1/models', timeout=10)
    if response.status_code == 200:
        print('✅ API 连接成功！')
        import json
        data = response.json()
        models = data.get('data', [])
        print(f'找到 {len(models)} 个模型：')
        for model in models:
            model_id = model.get('id', 'unknown')
            print(f'  - {model_id}')
            if model_id == 'trajad':
                print(f'    🎯 找到目标模型: trajad')
    else:
        print(f'❌ API 连接失败: {response.status_code}')
except Exception as e:
    print(f'❌ 连接异常: {e}')
"

echo.
echo ========================================
echo 🎉 检查完成！
echo.
echo 现在可以运行：
echo 1. python test_trajad_vllm.py
echo 2. python scripts\detect_anomaly.py --input test_session.json
echo 3. 或双击 run_detection.bat
echo ========================================
pause