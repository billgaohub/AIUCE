#!/bin/bash
# Eleven-Layer AI System - 一键启动脚本
# 十一层架构 AI 系统启动器

echo "🏯 十一层架构 AI 系统启动器"
echo "=============================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
pip3 show fastapi uvicorn pyyaml pydantic &> /dev/null
if [ $? -ne 0 ]; then
    echo "  安装依赖..."
    pip3 install fastapi uvicorn pyyaml pydantic -q
fi
echo "  ✅ 依赖已就绪"
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 检查端口
PORT=8000
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口 $PORT 已被占用，尝试关闭旧进程..."
    lsof -Pi :$PORT -sTCP:LISTEN -t | xargs kill -9 2>/dev/null
    sleep 1
fi

echo "🚀 启动 API 服务..."
echo "  地址: http://localhost:$PORT"
echo "  文档: http://localhost:$PORT/docs"
echo ""

# 启动服务
python3 api.py &
PID=$!

# 等待服务启动
sleep 3

# 检查服务是否成功启动
if curl -s http://localhost:$PORT/ > /dev/null; then
    echo "✅ 服务启动成功！"
    echo ""
    echo "=============================="
    echo "🌐 访问地址:"
    echo "   API:    http://localhost:$PORT"
    echo "   文档:   http://localhost:$PORT/docs"
    echo "=============================="
    echo ""
    echo "📋 快速测试:"
    echo "   curl http://localhost:$PORT/status"
    echo ""
    echo "🛑 停止服务: kill $PID"
    echo ""
    
    # 自动打开浏览器（macOS）
    if command -v open &> /dev/null; then
        echo "🌍 正在打开浏览器..."
        sleep 1
        open "http://localhost:$PORT/docs"
    fi
    
    # 保持脚本运行
    wait $PID
else
    echo "❌ 服务启动失败"
    kill $PID 2>/dev/null
    exit 1
fi
