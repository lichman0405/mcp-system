# mcp/tools/stock_quote.py

import requests

def stock_quote(args):
    symbol = args.get("symbol", "AAPL").upper()
    api_keys = args.get("__api_keys__", {})
    api_key = api_keys.get("twelve_data", "")

    url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={api_key}"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        print("原始 API 返回：", data)

        if "close" in data:
            return {
                "symbol": symbol,
                "name": data.get("name"),
                "exchange": data.get("exchange"),
                "price": data.get("close"),  # 作为当前价格
                "change": data.get("change"),
                "percent_change": data.get("percent_change"),
                "open": data.get("open"),
                "previous_close": data.get("previous_close"),
                "volume": data.get("volume"),
                "date": data.get("datetime"),
                "is_market_open": data.get("is_market_open")
            }
        else:
            return {"error": data.get("message", "接口返回错误"), "symbol": symbol, "raw": data}
    except Exception as e:
        return {"error": str(e), "symbol": symbol}



def register(mcp):
    mcp.register_tool_function(
        name="stock_quote",
        description="获取指定股票的最新行情（需 Twelve Data API key）",
        parameters={
            "symbol": {"type": "string", "description": "股票代码，如 AAPL, TSLA, BABA"}
        },
        func=stock_quote
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
            print(f"注册工具函数: {name}, 描述: {description}, 参数: {parameters}")

    mcp = MockMCP()
    register(mcp)

    # 调用测试函数
    result = stock_quote({
        "symbol": "AAPL",
        "__api_keys__": api_keys
    })
    print("调用结果：", result)

