import streamlit as st
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults
from datetime import datetime
from langchain.agents import create_react_agent, AgentExecutor, Tool
from langchain import hub
import os
import tempfile

# ======================
# 安全获取 API Key
# ======================
if "DASHSCOPE_API_KEY" not in st.secrets:
    st.error("❌ 请在 Streamlit Cloud 的 Secrets 中设置 DASHSCOPE_API_KEY")
    st.stop()

QWEN_API_KEY = st.secrets["DASHSCOPE_API_KEY"]

# 初始化 LLM（用于聊天和 PDF 问答）
llm = ChatOpenAI(
    model="qwen-max",
    api_key=QWEN_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# ======================
# Streamlit 页面设置
# ======================
st.set_page_config(page_title="🤖 AI 智能助手（ReAct + PDF）", layout="wide")
st.title("🤖 AI 智能助手（ReAct Agent + Qwen + PDF）")

# 初始化 session_state
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_executor" not in st.session_state:
    # 自定义获取当前时间的工具
    def get_current_time(*args, **kwargs):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    tools = [
        TavilySearchResults(
            max_results=3,
            api_key=st.secrets["TAVILY_API_KEY"]  # 显式传入密钥
        ),
        Tool(
            name="CurrentTime",
            func=get_current_time,
            description="获取当前日期和时间"
        )
    ]
    react_prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, tools, react_prompt)
    st.session_state.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# ======================
# PDF 上传区
# ======================
with st.expander("📁 上传 PDF 文档（可选）"):
    uploaded_file = st.file_uploader("选择一个 PDF 文件", type=["pdf"], label_visibility="collapsed")

    if uploaded_file and st.session_state.vectorstore is None:
        with st.spinner("正在解析 PDF..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            try:
                loader = UnstructuredPDFLoader(tmp_path)
                docs = loader.load()
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                splits = text_splitter.split_documents(docs)
                
                from langchain_community.embeddings import HuggingFaceEmbeddings
                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
                vectorstore = FAISS.from_documents(splits, embeddings)
                st.session_state.vectorstore = vectorstore
                st.success("✅ PDF 解析完成！现在可以提问文档内容。")
            except Exception as e:
                st.error(f"❌ PDF 解析失败: {e}")
            finally:
                os.unlink(tmp_path)

# ======================
# 聊天区
# ======================
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

if prompt := st.chat_input("例如：'现在几点？' 或 '这份文档讲了什么？'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                if st.session_state.vectorstore is not None:
                    retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 3})
                    template = """
                    你是一个专业的文档分析助手。请根据以下上下文回答问题。
                    如果不知道答案，请说“根据文档内容无法确定”。
                    
                    上下文：
                    {context}
                    
                    问题：{question}
                    """
                    prompt_template = ChatPromptTemplate.from_template(template)
                    rag_chain = (
                        {"context": retriever, "question": RunnablePassthrough()}
                        | prompt_template
                        | llm
                        | StrOutputParser()
                    )
                    response = rag_chain.invoke(prompt)
                else:
                    response = st.session_state.agent_executor.invoke({"input": prompt})["output"]
                
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"抱歉，处理时出错：{str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})