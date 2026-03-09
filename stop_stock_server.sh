#!/bin/bash
# 股票分析系统停止脚本

echo "🛑 停止股票分析服务器..."
echo ""

# 查找并终止进程
PIDS=$(pgrep -f "python3 stock_server_v2.py")

if [ -n "$PIDS" ]; then
    echo "找到进程: $PIDS"
    kill $PIDS

    sleep 2

    # 检查是否还有残留进程
    if pgrep -f "python3 stock_server_v2.py" > /dev/null; then
        echo "⚠️  进程未完全停止，强制终止..."
        pkill -9 -f "python3 stock_server_v2.py"
    fi

    echo "✅ 服务器已停止"
else
    echo "ℹ️  服务器未在运行"
fi

echo ""
