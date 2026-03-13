#!/bin/bash

# 养家心法选股服务启动脚本
# 端口：5000

echo "========================================="
echo "养家心法选股服务启动脚本"
echo "========================================="
echo ""

PORT=5000
LOG_FILE="logs/server.log"

# 检查端口占用
echo "[1/4] 检查端口 ${PORT} 占用情况..."
PORT_PID=$(lsof -ti:${PORT} 2>/dev/null)

if [ ! -z "$PORT_PID" ]; then
    echo "⚠️  端口 ${PORT} 被进程 $PORT_PID 占用"
    echo "正在终止旧进程..."
    kill -9 $PORT_PID 2>/dev/null
    sleep 2

    # 再次检查
    PORT_PID=$(lsof -ti:${PORT} 2>/dev/null)
    if [ ! -z "$PORT_PID" ]; then
        echo "❌ 无法释放端口 ${PORT}，请手动检查"
        echo "   运行: lsof -i:${PORT}"
        exit 1
    else
        echo "✅ 端口 ${PORT} 已释放"
    fi
else
    echo "✅ 端口 ${PORT} 可用"
fi

echo ""
echo "[2/4] 检查Python进程..."
# 查找所有stock_service进程
OLD_PIDS=$(ps aux | grep "python.*stock_service" | grep -v grep | awk '{print $2}')

if [ ! -z "$OLD_PIDS" ]; then
    echo "⚠️  发现旧进程: $OLD_PIDS"
    echo "正在终止旧进程..."
    echo $OLD_PIDS | xargs kill -9 2>/dev/null
    sleep 1
    echo "✅ 旧进程已终止"
else
    echo "✅ 无旧进程"
fi

echo ""
echo "[3/4] 启动Flask服务..."
# 创建日志目录
mkdir -p logs

# 启动服务（后台运行）
nohup python3 stock_service.py > $LOG_FILE 2>&1 &
NEW_PID=$!

echo "✅ 服务已启动，PID: $NEW_PID"
echo "   端口: ${PORT}"
echo "   日志: $LOG_FILE"

echo ""
echo "[4/4] 验证服务状态..."
sleep 3

# 检查进程是否还在运行
if ps -p $NEW_PID > /dev/null 2>&1; then
    echo "✅ 进程运行中"
else
    echo "❌ 进程已退出，请检查日志"
    tail -20 $LOG_FILE
    exit 1
fi

# 测试健康检查端点
if curl -s "http://localhost:${PORT}/api/health" > /dev/null; then
    echo "✅ 健康检查通过"
else
    echo "❌ 健康检查失败"
    tail -20 $LOG_FILE
    exit 1
fi

echo ""
echo "========================================="
echo "🎉 服务启动成功！"
echo "========================================="
echo ""
echo "访问地址："
echo "  🏠 主页:    http://localhost:${PORT}/"
echo "  📊 健康检查: http://localhost:${PORT}/api/health"
echo "  🎯 股票分析: http://localhost:${PORT}/api/analyze?code=<code>"
echo ""
echo "停止服务："
echo "  kill $NEW_PID"
echo ""
