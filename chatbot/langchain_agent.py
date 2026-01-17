# -*- coding: utf-8 -*-
import requests
from datetime import datetime
from langchain_core.tools import tool
from langchain.prompts import PromptTemplate
from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI

# ====== ReAct Prompt（硬编码）======
react_prompt = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""
prompt = PromptTemplate.from_template(react_prompt)

# ====== 工具定义（必须全部用 @tool 装饰）======
@tool
def get_current_time() -> str:
    """获取当前日期和时间"""
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
    """查询城市实时天气（使用 Open-Meteo 免费 API）"""
    city = city.strip()
    CITY_COORDS = {
        "上海": (31.23, 121.47),
        "北京": (39.90, 116.40),
        "广州": (23.12, 113.26),
        "深圳": (22.54, 114.05),
        "长沙": (28.23, 112.93),
        "杭州": (30.27, 120.15),
        "成都": (30.66, 104.06)
    }
    if city not in CITY_COORDS:
        supported = "、".join(CITY_COORDS.keys())
        return f"暂不支持「{city}」的天气查询。目前支持：{supported}"
    
    lat, lon = CITY_COORDS[city]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
    
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        temp = data["current"]["temperature_2m"]
        wcode = data["current"]["weather_code"]
        
        if wcode == 0:
            desc = "晴"
        elif 1 <= wcode <= 3:
            desc = "多云"
        elif wcode == 45 or wcode == 48:
            desc = "雾"
        elif 50 <= wcode <= 69:
            desc = "雨"
        elif 70 <= wcode <= 79:
            desc = "雪"
        else:
            desc = "阴"
            
        return f"{city}当前天气：{desc}，{temp}°C"
    except Exception:
        return "获取天气失败，请稍后再试"

# ====== 初始化 Agent ======
def init_agent(api_key: str):
    llm = ChatOpenAI(
        model="qwen-max",
        openai_api_key=api_key,
        openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        temperature=0
    )
    
    tools = [get_current_time, calculate_expression, get_weather]
    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    return executor