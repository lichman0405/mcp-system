# mcp/tools/weather.py

import requests

def get_weather(args):
    """
    查询城市天气：使用 wttr.in 提供的简易 JSON 接口
    """
    city = args["city"]
    url = f"https://wttr.in/{city}?format=j1"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        current = data["current_condition"][0]
        return {
            "location": city,
            "temperature_C": current["temp_C"],
            "humidity": current["humidity"],
            "weather": current["weatherDesc"][0]["value"]
        }
    except Exception as e:
        return {"error": str(e), "location": city}


def register(mcp):
    """
    注册天气插件到 MCP
    """
    mcp.register_tool_function(
        name="get_weather",
        description="获取指定城市的实时天气信息",
        parameters={
            "city": {"type": "string", "description": "城市名称，如北京、上海"}
        },
        func=get_weather
    )
