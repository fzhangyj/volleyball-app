#!/bin/bash

echo "========================================"
echo "启动排球APP后端服务"
echo "========================================"
echo ""

cd "$(dirname "$0")"

echo "检查Python环境..."
python3 --version || python --version
if [ $? -ne 0 ]; then
    echo "错误：未找到Python，请先安装Python"
    exit 1
fi

echo ""
echo "检查依赖是否已安装..."
python3 -c "import fastapi" 2>/dev/null || python -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装依赖..."
    pip3 install -r requirements.txt || pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误：依赖安装失败"
        exit 1
    fi
fi

echo ""
echo "启动FastAPI服务..."
echo "服务地址：http://localhost:8000"
echo "API文档：http://localhost:8000/docs"
echo "健康检查：http://localhost:8000/health"
echo ""
echo "按 Ctrl+C 停止服务"
echo "========================================"
echo ""

python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 || python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

