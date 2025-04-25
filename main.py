# tests/test_run.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp.context import MCPContext
from mcp.registry import register_all_plugins


# ==== 配置你的 OpenAI Key 和 Base URL（可接 deepseek） ====
OPENAI_API_KEY = "sk-72c0da4afef44d3ea74cfffc36162f47"
BASE_URL = "https://api.deepseek.com/v1"  # 或 https://api.openai.com/v1


def setup_mcp():
    mcp = MCPContext(api_key=OPENAI_API_KEY, base_url=BASE_URL)

    # 注册工具函数（plugin）
    register_all_plugins(mcp)

    # 注册记忆模块
    mcp.register_module(
        "memory",
        lambda: "\n".join(mcp.memory.get_recent(5)),
        priority=2,
        description="记录用户最近的说话内容"
    )

    # 注册记忆更新 Hook
    mcp.register_hook(lambda user_input, modules: mcp.memory.add(f"用户说过：{user_input}"))

    return mcp

def run_cli():
    print("🧠 MCP 模拟对话启动！输入 'exit' 退出\n")
    mcp = setup_mcp()

    while True:
        user_input = input("👤 请问我问题：")
        if user_input.strip().lower() in {"exit", "quit"}:
            break

        prompt = mcp.build_prompt(user_input)
        print("\n=== 最终生成的 Prompt ===\n")
        print(prompt)
        print("\n----------------------------\n")

if __name__ == "__main__":
    run_cli()
