#!/bin/bash
# 任务检查脚本 - 用于跟踪项目任务进度

echo "==================================="
echo "  📋 项目任务检查 - $(date '+%Y-%m-%d %H:%M:%S')"
echo "==================================="
echo ""

# 检查服务状态
echo "📊 服务状态检查："
echo "-----------------------------------"

# Gateway服务
if lsof -i :18789 > /dev/null 2>&1; then
    echo "✅ Gateway服务：运行中 (端口 18789)"
else
    echo "❌ Gateway服务：未运行"
fi

# 后端服务
if ps aux | grep stock_service.py | grep -v grep > /dev/null; then
    echo "✅ 后端服务：运行中"
else
    echo "❌ 后端服务：未运行"
fi

# 公网服务
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://stockbot.nat100.top/stock-analysis-final.html)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 公网服务：正常 (HTTP $HTTP_CODE)"
else
    echo "❌ 公网服务：异常 (HTTP $HTTP_CODE)"
fi

echo ""

# 检查Git状态
echo "📦 Git状态检查："
echo "-----------------------------------"
cd /Users/likan/.openclaw/workspace
CURRENT_BRANCH=$(git branch --show-current)
LATEST_COMMIT=$(git log -1 --format="%h - %s (%cr)")
echo "📍 当前分支：$CURRENT_BRANCH"
echo "🔖 最新提交：$LATEST_COMMIT"
UNCOMMITTED=$(git status --porcelain | wc -l)
if [ "$UNCOMMITTED" -eq 0 ]; then
    echo "✅ 工作区：干净"
else
    echo "⚠️  工作区：有 $UNCOMMITTED 个未提交的文件"
fi

echo ""

# 检查任务进度
echo "🎯 任务进度检查："
echo "-----------------------------------"
if [ -f "TASKS.md" ]; then
    echo "✅ 任务清单：TASKS.md 存在"
    # 统计任务数量
    TODO_COUNT=$(grep -c "📝 待分配" TASKS.md 2>/dev/null || echo 0)
    INPROGRESS_COUNT=$(grep -c "🔄 进行中" TASKS.md 2>/dev/null || echo 0)
    DONE_COUNT=$(grep -c "✅ 已完成" TASKS.md 2>/dev/null || echo 0)
    echo "   - 待分配：$TODO_COUNT"
    echo "   - 进行中：$INPROGRESS_COUNT"
    echo "   - 已完成：$DONE_COUNT"
else
    echo "❌ 任务清单：TASKS.md 不存在"
fi

echo ""

# 检查日志文件
echo "📝 日志文件检查："
echo "-----------------------------------"
if [ -f "stock_service.log" ]; then
    echo "✅ 后端日志：存在 ($(tail -1 stock_service.log))"
else
    echo "⚠️  后端日志：不存在"
fi

if [ -f "PM_DAILY_UPDATE_$(date '+%Y%m%d').md" ]; then
    echo "✅ 今日日报：存在"
else
    echo "⚠️  今日日报：不存在"
fi

echo ""

# 内存和CPU使用
echo "💻 系统资源检查："
echo "-----------------------------------"
CPU_USAGE=$(top -l 1 -n 0 | grep "CPU usage" | awk '{print $3}')
MEM_USAGE=$(top -l 1 -n 0 | grep "PhysMem" | awk '{print $2}')
echo "CPU使用率：$CPU_USAGE"
echo "内存使用：$MEM_USAGE"

echo ""
echo "==================================="
echo "  检查完成"
echo "==================================="
