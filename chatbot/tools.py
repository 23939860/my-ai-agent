# -*- coding: utf-8 -*-
import requests
from datetime import datetime
import re

def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate_expression(expr: str) -> str:
    expr = expr.strip()
    if not re.match(r'^[\d\s+\-*/().%^]+$', expr):
        return "❌ 表达式包含非法字符"
    try:
        expr = expr.replace('^', '**')
        result = eval(expr, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"❌ 计算错误: {str(e)}"

def get_weather(location: str) -> str:
    city_coords = {
        "北京": (39.9042, 116.4074),
        "上海": (31.2304, 121.4737),
        "广州": (23.1291, 113.2644),
        "深圳": (22.3193, 114.1694),
        "杭州": (30.2741, 120.1551),
        "new york": (40.7128, -74.0060),
        "london": (51.5074, -0.1278),
        "tokyo": (35.6895, 139.6917),
    }
    
    city = location.lower()
    if location in city_coords:
        lat, lon = city_coords[location]
    elif city in city_coords:
        lat, lon = city_coords[city]
    else:
        return f"❌ 暂不支持 '{location}' 的天气查询。支持城市：北京、上海、广州、深圳、杭州、New York、London、Tokyo"

    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
        response = requests.get(url, timeout=5)
        data = response.json()
        temp = data['current']['temperature_2m']
        return f"📍 {location} 当前温度: {temp}°C"
    except Exception as e:
        return f"❌ 天气查询失败: {str(e)}"
