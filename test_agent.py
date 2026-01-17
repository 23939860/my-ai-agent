import os
os.environ['DASHSCOPE_API_KEY'] = 'sk-352ac2c447984745ad305c07ee3d169a'

from langchain_community.chat_models import ChatOpenAI
from datetime import datetime

llm = ChatOpenAI(
    model="qwen-max",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 测试调用
response = llm.invoke("现在几点？")
print('🤖 回答:', response.content)
