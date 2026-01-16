# -*- coding: utf-8 -*-
import json
import os
from typing import List, Dict

MEMORY_FILE = "memory.json"

def save_memory(messages: List[Dict[str, str]]):
    """将对话历史保存到 memory.json"""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def load_memory() -> List[Dict[str, str]]:
    """从 memory.json 加载历史对话"""
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list) and all(
                isinstance(msg, dict) and "role" in msg and "content" in msg
                for msg in data
            ):
                return data
    except (json.JSONDecodeError, IOError):
        pass
    return []

# ================================
# 新增：记忆摘要功能（第10步 C）
# ================================

def summarize_conversation(messages: List[Dict[str, str]]) -> str:
    """
    对对话历史进行简单摘要（保留最近关键信息）
    返回格式化字符串，可作为系统消息注入
    """
    if len(messages) < 3:
        return ""
    
    recent = messages[-10:] if len(messages) > 10 else messages
    summary_lines = ["【对话摘要】"]
    
    for msg in recent:
        role = "用户" if msg["role"] == "user" else "AI"
        content = msg["content"].strip()
        if len(content) > 60:
            content = content[:57] + "..."
        summary_lines.append(f"- {role}: {content}")
    
    return "\n".join(summary_lines)