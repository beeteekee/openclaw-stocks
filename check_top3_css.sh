#!/bin/bash
# 检查当前Top3卡片的CSS类名

echo "========================================"
echo "检查Top3卡片CSS类名"
echo "========================================"
echo ""

echo "[当前使用的类名]"
echo "---"
grep "top3-stock-stats" /Users/likan/.openclaw/workspace/stock-analysis.html
grep "top3-stock-stats-row" /Users/likan/.openclaw/workspace/stock-analysis.html

echo ""
echo "[HTML中使用的类名]"
echo "---"
grep "top3-stock-stats" /Users/likan/.openclaw/workspace/stock-analysis.html | grep "class="
grep "top3-stock-stats-row" /Users/likan/.openclaw/workspace/stock-analysis.html | grep "class="

echo ""
echo "[CSS样式定义]"
echo "---"
sed -n '246,280p' /Users/likan/.openclaw/workspace/stock-analysis.html
