# -*- coding: utf-8 -*-
import os
from langchain_core.tools import tool
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.chat_models import ChatOpenAI

# === 工具定义（LangChain 风格）===
@tool
def get_current_time() -> str:
    """获取当前日期和时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def calculate_expression(expr: str) -> str:
    """安全地计算数学表达式"""
    try:
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expr):
            return "❌ 表达式包含非法字符"
        result = eval(expr, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"❌ 计算错误: {str(e)}"

@tool
def get_weather(city: str) -> str:
    """查询城市天气（模拟 API）"""
    weather_map = {
        "北京": "晴，15°C",
        "上海": "多云，18°C",
        "广州": "小雨，22°C",
        "深圳": "阴，20°C"
    }
    return weather_map.get(city.strip(), f"暂不支持 {city} 的天气查询")

# === 初始化 Agent ===
def init_agent(api_key):
    llm = ChatOpenAI(
        model="qwen-max",
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    tools = [get_current_time, calculate_expression, get_weather]
    
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, tools, prompt)
    
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10
    )
    
    return executor