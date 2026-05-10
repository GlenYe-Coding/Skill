#!/bin/bash
set -e

echo "🚀 Skill Orchestrator - 环境初始化脚本 (Linux/macOS)"
echo "================================================"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未找到。请先安装 Python 3.7+"
    exit 1
fi
echo "✅ Python3 已就绪: $(python3 --version)"

# 安装依赖
echo ""
echo "📦 正在安装 Python 依赖..."
pip3 install jieba -q || {
    echo "⚠️  pip3 安装失败，请尝试手动安装: pip3 install jieba"
}
echo "✅ 依赖安装完成"

# 检查 npx
if ! command -v npx &> /dev/null; then
    echo ""
    echo "⚠️  npx (Node.js) 未找到。find-skills 功能将受限。"
    echo "   如需完整功能，请安装 Node.js: https://nodejs.org/"
else
    echo "✅ npx (Node.js) 已就绪"
fi

# 创建目录
echo ""
echo "📁 初始化必要目录..."
mkdir -p logs output

echo ""
echo "================================================"
echo "✅ 初始化完成！"
echo ""
echo "使用方法: python3 scripts/run.py \"你的请求\""
