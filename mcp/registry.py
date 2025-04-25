# -*- coding: utf-8 -*-
# The code is licensed under the MIT License (MIT).
# Author: Shibo Li
# Date: 2025-04-25


import importlib
import pkgutil
import mcp.tools as tool_pkg  # 👈 关键：这是 Python 包，不是上下文对象

def register_all_tools(mcp):
    """
    自动注册 mcp.tools 目录下的所有插件模块（包含 register(mcp) 方法）
    """
    for _, name, is_pkg in pkgutil.iter_modules(tool_pkg.__path__, tool_pkg.__name__ + "."):
        if is_pkg:
            continue
        try:
            module = importlib.import_module(name)
            if hasattr(module, "register"):
                module.register(mcp)
                print(f"[PLUGIN] 已加载插件：{name.split('.')[-1]}")
        except Exception as e:
            print(f"[ERROR] 加载插件失败：{name} -> {e}")
