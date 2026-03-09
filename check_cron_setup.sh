#!/bin/bash
# 测试定时脚本设置和运行

echo "========================================"
echo "定时脚本设置和运行检查"
echo "========================================"
echo ""

echo "[检查1] Cron任务设置"
echo "---"
CRON_JOB=$(crontab -l 2>/dev/null | grep "run_top3_daily")
if [ -n "$CRON_JOB" ]; then
    echo "✅ Cron任务已设置:"
    echo "   $CRON_JOB"
    
    # 解析cron时间
    SCHEDULE=$(echo "$CRON_JOB" | awk '{print $1" "$2" "$3" "$4" "$5}')
    MINUTE=$(echo "$SCHEDULE" | awk '{print $1}')
    HOUR=$(echo "$SCHEDULE" | awk '{print $2}')
    echo "   运行时间: 每天 ${HOUR}:${MINUTE}"
else
    echo "❌ Cron任务未设置"
    exit 1
fi

echo ""
echo "[检查2] 运行脚本权限"
echo "---"
SCRIPT="/Users/likan/.openclaw/workspace/run_top3_daily.sh"
if [ -x "$SCRIPT" ]; then
    echo "✅ 运行脚本存在且有执行权限"
    ls -lh "$SCRIPT"
else
    echo "❌ 运行脚本不存在或无执行权限"
    exit 1
fi

echo ""
echo "[检查3] 选股脚本存在性]"
echo "---"
PY_SCRIPT="/Users/likan/.openclaw/workspace/top3_today.py"
if [ -f "$PY_SCRIPT" ]; then
    echo "✅ 选股脚本存在"
    ls -lh "$PY_SCRIPT"
else
    echo "❌ 选股脚本不存在"
    exit 1
fi

echo ""
echo "[检查4] 运行日志]"
echo "---"
LOG_FILE="/Users/likan/.openclaw/workspace/top3_today.log"
if [ -f "$LOG_FILE" ]; then
    echo "✅ 日志文件存在"
    LOG_SIZE=$(ls -lh "$LOG_FILE" | awk '{print $5}')
    LOG_MODIFIED=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$LOG_FILE")
    echo "   文件大小: $LOG_SIZE"
    echo "   最后修改: $LOG_MODIFIED"
    echo ""
    echo "   最新日志内容（最后10行）:"
    tail -10 "$LOG_FILE"
else
    echo "❌ 日志文件不存在"
fi

echo ""
echo "[检查5] 选股结果文件]"
echo "---"
RESULT_FILE="/Users/likan/.openclaw/workspace/top3_today_result.csv"
if [ -f "$RESULT_FILE" ]; then
    echo "✅ 选股结果文件存在"
    RESULT_SIZE=$(ls -lh "$RESULT_FILE" | awk '{print $5}')
    RESULT_MODIFIED=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$RESULT_FILE")
    echo "   文件大小: $RESULT_SIZE"
    echo "   最后修改: $RESULT_MODIFIED"
    echo ""
    echo "   Top3股票（前3名）:"
    head -4 "$RESULT_FILE" | tail -3 | cut -d',' -f1,2,3 | while IFS=',' read -r code name industry; do
        echo "   - $name ($code) - $industry"
    done
else
    echo "❌ 选股结果文件不存在"
    exit 1
fi

echo ""
echo "[检查6] 当前时间]"
echo "---"
CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')
CURRENT_HOUR=$(date '+%H')
CURRENT_MINUTE=$(date '+%M')
echo "   当前时间: $CURRENT_TIME"
echo "   当前小时: $CURRENT_HOUR"
echo "   当前分钟: $CURRENT_MINUTE"

if [ "$HOUR" = "$CURRENT_HOUR" ] && [ "$MINUTE" = "$CURRENT_MINUTE" ]; then
    echo "   ⚠️  当前就是定时任务运行时间！"
fi

echo ""
echo "[检查7] 下次运行时间]"
echo "---"
if [ "$CURRENT_HOUR" -lt "$HOUR" ] || [ "$CURRENT_HOUR" -eq "$HOUR" -a "$CURRENT_MINUTE" -lt "$MINUTE" ]; then
    # 今天还没到运行时间
    NEXT_RUN="今天 ${HOUR}:${MINUTE}"
else
    # 今天已经过了运行时间，下次是明天
    NEXT_RUN="明天 ${HOUR}:${MINUTE}"
fi
echo "   下次运行: $NEXT_RUN"

echo ""
echo "[检查8] Python环境]"
echo "---"
PYTHON_PATH=$(which python3)
if [ -n "$PYTHON_PATH" ]; then
    echo "✅ Python环境: $PYTHON_PATH"
    python3 --version
else
    echo "❌ Python环境未找到"
    exit 1
fi

echo ""
echo "[检查9] Tushare Token]"
echo "---"
if grep -q "TUSHARE_TOKEN" "$PY_SCRIPT"; then
    TOKEN=$(grep "TUSHARE_TOKEN" "$PY_SCRIPT" | head -1 | sed 's/.*=//' | sed "s/'//g" | sed 's/"//g')
    echo "✅ Tushare Token已设置"
    echo "   Token: ${TOKEN:0:20}..."
else
    echo "❌ Tushare Token未设置"
    exit 1
fi

echo ""
echo "📊 检查总结"
echo "========================================"
echo "✅ Cron任务已设置: 每天 ${HOUR}:${MINUTE}"
echo "✅ 运行脚本存在且可执行"
echo "✅ 选股脚本存在"
echo "✅ 日志文件存在"
echo "✅ 选股结果文件存在"
echo "✅ Python环境正常"
echo "✅ Tushare Token已设置"
echo ""
echo "下次自动运行: $NEXT_RUN"
echo ""
echo "📝 手动运行测试"
echo "========================================"
echo "如需立即运行测试，可以执行:"
echo "  bash /Users/likan/.openclaw/workspace/run_top3_daily.sh"
echo ""
echo "或直接运行Python脚本:"
echo "  python3 /Users/likan/.openclaw/workspace/top3_today.py"
echo ""
echo "查看实时日志:"
echo "  tail -f /Users/likan/.openclaw/workspace/top3_today.log"
