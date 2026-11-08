#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试AI服务是否正常工作
运行方式：python3 test_ai.py
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai import ai_service
from app.services.prompts import (
    ACADEMY_QA_SYSTEM_PROMPT,
    get_academy_qa_prompt,
    format_messages
)


def test_simple_chat():
    """测试简单对话"""
    print("=" * 50)
    print("测试1: 简单对话")
    print("=" * 50)
    
    try:
        response = ai_service.chat("你好，请介绍一下你自己")
        print(f"AI回复：\n{response}\n")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_academy_qa():
    """测试足球知识问答"""
    print("=" * 50)
    print("测试2: 足球知识问答")
    print("=" * 50)
    
    try:
        question = "如何提高盘带技巧？"
        user_prompt = get_academy_qa_prompt(question)
        messages = format_messages(ACADEMY_QA_SYSTEM_PROMPT, user_prompt)
        
        response = ai_service.chat_with_history(messages)
        print(f"问题：{question}")
        print(f"\nAI回复：\n{response}\n")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_training_plan():
    """测试训练计划生成"""
    print("=" * 50)
    print("测试3: 训练计划生成")
    print("=" * 50)
    
    try:
        from app.services.prompts import (
            TRAINING_PLAN_SYSTEM_PROMPT,
            get_training_plan_prompt
        )
        
        goal = "提升射门精度"
        user_prompt = get_training_plan_prompt(goal, level="初级", duration="1周")
        messages = format_messages(TRAINING_PLAN_SYSTEM_PROMPT, user_prompt)
        
        response = ai_service.chat_with_history(messages)
        print(f"训练目标：{goal}")
        print(f"\nAI生成的训练计划：\n{response}\n")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n🚀 开始测试AI服务...\n")
    
    # 检查API Key
    if not ai_service.api_key or ai_service.api_key == "your-api-key-here":
        print("❌ 错误：未配置API Key")
        print("请创建 backend/.env 文件，并设置 VOLCENGINE_ARK_API_KEY")
        print("\n参考 .env.example 文件创建 .env 文件")
        return
    
    print(f"✅ API Key已配置")
    print(f"✅ 模型：{ai_service.model}")
    print(f"✅ API地址：{ai_service.base_url}\n")
    
    # 运行测试
    results = []
    results.append(("简单对话", test_simple_chat()))
    results.append(("足球知识问答", test_academy_qa()))
    results.append(("训练计划生成", test_training_plan()))
    
    # 输出结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    print(f"\n总计：{success_count}/{total_count} 通过")
    
    if success_count == total_count:
        print("\n🎉 所有测试通过！AI服务配置正确。")
    else:
        print("\n⚠️  部分测试失败，请检查配置和网络连接。")


if __name__ == "__main__":
    main()

