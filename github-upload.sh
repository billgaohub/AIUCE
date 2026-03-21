#!/bin/bash
# GitHub 仓库创建和上传脚本
# 为 billgaohub/eleven-layer-ai 创建仓库

set -e

cd /Users/bill/Downloads/Qclaw_Dropzone/eleven_layer_ai

echo "🏯 十一层架构 AI 系统 - GitHub 上传脚本"
echo "======================================"
echo ""
echo "GitHub 用户名: billgaohub"
echo "仓库名称: eleven-layer-ai"
echo "仓库类型: Public"
echo ""

# 检查 Git
if ! command -v git &> /dev/null; then
    echo "❌ 错误: 未安装 Git"
    exit 1
fi

echo "✅ Git 已安装"

# 初始化 Git 仓库
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 仓库..."
    git init
else
    echo "📦 Git 仓库已存在"
fi

# 配置 Git（如果未配置）
if ! git config user.email &> /dev/null; then
    git config user.email "bill@example.com"
    git config user.name "Bill Gao"
fi

# 创建 .gitignore（如果不存在）
if [ ! -f ".gitignore" ]; then
    echo "📝 创建 .gitignore..."
    cat > .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Data and logs (keep structure, ignore content)
data/memory/*.json
data/audit/*.json
data/evolution/*.json
logs/
*.log

# Secrets
.env
.env.local
*.key
*.pem
secrets.yaml

# Test coverage
.coverage
htmlcov/
.pytest_cache/

# MyPy
.mypy_cache/

# Jupyter
.ipynb_checkpoints/

# Model files
*.pkl
*.pth
*.bin
*.safetensors
models/
GITIGNORE
fi

echo ""
echo "======================================"
echo "📤 准备上传文件"
echo "======================================"
echo ""

# 添加文件
echo "➕ 添加文件到 Git..."
git add .

# 检查是否有变更
if git diff --cached --quiet; then
    echo "ℹ️  没有新的变更需要提交"
else
    echo "💾 提交变更..."
    git commit -m "Initial commit: Eleven-Layer Architecture AI System

🏯 十一层架构 AI 系统

基于中国古代官僚体系设计的分层 AI 架构：
- L0 意志层 (秦始皇) - 最高宪法
- L1 身份层 (诸葛亮) - 人设边界
- L2 感知层 (魏征) - 现实对账
- L3 推理层 (张良) - 多路径推演
- L4 记忆层 (司马迁) - 语义索引
- L5 决策层 (包拯) - 审计存证
- L6 经验层 (曾国藩) - 复盘机制
- L7 演化层 (商鞅) - 内核重构
- L8 接口层 (张骞) - 算力外交
- L9 代理层 (韩信) - 跨设备执行
- L10 沙盒层 (庄子) - 影子模拟

特性：
- FastAPI 后端服务
- Web 可视化界面
- 完整的 API 文档
- Docker 支持"
fi

echo ""
echo "======================================"
echo "🔗 关联远程仓库"
echo "======================================"
echo ""

# 检查远程仓库
if git remote get-url origin &> /dev/null; then
    echo "📝 更新远程仓库地址..."
    git remote set-url origin https://github.com/billgaohub/eleven-layer-ai.git
else
    echo "📝 添加远程仓库..."
    git remote add origin https://github.com/billgaohub/eleven-layer-ai.git
fi

echo "✅ 远程仓库已配置: https://github.com/billgaohub/eleven-layer-ai"

echo ""
echo "======================================"
echo "🚀 推送到 GitHub"
echo "======================================"
echo ""

# 检查分支
BRANCH=$(git branch --show-current)
if [ -z "$BRANCH" ]; then
    git branch -m main
    BRANCH="main"
fi

echo "📋 当前分支: $BRANCH"
echo ""
echo "⚠️  注意：如果这是首次推送，你可能需要在浏览器中登录 GitHub 授权"
echo ""

# 推送
echo "⬆️  正在推送..."
if git push -u origin $BRANCH 2>&1; then
    echo ""
    echo "======================================"
    echo "🎉 上传成功！"
    echo "======================================"
    echo ""
    echo "📎 仓库地址:"
    echo "   https://github.com/billgaohub/eleven-layer-ai"
    echo ""
    echo "🌐 访问链接:"
    echo "   代码:     https://github.com/billgaohub/eleven-layer-ai"
    echo "   下载:     https://github.com/billgaohub/eleven-layer-ai/archive/refs/heads/main.zip"
    echo ""
else
    echo ""
    echo "======================================"
    echo "❌ 推送失败"
    echo "======================================"
    echo ""
    echo "可能的原因:"
    echo "1. 仓库 https://github.com/billgaohub/eleven-layer-ai 不存在"
    echo "2. 需要登录 GitHub 授权"
    echo "3. 网络连接问题"
    echo ""
    echo "解决方案:"
    echo "1. 在浏览器中访问 https://github.com/new 创建仓库"
    echo "   - Repository name: eleven-layer-ai"
    echo "   - 选择 Public"
    echo "   - 不要勾选 README"
    echo ""
    echo "2. 或者运行以下命令手动推送:"
    echo "   cd /Users/bill/Downloads/Qclaw_Dropzone/eleven_layer_ai"
    echo "   git push -u origin main"
    echo ""
fi
