#!/bin/bash
# AIUCE 系统 - GitHub 仓库创建脚本
# 需要先手动在 GitHub 创建 aiuce 仓库

echo "🏯 AIUCE System - GitHub 上传"
echo "=============================="
echo ""
echo "请先在 GitHub 创建仓库:"
echo "  1. 访问 https://github.com/new"
echo "  2. Repository name: aiuce"
echo "  3. Description: AIUCE - AI Universe Constitution Evolution System"
echo "  4. 选择 Public"
echo "  5. 不要勾选 README、.gitignore、License"
echo "  6. 点击 Create repository"
echo ""
read -p "创建完成后按 Enter 继续..."

cd /Users/bill/Downloads/Qclaw_Dropzone/aiuce

echo ""
echo "📤 推送到 GitHub..."
git push -u origin main

echo ""
echo "✅ 完成！"
echo "仓库地址: https://github.com/billgaohub/aiuce"
