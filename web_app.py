import streamlit as st 
from chatbot.langchain_agent import init_agent

 # 页面标题
st.title("🤖 AI 智能助手（ReAct Agent + Qwen）")

# === 初始化 Agent（仅一次）===
if "agent" not in st.session_state:
    try:
        api_key = st.secrets["DASHSCOPE_API_KEY"]
        st.session_state.agent = init_agent(api_key)
        st.success("✅ Agent 初始化成功！")
    except KeyError:
        st.error("❌ 未设置 DASHSCOPE_API_KEY，请在 Secrets 中配置。")
        st.stop()
    except Exception as e:
        st.error(f"❌ Agent 初始化失败: {str(e)}")
        st.stop()

# === 初始化会话状态 ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 👇👇👇 新增：初始化用户姓名 👇👇👇
if "user_name" not in st.session_state:
    st.session_state.user_name = None
# 👆👆👆 就加在这里！在 chat_history 初始化之后 👆👆👆

# 用户输入
user_input = st.chat_input("请输入你的问题，例如：'现在几点？' 或 '上海天气怎么样？'")

# 处理用户输入
if user_input:
    output = ""  # 初始化 output
    
    # 👇👇👇 新增：名字提取逻辑 👇👇👇
    if not st.session_state.user_name and ("我叫" in user_input or "我是" in user_input):
        name = user_input.replace("我叫", "").replace("我是", "").strip()
        if name and len(name) <= 10 and name.isalpha():  # 只允许字母
            st.session_state.user_name = name
            output = f"你好，{name}！很高兴认识你 😊"
    # 👆👆👆 名字逻辑结束 👆👆👆

    # 如果没触发名字逻辑，则调用 Agent
    if not output:
        with st.spinner("🤔 思考中..."):
            try:
                response = st.session_state.agent.invoke({
                    "input": user_input,
                    "chat_history": st.session_state.chat_history
                })
                output = response.get("output", "抱歉，我无法回答这个问题。")
            except Exception as e:
                output = f"⚠️ 执行出错: {str(e)}"

    # 保存对话历史
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": output})

# 显示聊天记录
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])