"""
测试火山方舟AI调用
"""
import sys
import os

# 添加app目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

from app.services.ai import simple_chat, chat_with_ai
from app.services.prompts import (
    get_action_analysis_prompt,
    get_qa_prompt,
    VOLLEYBALL_COACH_SYSTEM
)


def test_simple_chat():
    """测试简单对话"""
    print("\n" + "="*60)
    print("测试1: 简单对话")
    print("="*60)
    
    result = simple_chat("你好，请介绍一下自己")
    
    if result['success']:
        print(f"✅ 调用成功")
        print(f"📝 回复内容：\n{result['content']}")
        print(f"📊 Token使用：{result.get('usage', {})}")
    else:
        print(f"❌ 调用失败：{result.get('error')}")
    
    return result['success']


def test_coach_mode():
    """测试教练模式"""
    print("\n" + "="*60)
    print("测试2: 教练模式对话")
    print("="*60)
    
    result = simple_chat(
        "我的发球总是不稳定，有什么改进建议吗？",
        system_prompt=VOLLEYBALL_COACH_SYSTEM
    )
    
    if result['success']:
        print(f"✅ 调用成功")
        print(f"📝 回复内容：\n{result['content']}")
        print(f"📊 Token使用：{result.get('usage', {})}")
    else:
        print(f"❌ 调用失败：{result.get('error')}")
    
    return result['success']


def test_action_analysis():
    """测试动作分析"""
    print("\n" + "="*60)
    print("测试3: 动作分析")
    print("="*60)
    
    prompt = get_action_analysis_prompt(
        action_type="扣球",
        user_description="我扣球时感觉力量不足，而且经常下网"
    )
    
    result = simple_chat(prompt)
    
    if result['success']:
        print(f"✅ 调用成功")
        print(f"📝 回复内容：\n{result['content']}")
        print(f"📊 Token使用：{result.get('usage', {})}")
    else:
        print(f"❌ 调用失败：{result.get('error')}")
    
    return result['success']


def test_multi_turn_conversation():
    """测试多轮对话"""
    print("\n" + "="*60)
    print("测试4: 多轮对话")
    print("="*60)
    
    # 第一轮
    messages = [
        {"role": "system", "content": VOLLEYBALL_COACH_SYSTEM},
        {"role": "user", "content": "排球发球有哪些技巧？"}
    ]
    
    result1 = chat_with_ai(messages)
    
    if not result1['success']:
        print(f"❌ 第一轮调用失败：{result1.get('error')}")
        return False
    
    print(f"👤 用户: 排球发球有哪些技巧？")
    print(f"🤖 AI: {result1['content'][:100]}...")
    
    # 第二轮
    messages.append({"role": "assistant", "content": result1['content']})
    messages.append({"role": "user", "content": "那上手发球的要点是什么？"})
    
    result2 = chat_with_ai(messages)
    
    if result2['success']:
        print(f"👤 用户: 那上手发球的要点是什么？")
        print(f"🤖 AI: {result2['content'][:100]}...")
        print(f"✅ 多轮对话成功")
        print(f"📊 总Token使用：{result2.get('usage', {})}")
    else:
        print(f"❌ 第二轮调用失败：{result2.get('error')}")
    
    return result2['success']


def main():
    """运行所有测试"""
    print("\n🚀 开始测试火山方舟AI服务\n")
    
    tests = [
        ("简单对话", test_simple_chat),
        ("教练模式", test_coach_mode),
        ("动作分析", test_action_analysis),
        ("多轮对话", test_multi_turn_conversation)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ {name}测试异常：{e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！AI服务已正常工作")
    else:
        print("\n⚠️  部分测试失败，请检查配置")


if __name__ == "__main__":
    main()

