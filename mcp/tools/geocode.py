# mcp/tools/geocode.py

import requests

def geo_search(args):
    """
    使用 OpenCage API 将地址转换为经纬度坐标
    """
    query = args.get("location", "")
    api_keys = args.get("__api_keys__", {})
    api_key = api_keys.get("opencage", "")

    url = f"https://api.opencagedata.com/geocode/v1/json?q={query}&key={api_key}&limit=1"

    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if data["results"]:
            result = data["results"][0]
            return {
                "input": query,
                "formatted": result["formatted"],
                "latitude": result["geometry"]["lat"],
                "longitude": result["geometry"]["lng"],
                "components": result["components"]
            }
        else:
            return {"error": "未找到地址信息", "input": query}
    except Exception as e:
        return {"error": str(e), "input": query}


def register(mcp):
    mcp.register_tool_function(
        name="geo_search",
        description="将地址文本转换为经纬度（使用 OpenCage API）",
        parameters={
            "location": {"type": "string", "description": "地址名称，如 '天安门' 或 '1600 Amphitheatre Parkway'"}
        },
        func=geo_search
    )


# 可选测试
if __name__ == "__main__":
    import yaml
    from pathlib import Path

    api_keys_path = Path("configs/api_keys.yaml")
    api_keys = yaml.safe_load(api_keys_path.open()) if api_keys_path.exists() else {}

    class MockMCP:
        def register_tool_function(self, name, description, parameters, func):
            print(f"注册工具函数: {name}, 描述: {description}, 参数: {parameters}")

    mcp = MockMCP()
    register(mcp)

    result = geo_search({
        "location": "天安门",
        "__api_keys__": api_keys
    })
    print("调用结果：", result)
