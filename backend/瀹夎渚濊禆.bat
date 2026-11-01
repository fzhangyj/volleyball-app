@echo off
chcp 65001 >nul
echo ========================================
echo 安装后端依赖包
echo ========================================
echo.

cd /d "%~dp0"

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
            echo.
            echo 请确保：
            echo 1. Python已正确安装
            echo 2. Python已添加到系统PATH环境变量
            echo 3. 或者手动指定Python路径
            pause
            exit /b 1
        )
    )
)

echo.
echo 正在安装依赖包...
echo 这可能需要几分钟时间，请耐心等待...
echo 使用的Python: %PYTHON_CMD%
echo.

"%PYTHON_CMD%" -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ========================================
    echo 依赖安装失败！
    echo ========================================
    echo 请尝试以下方法：
    echo 1. 检查网络连接
    echo 2. 手动执行: python -m pip install -r requirements.txt
    echo 3. 如果pip未安装，先执行: python -m ensurepip --upgrade
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo 依赖安装成功！
    echo ========================================
    echo 现在可以运行 start.bat 启动服务了
    pause
)

