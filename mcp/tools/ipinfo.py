# mcp/tools/ipinfo.py

import requests

def get_ip_location(args):
    """
    使用 ipinfo.io 获取当前设备的 IP 地理位置
    """
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5)
        data = res.json()
        return {
            "ip": data.get("ip"),
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "org": data.get("org")
        }
    except Exception as e:
        return {"error": str(e)}


def register(mcp):
    """
    注册 IP 定位插件（不需参数）
    """
    mcp.register_tool_function(
        name="get_ip_location",
        description="获取当前设备的 IP 所在地信息",
        parameters={},
        func=get_ip_location
    )
