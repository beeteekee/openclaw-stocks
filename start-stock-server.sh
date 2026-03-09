#!/bin/bash

# 股票分析页面服务器启动脚本

echo "🚀 启动股票分析页面服务器..."
echo ""
echo "📄 页面文件：$(pwd)/stock-analysis-http.html"
echo "🌐 服务地址："
echo "   - http://localhost:8080"
echo ""
echo "⚠️  注意：如果 80 端口被占用，会自动使用 8000 端口"
echo ""
echo "📝 按 Ctrl+C 停止服务器"
echo ""

cd "$(dirname "$0")"
python3 -m http.server 8080
