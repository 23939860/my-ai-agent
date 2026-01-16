# -*- coding: utf-8 -*-
import streamlit as st
from chatbot.langchain_agent import init_agent
from chatbot.logger import log_conversation
from chatbot.memory import load_memory, save_memory, summarize_conversation
from langchain_core.messages import HumanMessage, AIMessage  # 👈 新增导入

st.set_page_config(page_title="🤖 AI 聊天机器人", layout="centered")

# 初始化会话状态
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = load_memory()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = init_agent()

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
            # 🔧 转换对话历史为 LangChain 兼容格式
            def convert_to_messages(history):
                messages = []
                for msg in history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
                return messages
            
            chat_history = convert_to_messages(st.session_state.conversation_history)

            # 调用 LangChain Agent
            response = st.session_state.agent.invoke({
                "input": user_input,
                "chat_history": chat_history  # 使用转换后的格式
            })
            answer = response["output"]
            
            # 更新为最终回答
            message_placeholder.markdown(answer)
            
            # 添加到历史记录
            st.session_state.messages.append({"role": "assistant", "content": answer})
                
            # 记录日志
            log_conversation(user_input, answer)
            
            # 更新记忆（仍用 dict 格式存储）
            st.session_state.conversation_history.append({"role": "user", "content": user_input})
            st.session_state.conversation_history.append({"role": "assistant", "content": answer})
           
            # ===== 记忆压缩 =====
            if len(st.session_state.conversation_history) > 20:
                summary = summarize_conversation(st.session_state.conversation_history)
                recent_msgs = st.session_state.conversation_history[-4:]
                st.session_state.conversation_history = [
                    {"role": "system", "content": summary}
                ] + recent_msgs
                st.info("🧠 对话过长，已自动摘要并压缩记忆。")
            # ===================
            
        except Exception as e:
            error_msg = f"❌ 出错了: {str(e)}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            # 可选：显示详细错误（调试用）
            # st.error(f"开发者调试信息: {type(e).__name__}: {e}")

# 保存记忆按钮
if st.button("💾 保存记忆"):
    save_memory(st.session_state.conversation_history)
    st.success("✅ 记忆已保存！")