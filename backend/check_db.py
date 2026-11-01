#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库连接检查脚本
"""
import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("数据库配置检查")
print("=" * 50)
print()

# 检查环境变量
db_type = os.getenv("DB_TYPE", "sqlite")
print(f"当前数据库类型: {db_type}")

if db_type == "mysql":
    print("\n[警告] 检测到使用 MySQL 配置")
    print("\nMySQL 配置信息：")
    print(f"  主机: {os.getenv('DB_HOST', '127.0.0.1')}")
    print(f"  端口: {os.getenv('DB_PORT', '3306')}")
    print(f"  用户: {os.getenv('DB_USER', 'root')}")
    print(f"  数据库: {os.getenv('DB_NAME', 'my_app')}")
    
    print("\n正在测试 MySQL 连接...")
    try:
        import pymysql
        from app.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD
        
        connection = pymysql.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            connect_timeout=5
        )
        connection.close()
        print("[成功] MySQL 连接成功！")
    except Exception as e:
        print(f"[失败] MySQL 连接失败: {e}")
        print("\n解决方案：")
        print("1. 确保 MySQL 服务已启动")
        print("   Windows: net start MySQL80")
        print("   或使用服务管理器启动 MySQL 服务")
        print("\n2. 检查用户名和密码是否正确")
        print("   在 .env 文件中设置正确的 DB_PASSWORD")
        print("\n3. 或者切换到 SQLite（推荐用于开发）")
        print("   删除 .env 文件中的 DB_TYPE=mysql 行")
else:
    print("\n[成功] 使用 SQLite 数据库（默认配置）")
    from app.config import DB_PATH
    print(f"数据库文件路径: {DB_PATH}")
    
    if os.path.exists(DB_PATH):
        file_size = os.path.getsize(DB_PATH)
        print(f"数据库文件已存在，大小: {file_size / 1024:.2f} KB")
    else:
        print("数据库文件不存在，将在首次运行时自动创建")

print("\n" + "=" * 50)

