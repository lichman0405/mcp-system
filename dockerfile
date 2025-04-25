# 使用轻量级 Python 镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 拷贝依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝整个项目代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动 FastAPI 服务
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
