"""
测试数据库连接和创建
"""
import os
import pymysql

def test_database():
    """测试数据库连接和创建"""
    try:
        print("=" * 50)
        print("测试MySQL连接和数据库创建")
        print("=" * 50)
        
        # 1. 测试连接MySQL服务器
        print("\n1. 正在连接MySQL服务器...")
        connection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password=os.environ['DB_PASSWORD'],
            charset='utf8mb4'
        )
        print("✓ MySQL服务器连接成功")
        
        # 2. 查看现有数据库
        print("\n2. 查看现有数据库...")
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print("现有数据库列表：")
            for db in databases:
                print(f"  - {db[0]}")
        
        # 3. 创建数据库（如果不存在）
        print("\n3. 创建数据库 my_app...")
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS my_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            connection.commit()
            print("✓ 数据库创建命令执行成功")
        
        # 4. 验证数据库是否存在
        print("\n4. 验证数据库是否存在...")
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES LIKE 'my_app'")
            result = cursor.fetchone()
            if result:
                print(f"✓ 数据库 {result[0]} 已存在")
            else:
                print("❌ 数据库 my_app 不存在")
        
        # 5. 连接到my_app数据库并查看表
        print("\n5. 连接到 my_app 数据库...")
        connection.select_db('my_app')
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            if tables:
                print("现有数据表：")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("⚠ 数据库中没有表（这是正常的，表会在后端启动时创建）")
        
        connection.close()
        print("\n" + "=" * 50)
        print("✓ 测试完成！数据库 my_app 已准备就绪")
        print("=" * 50)
        
    except pymysql.Error as e:
        print(f"\n❌ MySQL错误: {e}")
        print("\n请检查：")
        print("1. MySQL服务是否已启动")
        print("2. 用户名和密码是否正确（环境变量 DB_USER / DB_PASSWORD）")
        print("3. MySQL是否允许本地连接")
        print("\nWindows启动MySQL方法：")
        print("  - 打开服务管理器（services.msc）")
        print("  - 找到MySQL服务并启动")
        return False
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_database()

