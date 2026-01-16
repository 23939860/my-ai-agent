from datetime import datetime

def log_conversation(user_msg: str, ai_msg: str, filename: str = "chat_log.txt"):
    """将对话追加写入日志文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] 你: {user_msg}\n")
        f.write(f"[{timestamp}] AI: {ai_msg}\n")