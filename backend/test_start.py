# -*- coding: utf-8 -*-
"""测试启动服务"""
import sys
import os

# 切换到backend目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("检查依赖...")
try:
    import fastapi
    import uvicorn
    print("依赖已安装")
except ImportError as e:
    print(f"缺少依赖: {e}")
    print("正在安装依赖...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("依赖安装完成")

print("\n启动服务...")
try:
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
except Exception as e:
    print(f"启动失败: {e}")
    import traceback
    traceback.print_exc()

