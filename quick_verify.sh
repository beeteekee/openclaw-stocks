#!/bin/bash
# 快速验证定时脚本设置

echo "========================================"
echo "定时脚本快速验证"
echo "========================================"
echo ""

# 检查Cron任务
if crontab -l 2>/dev/null | grep -q "run_top3_daily"; then
    echo "✅ Cron任务: 已设置"
    crontab -l | grep "run_top3_daily"
else
    echo "❌ Cron任务: 未设置"
    exit 1
fi

# 检查运行脚本
if [ -x "/Users/likan/.openclaw/workspace/run_top3_daily.sh" ]; then
    echo "✅ 运行脚本: 存在且可执行"
else
    echo "❌ 运行脚本: 不存在或无执行权限"
    exit 1
fi

# 检查选股脚本
if [ -f "/Users/likan/.openclaw/workspace/top3_today.py" ]; then
    echo "✅ 选股脚本: 存在"
else
    echo "❌ 选股脚本: 不存在"
    exit 1
fi

# 检查结果文件
if [ -f "/Users/likan/.openclaw/workspace/top3_today_result.csv" ]; then
    echo "✅ 结果文件: 存在"
    ls -lh /Users/likan/.openclaw/workspace/top3_today_result.csv
else
    echo "❌ 结果文件: 不存在"
    exit 1
fi

# 检查API
if curl -s http://127.0.0.1:5000/api/top3-today | grep -q "status.*ok"; then
    echo "✅ API接口: 正常"
else
    echo "⚠️  API接口: 无法连接或异常"
fi

echo ""
echo "当前时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "下次运行: 今天 17:00"
echo ""
echo "📊 所有检查完成！"
echo ""
echo "手动运行测试:"
echo "  bash /Users/likan/.openclaw/workspace/run_top3_daily.sh"
echo ""
echo "查看日志:"
echo "  tail -f /Users/likan/.openclaw/workspace/top3_today.log"
