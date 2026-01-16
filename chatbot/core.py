# -*- coding: utf-8 -*-
import dashscope
from dashscope import Generation
from typing import List, Dict

dashscope.api_key = "sk-352ac2c447984745ad305c07ee3d169a"

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

def ask_qwen_with_tools(messages: List[Dict[str, str]]) -> str:
    """发送带工具说明的消息，并处理工具调用"""
    # 在系统消息中加入工具说明
    system_msg = {"role": "system", "content": TOOL_DESCRIPTIONS}
    full_messages = [system_msg] + messages
    
    response = Generation.call(
        model="qwen-max",
        messages=full_messages
    )
    raw_answer = response.output.text
    
    # 检查是否需要调用工具
    if raw_answer.startswith("TOOL:"):
        parts = raw_answer.split("|", 1)
        tool_name = parts[0].replace("TOOL: ", "").strip()
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