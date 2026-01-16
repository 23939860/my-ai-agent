# -*- coding: utf-8 -*-
import os
import streamlit as st
import dashscope
from dashscope import Generation

# 🔐 使用 Streamlit Secrets 获取 API Key
api_key = st.secrets.get("DASHSCOPE_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise ValueError("请设置 DASHSCOPE_API_KEY")
dashscope.api_key = api_key

# 工具描述（给 AI 看的说明书）
TOOL_DESCRIPTIONS = """
你可以使用以下工具来帮助用户：

1. 【计算】当你需要进行数学计算时，请回复：
   TOOL: CALCULATE|<表达式>
   例如：TOOL: CALCULATE|2+3*4

2. 【天气】当用户询问某地天气时，请回复：
   TOOL: WEATHER|<城市名>
   例如：TOOL: WEATHER|北京

3. 【时间】当用户问现在几点或今天日期时，请回复：
   TOOL: TIME|

注意：只有在确实需要工具时才使用，否则直接回答。
"""

def ask_qwen_with_tools(query, history):
    try:
        response = dashscope.Generation.call(
            model="qwen-max",
            messages=history + [{"role": "user", "content": query}],
        )
        
        # ✅ 关键：先检查状态码，再访问 output
        if response.status_code != 200:
            return f"❌ API 错误: {response.code} - {response.message}"
        
        # ✅ 安全访问 output 字段
        output = getattr(response, 'output', None)
        if output is None:
            return "❌ API 返回异常：output 为空"
        
        choices = output.get('choices', [])
        if not choices:
            return "❌ API 返回异常：无有效回答"
        
        message = choices[0].get('message', {})
        raw_answer = message.get('content', '').strip()
        
        # === 工具调用逻辑 ===
        if raw_answer.startswith("TOOL:"):
            parts = raw_answer.split("|", 1)
            tool_name = parts[0].replace("TOOL:", "").strip()
            args = parts[1].strip() if len(parts) > 1 else ""
            
            from .tools import get_weather, calculate_expression, get_current_time
            
            if tool_name == "WEATHER":
                return get_weather(args)
            elif tool_name == "CALCULATE":
                return calculate_expression(args)
            elif tool_name == "TIME":
                return get_current_time()
            else:
                return f"❌ 未知工具: {tool_name}"
        else:
            return raw_answer
        # ===================

    except Exception as e:
        return f"⚠️ 网络或服务异常，请稍后重试：{str(e)[:100]}..."