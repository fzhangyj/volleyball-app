@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo 启动排球APP后端服务
echo ========================================
echo.

echo 检查Python环境...
py --version
if errorlevel 1 (
    echo 错误：未找到Python
    pause
    exit /b 1
)

echo.
echo 安装/更新依赖...
py -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo 警告：依赖安装可能有问题
)

echo.
echo 启动服务...
echo 服务地址：http://localhost:8000
echo API文档：http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause

