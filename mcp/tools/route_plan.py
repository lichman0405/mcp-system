# mcp/tools/route_plan.py

import requests
from mcp.tools import geocode

def route_plan(args):
    """
    查询公交路线（高德 API），需要指定 origin, destination 和 city。
    """
    origin_text = args.get("origin", "")
    destination = args.get("destination", "")
    city = args.get("city", "")
    api_keys = args.get("__api_keys__", {})
    amap_key = api_keys.get("amap", "")

    if not all([origin_text, destination, city]):
        return {"error": "必须提供 origin、destination 和 city 参数"}

    # 地理编码 origin
    origin_result = geocode.geo_search({
        "location": f"{city} {origin_text}",
        "__api_keys__": api_keys
    })

    if "latitude" not in origin_result:
        return {"error": f"起点解析失败: {origin_result.get('error')}"}

    from_coords = f"{origin_result['longitude']},{origin_result['latitude']}"

    # 地理编码 destination
    dst_result = geocode.geo_search({
        "location": f"{city} {destination}",
        "__api_keys__": api_keys
    })

    if "latitude" not in dst_result:
        return {"error": f"终点解析失败: {dst_result.get('error')}"}

    to_coords = f"{dst_result['longitude']},{dst_result['latitude']}"

    # 请求高德公交路线 API
    url = (
        f"https://restapi.amap.com/v3/direction/transit/integrated"
        f"?origin={from_coords}&destination={to_coords}&city={city}&key={amap_key}"
    )

    try:
        res = requests.get(url, timeout=8)
        data = res.json()

        if data.get("status") != "1" or not data.get("route", {}).get("transits"):
            return {"error": "高德未返回有效公交路径", "raw": data}

        best_route = data["route"]["transits"][0]
        steps = []
        for seg in best_route["segments"]:
            if "bus" in seg and seg["bus"]["buslines"]:
                line = seg["bus"]["buslines"][0]
                steps.append(f"{line['name']}（{line['departure_stop']['name']} ➜ {line['arrival_stop']['name']}）")

        return {
            "origin": origin_result.get("formatted"),
            "destination": dst_result.get("formatted"),
            "city": city,
            "duration_min": round(int(best_route["duration"]) / 60, 1),
            "distance_km": round(int(best_route["distance"]) / 1000, 2),
            "segments": steps
        }

    except Exception as e:
        return {"error": str(e)}

def register(mcp):
    mcp.register_tool_function(
        name="route_plan",
        description="查询公交路线（高德地图），需提供出发地、目的地和城市",
        parameters={
            "origin": {"type": "string", "description": "出发地名称，如 '望京'"},
            "destination": {"type": "string", "description": "目的地名称，如 '颐和园'"},
            "city": {"type": "string", "description": "城市名称，如 '北京'"}
        },
        func=route_plan
    )

# 可选测试代码
if __name__ == "__main__":
    import yaml
    from pathlib import Path
    from mcp.tools import geocode

    api_keys = yaml.safe_load(open("configs/api_keys.yaml"))

    class MockMCP:
        def register_tool_function(self, name, description, parameters, func):
            print(f"注册工具函数: {name}, 描述: {description}")

    mcp = MockMCP()
    register(mcp)

    result = route_plan({
        "origin": "望京",
        "destination": "颐和园",
        "city": "北京",
        "__api_keys__": api_keys
    })

    print("公交路线规划结果：", result)
