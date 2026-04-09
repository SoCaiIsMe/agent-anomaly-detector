@echo off
echo ========================================
echo 🐍 Python 环境修复工具
echo ========================================

echo.
echo 当前系统信息：
echo 用户：%USERNAME%
echo 系统：%OS%
echo.

echo 步骤 1：检查 Python 安装
echo.

REM 检查 Python 是否在 PATH 中
where python >nul 2>nul
if %errorlevel% equ 0 (
    echo ✅ Python 已在 PATH 中
    python --version
    goto :check_pip
) else (
    echo ❌ Python 未在 PATH 中
)

echo.
echo 步骤 2：查找已安装的 Python
echo.

REM 检查常见安装位置
set FOUND=0

echo 检查 C:\Python...
if exist "C:\Python39\python.exe" (
    echo ✅ 找到 Python 3.9: C:\Python39
    set "PYTHON_PATH=C:\Python39"
    set FOUND=1
)
if exist "C:\Python310\python.exe" (
    echo ✅ 找到 Python 3.10: C:\Python310
    set "PYTHON_PATH=C:\Python310"
    set FOUND=1
)
if exist "C:\Python311\python.exe" (
    echo ✅ 找到 Python 3.11: C:\Python311
    set "PYTHON_PATH=C:\Python311"
    set FOUND=1
)

echo 检查 Program Files...
if exist "C:\Program Files\Python39\python.exe" (
    echo ✅ 找到 Python 3.9: C:\Program Files\Python39
    set "PYTHON_PATH=C:\Program Files\Python39"
    set FOUND=1
)
if exist "C:\Program Files\Python310\python.exe" (
    echo ✅ 找到 Python 3.10: C:\Program Files\Python310
    set "PYTHON_PATH=C:\Program Files\Python310"
    set FOUND=1
)

echo 检查用户目录...
if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python39\python.exe" (
    echo ✅ 找到 Python 3.9: %%USERPROFILE%%\AppData\Local\Programs\Python\Python39
    set "PYTHON_PATH=%USERPROFILE%\AppData\Local\Programs\Python\Python39"
    set FOUND=1
)
if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python310\python.exe" (
    echo ✅ 找到 Python 3.10: %%USERPROFILE%%\AppData\Local\Programs\Python\Python310
    set "PYTHON_PATH=%USERPROFILE%\AppData\Local\Programs\Python\Python310"
    set FOUND=1
)

if %FOUND% equ 0 (
    echo ❌ 未找到已安装的 Python
    echo.
    echo 建议安装 Python 3.8+：
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载 Windows installer
    echo 3. 安装时勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo.
echo 步骤 3：临时添加到 PATH
echo.

echo 设置 Python 路径：%PYTHON_PATH%
set "PATH=%PYTHON_PATH%;%PYTHON_PATH%\Scripts;%PATH%"

:check_pip
echo.
echo 步骤 4：检查 pip
echo.

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
echo 步骤 5：安装 requests 库
echo.

python -c "import requests" 2>nul
if %errorlevel% equ 0 (
    echo ✅ requests 库已安装
) else (
    echo 安装 requests 库...
    python -m pip install requests --user
)

echo.
echo 步骤 6：测试环境
echo.

echo 测试 Python 版本：
python --version

echo.
echo 测试 requests 库：
python -c "import requests; print('✅ requests 版本：' + requests.__version__)"

echo.
echo 步骤 7：测试 vLLM 连接
echo.

echo 测试 API 连接...
python -c "
import requests
try:
    response = requests.get('http://211.87.232.207:8001/v1/models', timeout=10)
    if response.status_code == 200:
        print('✅ API 连接成功！')
        data = response.json()
        models = data.get('data', [])
        print(f'找到 {len(models)} 个模型：')
        for model in models:
            print(f'  - {model.get(\"id\", \"unknown\")}')
    else:
        print(f'❌ API 连接失败：{response.status_code}')
except Exception as e:
    print(f'❌ 连接异常：{e}')
"

echo.
echo ========================================
echo 🎉 Python 环境修复完成！
echo ========================================
echo.
echo 现在可以运行：
echo 1. python test_trajad_vllm.py
echo 2. python scripts/detect_anomaly.py --input test_session.json
echo 3. 或双击 run_detection.bat
echo.
pause