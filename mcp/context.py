# -*- coding: utf-8 -*-
# The code is licensed under the MIT License (MIT).
# Author: Shibo Li
# Date: 2025-04-25
# 该文件包含 MCPContext 类的实现
# 该类用于管理上下文模块、工具函数和用户输入的处理
# 以及与 OpenAI API 的交互
# 该类的主要功能包括：
# 1. 注册模块和工具函数
# 2. 处理用户输入和工具调用
# 3. 构建和生成最终的上下文内容
# 4. 估算 token 数量
# 5. 处理模块的优先级和依赖关系
# 6. 处理函数调用的响应
# 7. 生成最终的上下文内容

# mcp/context.py

from openai import OpenAI
from mcp.model_router import ModelRouter
from mcp.memory import MemoryStore
import json
import yaml
from pathlib import Path

def estimate_tokens(text: str) -> int:
    return len(text) // 4  # 简化估算

class MCPContext:
    def __init__(self, api_key, base_url, max_token_limit=1500):
        self.modules = {}
        self.update_hooks = []
        self.tools = {}
        self.max_token_limit = max_token_limit
        self.current_user_input = ""

        # 初始化模型客户端和调度器
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.router = ModelRouter()
        self.memory = MemoryStore()

        # ✅ 加载所有 API key 配置
        api_key_path = Path("configs/api_keys.yaml")
        if api_key_path.exists():
            with open(api_key_path, "r") as f:
                self.api_keys = yaml.safe_load(f)
        else:
            self.api_keys = {}
            print("[WARN] 未找到 configs/api_keys.yaml，api_keys 默认为空")

    def register_module(self, name, content_fn, priority=1, deps=None, description=""):
        self.modules[name] = {
            "fn": content_fn,
            "priority": priority,
            "deps": deps or [],
            "description": description
        }

    def register_hook(self, hook_fn):
        self.update_hooks.append(hook_fn)

    def register_tool_function(self, name, description, parameters, func=None):
        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "func": func
        }
        self.register_module(
            "tools",
            content_fn=lambda: {
                "available_functions": [
                    {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["parameters"]
                    } for t in self.tools.values()
                ]
            },
            priority=3,
            description="GPT 可调用的函数列表"
        )

    def _format_content(self, name, content):
        if isinstance(content, dict):
            return json.dumps({name: content}, indent=2, ensure_ascii=False)
        else:
            return f"[{name.upper()}]\n{content}"

    def update_context(self, user_input):
        for hook in self.update_hooks:
            hook(user_input, self.modules)

    def handle_tool_call(self, tool_call_obj):
        name = tool_call_obj.name
        arguments = tool_call_obj.arguments or {}
        if isinstance(arguments, str):
            arguments = json.loads(arguments)

        tool = self.tools.get(name)
        if tool and tool.get("func"):
            # ✅ 将 api_keys 注入到参数中（方便插件使用）
            arguments["__api_keys__"] = self.api_keys

            result = tool["func"](arguments)
            print(f"[TOOL] 执行函数：{name}，参数：{arguments}")
            self.register_module(
                f"tool_result_{name}",
                content_fn=lambda result=result: result,
                priority=4,
                description=f"函数 {name} 的调用结果"
            )

    def build_prompt(self, user_input):
        self.current_user_input = user_input
        self.memory.add(f"用户说过：{user_input}")
        self.update_context(user_input)

        # === STEP 1: 模块调度 ===
        module_descriptions = {k: v["description"] for k, v in self.modules.items()}
        system_prompt = "你是模块调度器，请根据用户输入和模块描述返回要激活的模块名数组（JSON）"
        modules_text = "\n".join([f"- {k}: {v}" for k, v in module_descriptions.items()])
        user_prompt = f"输入：{user_input}\n模块描述：\n{modules_text}"

        model = self.router.get_model_for("intent_decision")
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )
        content = response.choices[0].message.content.strip()

        try:
            active_module_names = json.loads(content)
        except:
            active_module_names = list(self.modules.keys())

        module_data = []
        for name, data in self.modules.items():
            if name in active_module_names:
                content = data["fn"]()
                tokens = estimate_tokens(str(content))
                module_data.append({
                    "name": name,
                    "priority": data["priority"],
                    "tokens": tokens,
                    "deps": data["deps"],
                    "content": content
                })

        context_text = "\n\n".join(self._format_content(m["name"], m["content"]) for m in module_data)
        full_prompt = f"{context_text}\n\n[USER]\n{user_input}"

        # === STEP 2: 函数调用判断 ===
        model = self.router.get_model_for("tool_decision")
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个可以调用工具的 AI"},
                {"role": "user", "content": full_prompt}
            ],
            tools=[{
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": {
                        "type": "object",
                        "properties": t["parameters"],
                        "required": list(t["parameters"].keys())
                    }
                }
            } for t in self.tools.values()],
            tool_choice="auto"
        )

        choice = response.choices[0]
        if choice.message.tool_calls:
            for tool_call in choice.message.tool_calls:
                self.handle_tool_call(tool_call.function)

        return self.generate_context() + f"\n\n[USER]\n{user_input}"

    def generate_context(self):
        module_data = []
        for name, data in self.modules.items():
            content = data["fn"]()
            tokens = estimate_tokens(str(content))
            module_data.append({
                "name": name,
                "priority": data["priority"],
                "tokens": tokens,
                "deps": data["deps"],
                "content": content
            })

        module_data.sort(key=lambda x: -x["priority"])
        selected = set()
        used_tokens = 0

        for m in module_data:
            if used_tokens + m["tokens"] <= self.max_token_limit:
                selected.add(m["name"])
                used_tokens += m["tokens"]

        final_modules = [m for m in module_data if m["name"] in selected]
        return "\n\n".join(self._format_content(m["name"], m["content"]) for m in final_modules)
