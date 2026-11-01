"""
快速测试火山方舟AI调用（单个测试）
"""
import sys
import os

# 添加app目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

from app.services.ai import simple_chat


def main():
    """快速测试"""
    print("🚀 测试火山方舟AI调用...\n")
    
    # 测试简单对话
    result = simple_chat("你好，请用一句话介绍排球运动")
    
    if result['success']:
        print("✅ AI调用成功！\n")
        print(f"📝 AI回复：\n{result['content']}\n")
        print(f"📊 Token使用：{result.get('usage', {})}")
        print("\n🎉 AI基础设施搭建完成，服务正常工作！")
    else:
        print(f"❌ AI调用失败：{result.get('error')}")
        print("\n⚠️  请检查：")
        print("1. .env 文件中的 VOLC_API_KEY 是否正确")
        print("2. 网络连接是否正常")
        print("3. API配置是否正确")


if __name__ == "__main__":
    main()

