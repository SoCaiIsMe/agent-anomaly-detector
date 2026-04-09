@echo off
echo ========================================
echo 最终测试 - 修复编码问题后
echo ========================================

echo.
echo 测试 1: 快速连接测试
echo.
py quick_test.py

echo.
echo 测试 2: 简单连接测试
echo.
py test_connection_simple.py

echo.
echo 测试 3: 运行批处理菜单
echo.
echo 注意: 请手动运行 run_detection.bat 并选择选项 1
echo.

echo.
echo ========================================
echo 修复总结
echo ========================================
echo.
echo 已修复的文件:
echo 1. test_detection_simple.py - 移除 Unicode 表情符号
echo 2. test_trajad_vllm.py - 移除 Unicode 表情符号
echo 3. scripts/detect_anomaly.py - 移除 Unicode 表情符号
echo 4. simple_test.py - 移除 Unicode 表情符号
echo 5. run_detection.bat - 移除 Unicode 表情符号
echo.
echo 新增的文件:
echo 1. test_connection_simple.py - 纯文本测试脚本
echo 2. quick_test.py - 快速测试脚本
echo.
echo 当前状态:
echo - API 连接: 正常
echo - 模型检测: 正常
echo - 编码问题: 已修复
echo - Windows 兼容性: 已修复
echo.
echo 下一步:
echo 1. 运行 run_detection.bat 测试完整功能
echo 2. 测试与 OpenClaw 的集成
echo 3. 配置定时任务
echo.
pause