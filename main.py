# -*- coding: utf-8 -*-
from chatbot.core import ask_qwen_with_tools as ask_qwen_with_memory
from chatbot.logger import log_conversation
from chatbot.memory import load_memory, save_memory

def main():
    print("🤖 带持久化记忆的 AI 聊天机器人已启动！输入 '退出' 结束对话。")
    
    # 启动时加载历史记忆
    conversation_history = load_memory()
    if conversation_history:
        print("💾 已加载之前的对话记忆。")
    
    try:
        while True:
            user_input = input("\n你: ")
            if user_input == "退出":
                print("👋 正在保存记忆...")
                break
                
            conversation_history.append({"role": "user", "content": user_input})
            
            try:
                answer = ask_qwen_with_memory(conversation_history)
                conversation_history.append({"role": "assistant", "content": answer})
                
                print(f"AI: {answer}")
                log_conversation(user_input, answer)
                
            except Exception as e:
                print(f"❌ 出错了: {e}")
                # 回滚用户消息（避免不完整历史）
                conversation_history.pop()
                
    finally:
        # 无论是否异常，都保存记忆
        save_memory(conversation_history)
        print("✅ 记忆已保存到 memory.json")

if __name__ == "__main__":
    main()