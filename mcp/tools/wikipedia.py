# mcp/tools/wikipedia.py

import requests

def search_wikipedia(args):
    """
    查询维基百科摘要，返回标题、简介和页面链接
    """
    query = args["query"]
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
    try:
        res = requests.get(url, timeout=5, headers={"User-Agent": "MCP-Agent/1.0"})
        if res.status_code == 200:
            data = res.json()
            return {
                "title": data.get("title"),
                "extract": data.get("extract"),
                "source": data.get("content_urls", {}).get("desktop", {}).get("page")
            }
        else:
            return {"error": f"未找到 {query} 的维基百科条目"}
    except Exception as e:
        return {"error": str(e), "query": query}


def register(mcp):
    """
    注册 Wikipedia 摘要插件
    """
    mcp.register_tool_function(
        name="search_wikipedia",
        description="查询一个名词的维基百科摘要内容",
        parameters={
            "query": {"type": "string", "description": "你想搜索的维基百科词条名"}
        },
        func=search_wikipedia
    )
