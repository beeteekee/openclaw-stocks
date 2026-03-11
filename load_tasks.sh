#!/bin/bash
# 任务加载脚本 - stock-analysis agent启动时自动加载任务

echo "========================================="
echo "  检查待办任务"
echo "========================================="
echo ""

# 读取TASKS.md中的任务
TASKS_MD="/Users/likan/.openclaw/workspace/TASKS.md"

if [ ! -f "$TASKS_MD" ]; then
    echo "⚠️ TASKS.md 文件不存在"
    exit 1
fi

# 提取进行中的任务
echo "当前进行中的任务："
grep -A 20 "## 任务状态跟踪" "$TASKS_MD" | grep "🔄" | while read line; do
    echo "  - $line"
done

echo ""
echo "========================================="
echo "  详细任务信息请查看 TASKS.md"
echo "========================================="
echo ""
echo "提示：请在开始工作前查看TASKS.md中的质量检查标准"
