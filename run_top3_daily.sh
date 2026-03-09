#!/bin/bash
# Top3选股定时脚本 - 每天11:00和17:00执行

# 切换到工作目录
cd /Users/likan/.openclaw/workspace

# 获取当前时间
CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# 记录开始时间
echo "========================================" >> /Users/likan/.openclaw/workspace/top3_today.log
echo "开始时间: ${CURRENT_TIME}" >> /Users/likan/.openclaw/workspace/top3_today.log
echo "执行类型: 定时任务" >> /Users/likan/.openclaw/workspace/top3_today.log

# 运行选股脚本
if /usr/bin/python3 top3_today.py >> /Users/likan/.openclaw/workspace/top3_today.log 2>&1; then
    # 执行成功
    SUCCESS_TIME=$(date '+%Y-%m-%d %H:%M:%S')
    echo "执行状态: 成功" >> /Users/likan/.openclaw/workspace/top3_today.log
    echo "结束时间: ${SUCCESS_TIME}" >> /Users/likan/.openclaw/workspace/top3_today.log
    echo "========================================" >> /Users/likan/.openclaw/workspace/top3_today.log
    echo "" >> /Users/likan/.openclaw/workspace/top3_today.log
    exit 0
else
    # 执行失败
    FAIL_TIME=$(date '+%Y-%m-%d %H:%M:%S')
    echo "执行状态: 失败" >> /Users/likan/.openclaw/workspace/top3_today.log
    echo "结束时间: ${FAIL_TIME}" >> /Users/likan/.openclaw/workspace/top3_today.log
    echo "错误信息: 请检查日志详细信息" >> /Users/likan/.openclaw/workspace/top3_today.log
    echo "========================================" >> /Users/likan/.openclaw/workspace/top3_today.log
    echo "" >> /Users/likan/.openclaw/workspace/top3_today.log

    # TODO: 可以在这里添加错误通知逻辑（邮件、消息等）

    exit 1
fi
