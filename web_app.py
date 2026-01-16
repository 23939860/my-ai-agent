# -*- coding: utf-8 -*-
import streamlit as st
from chatbot.core import ask_qwen_with_tools as ask_qwen_with_memory
from chatbot.logger import log_conversation
from chatbot.memory import load_memory, save_memory
import json

st.set_page_config(page_title="🤖 AI 聊天机器人", layout="centered")

# 初始化会话状态
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = load_memory()
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 用户输入
user_input = st.chat_input("请输入你的问题...")
if user_input:
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # === AI 回复（带加载状态）===
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 正在思考...")
        
        try:
            answer = ask_qwen_with_memory(st.session_state.conversation_history + [{"role": "user", "content": user_input}])
            
            # 更新为最终回答
            message_placeholder.markdown(answer)
            
            # 添加到历史记录
            st.session_state.messages.append({"role": "assistant", "content": answer})
                
            # 记录日志
            log_conversation(user_input, answer)
            
            # 更新记忆
            st.session_state.conversation_history.append({"role": "user", "content": user_input})
            st.session_state.conversation_history.append({"role": "assistant", "content": answer})
           
            # ===== 新增：记忆压缩 =====
            if len(st.session_state.conversation_history) > 20:
                from chatbot.memory import summarize_conversation
                summary = summarize_conversation(st.session_state.conversation_history)
                recent_msgs = st.session_state.conversation_history[-4:]
                st.session_state.conversation_history = [
                    {"role": "system", "content": summary}
                ] + recent_msgs
                st.info("🧠 对话过长，已自动摘要并压缩记忆。")
            # =========================
            
        except Exception as e:
            error_msg = f"❌ 出错了: {str(e)}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
    # ===========================
# 保存记忆按钮
if st.button("💾 保存记忆"):
    save_memory(st.session_state.conversation_history)
    st.success("✅ 记忆已保存！")
    