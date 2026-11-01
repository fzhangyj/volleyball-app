@echo off
chcp 65001 >nul
echo ========================================
echo 启动排球APP后端服务
echo ========================================
echo.

REM 获取脚本所在目录并切换到该目录
cd /d "%~dp0"
if errorlevel 1 (
    echo 错误：无法切换到backend目录
    pause
    exit /b 1
)

echo 检查Python环境...
REM 尝试多种方式查找Python
set PYTHON_CMD=
where python >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    python --version
) else (
    where py >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=py
        py --version
    ) else (
        if exist "<PROJECT_PATH>" (
            set PYTHON_CMD=<PROJECT_PATH>
            "%PYTHON_CMD%" --version
        ) else (
            echo 错误：未找到Python
            echo 提示：请确保Python已添加到系统PATH环境变量中
            pause
            exit /b 1
        )
    )
)

echo.
echo 检查依赖是否已安装...
"%PYTHON_CMD%" -c "import fastapi" 2>nul
if errorlevel 1 (
    echo 正在安装依赖...
    echo 使用 %PYTHON_CMD% -m pip 安装...
    "%PYTHON_CMD%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误：依赖安装失败
        echo 提示：请确保pip已正确安装，或手动执行: "%PYTHON_CMD%" -m pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo 依赖安装完成！
)

echo.
echo 启动FastAPI服务...
echo 服务地址：http://localhost:8000
echo API文档：http://localhost:8000/docs
echo 健康检查：http://localhost:8000/health
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

REM 使用检测到的Python命令启动服务
"%PYTHON_CMD%" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause

