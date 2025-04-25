# tests/test_run.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp.context import MCPContext
from mcp.registry import register_all_plugins


# ==== 配置你的 OpenAI Key 和 Base URL（可接 deepseek） ====
OPENAI_API_KEY = "sk-72c0da4afef44d3ea74cfffc36162f47"
BASE_URL = "https://api.deepseek.com/v1"  # 或 https://api.openai.com/v1

def main():
    # 初始化 MCP 实例
    mcp = MCPContext(api_key=OPENAI_API_KEY, base_url=BASE_URL)

    # 注册工具插件（自动扫描 tools 目录）
    register_all_plugins(mcp)

    # 注册 Memory 模块
    mcp.register_module(
        "memory",
        lambda: "\n".join(mcp.memory.get_recent(5)),
        priority=2,
        description="记录用户最近的说话内容"
    )

    # 注册记忆更新 Hook
    mcp.register_hook(lambda user_input, modules: mcp.memory.add(f"用户说过：{user_input}"))

    # 模拟一次用户输入
    user_input = "帮我查下北京的天气，然后告诉我它的维基百科简介"

    # 构建 prompt（同时触发函数调用）
    final_prompt = mcp.build_prompt(user_input)

    print("\n========== 最终 Prompt ==========\n")
    print(final_prompt)

if __name__ == "__main__":
    main()
