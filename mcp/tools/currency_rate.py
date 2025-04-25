# mcp/tools/currency_rate.py

import requests

def currency_rate(args):
    """
    使用 Frankfurter 免费 API 查询两种货币之间的汇率
    示例：USD → CNY
    """
    base = args.get("base", "USD").upper()
    target = args.get("target", "CNY").upper()

    url = f"https://api.frankfurter.app/latest?from={base}&to={target}"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()

        rate = data.get("rates", {}).get(target)
        if rate:
            return {
                "base": base,
                "target": target,
                "rate": rate,
                "date": data.get("date")
            }
        else:
            return {"error": f"未找到 {target} 汇率", "base": base}
    except Exception as e:
        return {"error": str(e), "base": base}


def register(mcp):
    mcp.register_tool_function(
        name="currency_rate",
        description="查询两个币种之间的汇率（使用 Frankfurter 免费 API）",
        parameters={
            "base": {"type": "string", "description": "基础币种，如 USD"},
            "target": {"type": "string", "description": "目标币种，如 CNY"}
        },
        func=currency_rate
    )


# 可选测试代码
if __name__ == "__main__":
    class MockMCP:
        def register_tool_function(self, name, description, parameters, func):
            print(f"注册工具函数: {name}, 描述: {description}, 参数: {parameters}")

    mcp = MockMCP()
    register(mcp)
    result = currency_rate({
        "base": "USD",
        "target": "CNY"
    })
    print("调用结果：", result)
