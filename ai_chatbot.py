import os
from datetime import datetime
import dashscope
from dashscope import Generation

# 替换为你的 API Key
dashscope.api_key = "sk-352ac2c447984745ad305c07ee3d169a"

def ask_qwen(prompt):
    response = Generation.call(
        model="qwen-max",
        prompt=prompt
    )
    return response.output.text

def log_conversation(user_msg, ai_msg):
    """将对话追加写入 chat_log.txt"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] 你: {user_msg}\n")
        f.write(f"[{timestamp}] AI: {ai_msg}\n")

# 主程序：循环对话（只保留一个！）
print("🤖 AI 聊天机器人已启动！输入 '退出' 结束对话。")
while True:
    user_input = input("\n你: ")
    if user_input == "退出":
        print("👋 再见！")
        break
    try:
        answer = ask_qwen(user_input)
        print(f"AI: {answer}")
        log_conversation(user_input, answer)  # ✅ 确保在这里调用
    except Exception as e:
        print(f"❌ 出错了: {e}")