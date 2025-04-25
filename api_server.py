# api_server.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import yaml
from pathlib import Path
import os

from mcp.context import MCPContext
from mcp.registry import register_all_tools

# === 配置加载 ===
api_key_file = Path("configs/api_keys.yaml")
api_keys = yaml.safe_load(api_key_file.open()) if api_key_file.exists() else {}

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", api_keys.get("deepseek", "sk-..."))
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", api_keys.get("openai_base_url", "https://api.deepseek.com/v1"))

# === 初始化 MCP 系统 ===
mcp = MCPContext(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
register_all_tools(mcp)

# === 初始化 FastAPI 应用 ===
app = FastAPI(title="MCP Chat API")

# 允许所有跨域（适用于前端测试）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 接口模型 ===
class ChatRequest(BaseModel):
    user_input: str

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    result = mcp.build_prompt(req.user_input)
    return {
        "response": result
    }

# === 启动 ===
if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
