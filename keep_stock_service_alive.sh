#!/bin/bash
# ==================== 股票服务守护脚本 ====================
# 自动监控并重启崩溃的股票分析服务

cd "$(dirname "$0")"

while true; do
    # 检查服务是否在运行
    if ! lsof -i :5000 > /dev/null 2>&1; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  检测到服务已停止，正在重启..."
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 重启服务中..."

        # 重启服务
        nohup python3 -u stock_service.py >> stock_service.log 2>&1 &
        SERVICE_PID=$!

        # 等待服务启动
        sleep 5

        # 检查服务是否成功启动
        if lsof -i :5000 > /dev/null 2>&1; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 服务重启成功 (PID: $SERVICE_PID)"
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 服务重启失败，请检查日志"
            tail -30 stock_service.log
        fi
    fi

    # 每10秒检查一次
    sleep 10
done
