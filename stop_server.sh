#!/bin/bash

# 养家心法选股服务停止脚本

echo "========================================="
echo "养家心法选股服务停止脚本"
echo "========================================="
echo ""

PORT=5000

# 检查端口占用
echo "[1/2] 检查端口 ${PORT} 占用情况..."
PORT_PID=$(lsof -ti:${PORT} 2>/dev/null)

if [ ! -z "$PORT_PID" ]; then
    echo "⚠️  端口 ${PORT} 被进程 $PORT_PID 占用"
    echo "正在终止进程..."
    kill -9 $PORT_PID 2>/dev/null
    sleep 1

    # 再次检查
    PORT_PID=$(lsof -ti:${PORT} 2>/dev/null)
    if [ ! -z "$PORT_PID" ]; then
        echo "❌ 无法释放端口 ${PORT}"
        exit 1
    else
        echo "✅ 端口 ${PORT} 已释放"
    fi
else
    echo "✅ 端口 ${PORT} 无占用"
fi

# 检查Python进程
echo ""
echo "[2/2] 检查Python进程..."
OLD_PIDS=$(ps aux | grep "python.*stock_service" | grep -v grep | awk '{print $2}')

if [ ! -z "$OLD_PIDS" ]; then
    echo "⚠️  发现进程: $OLD_PIDS"
    echo "正在终止进程..."
    echo $OLD_PIDS | xargs kill -9 2>/dev/null
    sleep 1
    echo "✅ 进程已终止"
else
    echo "✅ 无相关进程"
fi

echo ""
echo "========================================="
echo "🛑 服务已停止"
echo "========================================="
