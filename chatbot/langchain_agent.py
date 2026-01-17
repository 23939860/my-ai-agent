import requests  # ← 这行加在文件顶部（已有就不用加）

# 在文件顶部已有的 import 下面添加（如果还没有）
# 注意：确保 'requests' 在 requirements.txt 中

@tool
def get_weather(city: str) -> str:
    """查询城市实时天气（使用 Open-Meteo 免费 API）"""
    city = city.strip()
    
    # 城市坐标映射（可继续添加）
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
        
        # 天气代码简化解释
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
    except Exception as e:
        return f"获取天气失败，请稍后再试"