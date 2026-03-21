#!/bin/bash
# Eleven-Layer AI System - 完整部署启动脚本
# 十一层架构 AI 系统 - 一键启动

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║           🏯 十一层架构 AI 系统 - 部署启动器               ║"
echo "║      Eleven-Layer Architecture AI System Launcher          ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 检查 Python
echo -e "${YELLOW}📦 检查环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 Python3${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}  ✅ Python $PYTHON_VERSION${NC}"

# 安装依赖
echo -e "${YELLOW}📦 安装依赖...${NC}"
pip3 install -q fastapi uvicorn pyyaml pydantic requests 2>/dev/null || pip3 install fastapi uvicorn pyyaml pydantic requests --user -q
echo -e "${GREEN}  ✅ 依赖已就绪${NC}"

# 检查端口
PORT=8000
echo -e "${YELLOW}🔌 检查端口 $PORT...${NC}"
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}  ⚠️  端口 $PORT 被占用，尝试关闭...${NC}"
    lsof -Pi :$PORT -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
    sleep 1
fi
echo -e "${GREEN}  ✅ 端口已就绪${NC}"

# 创建必要的目录
echo -e "${YELLOW}📁 创建目录...${NC}"
mkdir -p data/{memory,audit,evolution} static
echo -e "${GREEN}  ✅ 目录已就绪${NC}"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# 启动服务
echo -e "${YELLOW}🚀 启动 API 服务...${NC}"
echo ""

python3 api.py &
PID=$!

# 等待服务启动
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
MAX_RETRIES=30
RETRY=0

while [ $RETRY -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:$PORT/status > /dev/null 2>&1; then
        echo -e "${GREEN}  ✅ 服务启动成功！${NC}"
        break
    fi
    sleep 1
    RETRY=$((RETRY + 1))
    echo -n "."
done

if [ $RETRY -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ 服务启动超时${NC}"
    kill $PID 2>/dev/null || true
    exit 1
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                     🎉 部署成功！                          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}🌐 访问地址:${NC}"
echo -e "   ${GREEN}Web 界面:${NC} http://localhost:$PORT/static/index.html"
echo -e "   ${GREEN}API 文档:${NC} http://localhost:$PORT/docs"
echo -e "   ${GREEN}API 地址:${NC} http://localhost:$PORT"
echo ""
echo -e "${BLUE}📡 API 端点:${NC}"
echo -e "   ${YELLOW}GET${NC}  /          - 系统信息"
echo -e "   ${YELLOW}GET${NC}  /status     - 系统状态"
echo -e "   ${YELLOW}POST${NC} /chat       - 对话接口"
echo -e "   ${YELLOW}GET${NC}  /docs       - API 文档"
echo ""
echo -e "${BLUE}🧪 快速测试:${NC}"
echo -e "   curl http://localhost:$PORT/status"
echo -e "   curl -X POST http://localhost:$PORT/chat -H 'Content-Type: application/json' -d '{\"message\":\"你好\"}'"
echo ""
echo -e "${BLUE}🛑 停止服务:${NC} kill $PID"
echo ""

# 自动打开浏览器（macOS）
if command -v open &> /dev/null; then
    echo -e "${YELLOW}🌍 正在打开浏览器...${NC}"
    sleep 2
    open "http://localhost:$PORT/static/index.html"
fi

echo -e "${GREEN}按 Ctrl+C 停止服务${NC}"
echo ""

# 保持脚本运行
wait $PID
