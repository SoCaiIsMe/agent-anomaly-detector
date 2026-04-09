# PowerShell 脚本：检查 Python 环境

Write-Host "🔍 Python 环境检查" -ForegroundColor Cyan
Write-Host "=" * 50

# 1. 检查 Python 命令
Write-Host "`n1. 检查 Python 命令..." -ForegroundColor Yellow

$pythonPaths = @()
$possiblePaths = @(
    "python",
    "python3",
    "py",
    "$env:USERPROFILE\AppData\Local\Programs\Python\Python39\python.exe",
    "$env:USERPROFILE\AppData\Local\Programs\Python\Python310\python.exe",
    "$env:USERPROFILE\AppData\Local\Programs\Python\Python311\python.exe",
    "C:\Python39\python.exe",
    "C:\Python310\python.exe",
    "C:\Python311\python.exe",
    "C:\Program Files\Python39\python.exe",
    "C:\Program Files\Python310\python.exe",
    "C:\Program Files\Python311\python.exe"
)

foreach ($cmd in $possiblePaths) {
    try {
        if ($cmd -match "^[a-zA-Z]+$") {
            # 检查命令
            $result = Get-Command $cmd -ErrorAction SilentlyContinue
            if ($result) {
                $pythonPaths += $result.Source
                Write-Host "  ✅ 找到: $($result.Source)" -ForegroundColor Green
            }
        } else {
            # 检查文件路径
            if (Test-Path $cmd) {
                $pythonPaths += $cmd
                Write-Host "  ✅ 找到: $cmd" -ForegroundColor Green
            }
        }
    } catch {
        # 忽略错误
    }
}

if ($pythonPaths.Count -eq 0) {
    Write-Host "  ❌ 未找到 Python" -ForegroundColor Red
    Write-Host "`n建议安装 Python 3.8+：" -ForegroundColor Yellow
    Write-Host "1. 访问 https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "2. 下载 Windows installer (64-bit)" -ForegroundColor White
    Write-Host "3. 安装时务必勾选 'Add Python to PATH'" -ForegroundColor White
    Write-Host "4. 重启终端后再次运行此脚本" -ForegroundColor White
    exit 1
}

# 使用第一个找到的 Python
$pythonExe = $pythonPaths[0]
Write-Host "`n使用 Python: $pythonExe" -ForegroundColor Cyan

# 2. 检查 Python 版本
Write-Host "`n2. 检查 Python 版本..." -ForegroundColor Yellow
try {
    $versionOutput = & $pythonExe --version 2>&1
    Write-Host "  $versionOutput" -ForegroundColor Green
} catch {
    Write-Host "  ❌ 无法获取版本" -ForegroundColor Red
}

# 3. 检查 pip
Write-Host "`n3. 检查 pip..." -ForegroundColor Yellow
try {
    $pipOutput = & $pythonExe -m pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ $($pipOutput | Select-String 'pip')" -ForegroundColor Green
    } else {
        Write-Host "  ❌ pip 未安装或有问题" -ForegroundColor Red
        Write-Host "  正在安装 pip..." -ForegroundColor Yellow
        & $pythonExe -m ensurepip --default-pip
    }
} catch {
    Write-Host "  ❌ 检查 pip 失败" -ForegroundColor Red
}

# 4. 检查 requests 库
Write-Host "`n4. 检查 requests 库..." -ForegroundColor Yellow
try {
    $testScript = @"
try:
    import requests
    print(f"✅ requests 版本: {requests.__version__}")
except ImportError:
    print("❌ requests 未安装")
"@
    
    $testScript | Out-File -FilePath "test_import.py" -Encoding UTF8
    $importOutput = & $pythonExe test_import.py 2>&1
    Remove-Item test_import.py -ErrorAction SilentlyContinue
    
    if ($importOutput -match "✅") {
        Write-Host "  $importOutput" -ForegroundColor Green
    } else {
        Write-Host "  $importOutput" -ForegroundColor Red
        Write-Host "  正在安装 requests..." -ForegroundColor Yellow
        & $pythonExe -m pip install requests --user
    }
} catch {
    Write-Host "  ❌ 检查 requests 失败" -ForegroundColor Red
}

# 5. 测试 vLLM 连接
Write-Host "`n5. 测试 vLLM 连接..." -ForegroundColor Yellow
try {
    $testApiScript = @"
import requests
import json

print("测试连接: http://211.87.232.207:8001/v1/models")
try:
    response = requests.get('http://211.87.232.207:8001/v1/models', timeout=10)
    if response.status_code == 200:
        print("✅ API 连接成功！")
        data = response.json()
        models = data.get('data', [])
        print(f"找到 {len(models)} 个模型：")
        for model in models:
            model_id = model.get('id', 'unknown')
            print(f"  - {model_id}")
            if model_id == 'trajad':
                print(f"    🎯 找到目标模型: trajad")
    else:
        print(f"❌ API 连接失败: {response.status_code}")
except Exception as e:
    print(f"❌ 连接异常: {e}")
"@
    
    $testApiScript | Out-File -FilePath "test_api.py" -Encoding UTF8
    $apiOutput = & $pythonExe test_api.py 2>&1
    Remove-Item test_api.py -ErrorAction SilentlyContinue
    
    Write-Host $apiOutput -ForegroundColor White
} catch {
    Write-Host "  ❌ 测试 API 失败" -ForegroundColor Red
}

Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
Write-Host "🎉 环境检查完成！" -ForegroundColor Green
Write-Host "`n下一步：" -ForegroundColor Yellow
Write-Host "1. 运行测试: .\test_trajad_vllm.py" -ForegroundColor White
Write-Host "2. 运行检测: python scripts\detect_anomaly.py --input test_session.json" -ForegroundColor White
Write-Host "3. 或双击 run_detection.bat" -ForegroundColor White
Write-Host "=" * 50 -ForegroundColor Cyan