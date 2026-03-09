#!/bin/bash
# ==================== 股票分析服务启动脚本 ====================

# 进入工作目录
cd "$(dirname "$0")"

# 停止旧的服务进程
echo "停止旧的服务进程..."
pkill -f "python3 stock_service.py" 2>/dev/null || true
sleep 2

# 启动新服务
echo "启动股票分析服务..."
nohup python3 stock_service.py >> stock_service.log 2>&1 &

# 等待服务启动
sleep 3

# 检查服务状态
if lsof -i:5000 2>/dev/null | grep -q LISTEN; then
    echo "✓ 服务已在5000端口成功启动！"
    echo "  访问地址：http://127.0.0.1:5000"
    echo "  健康检查：http://127.0.0.1:5000/api/health"
    echo "  日志文件：stock_service.log"
else
    echo "✗ 服务启动失败，请检查日志："
    tail -30 stock_service.log
fi
