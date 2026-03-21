# Eleven-Layer AI System Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . /app/

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装项目
RUN pip install --no-cache-dir -e .

# 创建数据目录
RUN mkdir -p /app/data/{memory,audit,evolution}

# 暴露端口（如果需要API服务）
EXPOSE 8000

# 默认命令
CMD ["python3", "-c", "from eleven_layer_ai import create_system; s = create_system(); print(s.chat('系统启动完成'))"]
