#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动脚本 - 用于处理中文路径问题
"""
import os
import sys

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print("=" * 50)
print("启动排球APP后端服务")
print("=" * 50)
print(f"工作目录: {os.getcwd()}")
print()

# 检查main.py是否存在
if not os.path.exists("app/main.py"):
    print("错误：未找到 app/main.py 文件")
    sys.exit(1)

# 启动uvicorn
print("正在启动FastAPI服务...")
print("服务地址：http://localhost:8000")
print("API文档：http://localhost:8000/docs")
print("健康检查：http://localhost:8000/health")
print()
print("按 Ctrl+C 停止服务")
print("=" * 50)
print()

if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"\n错误：{e}")
        sys.exit(1)

