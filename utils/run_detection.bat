@echo off
REM 智能体异常检测一键运行脚本
REM 适用于 Windows 系统

echo ========================================
echo [检测] 智能体异常轨迹检测系统
echo ========================================

REM 检查 Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖
echo 检查依赖库...
python -c "import requests" 2>nul
if %errorlevel% neq 0 (
    echo 安装 requests 库...
    pip install requests
)

REM 检查配置文件
if not exist .env (
    echo 配置文件 .env 不存在
    echo 请从模板创建：copy .env.vllm .env
    echo 然后编辑 .env 文件，设置你的 vLLM 服务器地址
    pause
    exit /b 1
)

REM 显示配置
echo.
echo 当前配置：
echo API 提供商: vllm
echo 服务器地址: http://211.87.232.207:8001/v1
echo 模型名称: trajad (Qwen3-8B + LoRA)
echo 检测阈值: 0.7
echo.

echo 请选择操作：
echo 1. 测试 trajad 模型连接
echo 2. 运行异常检测（测试数据）
echo 3. 运行异常检测并保存报告
echo 4. 查看帮助
echo 5. 退出
echo.

set /p choice="请输入选项 (1-5): "

if "%choice%"=="1" (
    echo 测试 trajad 模型连接...
    python test_trajad_vllm.py
    pause
    goto :eof
)

if "%choice%"=="2" (
    echo 运行异常检测（测试数据）...
    python scripts/detect_anomaly.py --input test_session.json
    pause
    goto :eof
)

if "%choice%"=="3" (
    set /p output="请输入报告文件名（默认：report.json）: "
    if "%output%"=="" set output=report.json
    echo 运行异常检测并保存报告...
    python scripts/detect_anomaly.py --input test_session.json --output %output%
    pause
    goto :eof
)

if "%choice%"=="4" (
    echo.
    echo 使用说明：
    echo 1. 首先编辑 .env 文件，设置你的 vLLM 服务器地址
    echo 2. 运行测试确保连接正常
    echo 3. 使用检测功能
    echo.
    echo 配置文件示例：
    echo ANOMALY_API_PROVIDER=vllm
    echo ANOMALY_VLLM_URL=http://192.168.1.100:8000/v1/completions
    echo ANOMALY_MODEL=qwen2.5:7b
    echo.
    pause
    goto :eof
)

if "%choice%"=="5" (
    exit /b 0
)

echo 无效选项
pause