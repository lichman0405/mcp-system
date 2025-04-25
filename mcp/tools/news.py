# mcp/tools/news.py

import requests

def get_news_headlines(args):
    """
    获取指定主题的新闻头条（来自 CurrentsAPI）
    注意：需要提供有效的 API Key
    """
    api_key = args["__api_keys__"].get("currents_api")
    topic = args.get("topic", "technology")
    url = f"https://api.currentsapi.services/v1/latest-news?apiKey={api_key}&category={topic}"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if data.get("news"):
            return {
                "topic": topic,
                "headlines": [
                    {"title": item["title"], "url": item["url"]}
                    for item in data["news"][:5]
                ]
            }
        else:
            return {"error": "未返回新闻数据", "topic": topic}
    except Exception as e:
        return {"error": str(e), "topic": topic}


def register(mcp):
    """
    注册新闻插件（支持主题 + API Key 参数）
    """
    mcp.register_tool_function(
        name="get_news_headlines",
        description="获取指定主题的最新新闻（需要 API key）",
        parameters={
            "topic": {"type": "string", "description": "新闻主题，如 technology, health"},
            "api_key": {"type": "string", "description": "你的 CurrentsAPI 密钥"}
        },
        func=get_news_headlines
    )

if __name__ == "__main__":
    import yaml
    from pathlib import Path

    # 加载本地配置中的 API Key
    api_keys_path = Path("configs/api_keys.yaml")
    if api_keys_path.exists():
        api_keys = yaml.safe_load(api_keys_path.open())
    else:
        api_keys = {}
        print("[WARN] configs/api_keys.yaml 文件不存在，将使用空配置")

    # 虚拟 MCP 注册器（用于测试）
    class MockMCP:
        def register_tool_function(self, name, description, parameters, func):
            print(f"注册工具：{name}, 描述：{description}, 参数：{parameters}")

    mcp = MockMCP()
    register(mcp)
    # 测试获取新闻头条
    test_args = {
        "__api_keys__": api_keys,
        "topic": "technology"
    }
    result = get_news_headlines(test_args)
    print(result)