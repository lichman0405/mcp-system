# -*- coding: utf-8 -*-
# The code is licensed under the MIT License (MIT).
# Author: Shibo Li
# Date: 2025-04-25


import yaml
from pathlib import Path

class ModelRouter:
    """
    从配置文件中加载多模型分发策略
    """

    def __init__(self, config_path="configs/router.yaml"):
        # 默认模型映射
        self.routes = {
            "intent_decision": "deepseek-reasoner",
            "tool_decision": "deepseek-reasoner",
            "final_response": "deepseek-chat"
        }

        # 如果存在 config 文件，则加载并覆盖默认设置
        path = Path(config_path)
        if path.exists():
            self.routes.update(yaml.safe_load(path.open()))

    def get_model_for(self, task: str):
        """
        获取指定任务应该使用的模型
        例如 task = "tool_decision" → 返回 deepseek-chat
        """
        return self.routes.get(task, "deepseek-chat")

if __name__ == "__main__":
    # 测试 ModelRouter
    router = ModelRouter()
    print(router.get_model_for("tool_decision"))  # 输出: deepseek-chat
    print(router.get_model_for("unknown_task"))   # 输出: deepseek-chat