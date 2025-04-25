# -*- coding: utf-8 -*-
# The code is licensed under the MIT License (MIT).
# Author: Shibo Li
# Date: 2025-04-25

class MemoryStore:
    def __init__(self):
        self.entries = []

    def add(self, summary: str):
        """添加一条摘要到记忆中"""
        self.entries.append(summary)

    def get_recent(self, max_entries=5):
        """返回最近的 N 条记忆"""
        return self.entries[-max_entries:]
