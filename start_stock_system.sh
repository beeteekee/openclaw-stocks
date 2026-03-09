#!/bin/bash
# 股票分析系统启动脚本

echo "╔══════════════════════════════════════════════════╗"
echo "║      🚀 股票分析系统 - 养家心法                    ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# 检查是否已经运行
if pgrep -f "python3 stock_server_v2.py" > /dev/null; then
    echo "✅ 服务器已经在运行中"
    echo ""
    echo "访问地址："
    echo "  📱 本地: http://localhost:5001"
    echo "  🌐 外网: http://192.168.0.105:5001"
    echo ""
    echo "如需停止服务器，运行: ./stop_stock_server.sh"
    echo ""
else
    # 启动服务器
    echo "🚀 启动服务器..."
    echo ""

    cd /Users/likan/.openclaw/workspace
    nohup python3 stock_server_v2.py > stock_server.log 2>&1 &

    sleep 5

    # 检查是否成功启动
    if pgrep -f "python3 stock_server_v2.py" > /dev/null; then
        echo "✅ 服务器启动成功！"
        echo ""
        echo "访问地址："
        echo "  📱 本地: http://localhost:5001"
        echo "  🌐 外网: http://192.168.0.105:5001"
        echo ""
        echo "日志文件: stock_server.log"
        echo ""
        echo "正在打开浏览器..."
        sleep 1
        open http://localhost:5001
        echo ""
        echo "💡 提示:"
        echo "  - 使用Ctrl+C停止服务器"
        echo "  - 或运行: ./stop_stock_server.sh"
        echo ""
    else
        echo "❌ 服务器启动失败，请查看日志: stock_server.log"
        echo ""
        exit 1
    fi
fi
