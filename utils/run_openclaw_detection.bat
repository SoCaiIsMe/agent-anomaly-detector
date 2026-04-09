@echo off
REM 运行 OpenClaw 集成异常检测

echo ========================================
echo OpenClaw 异常检测集成
echo ========================================

REM 设置环境变量
set ANOMALY_API_PROVIDER=vllm
set ANOMALY_VLLM_URL=http://211.87.232.207:8001/v1/completions
set ANOMALY_MODEL=trajad
set ANOMALY_THRESHOLD=0.7
set ANOMALY_TEMPERATURE=0.1
set ANOMALY_MAX_TOKENS=1024
set ANOMALY_TIMEOUT=60

echo.
echo 环境变量已设置:
echo API 提供商: %ANOMALY_API_PROVIDER%
echo 服务器地址: %ANOMALY_VLLM_URL%
echo 模型名称: %ANOMALY_MODEL%
echo.

echo 运行 OpenClaw 集成检测...
echo.

REM 运行脚本
python scripts/openclaw_integration_fixed.py %*

echo.
pause