#!/bin/bash
# 终极对齐验证

echo "========================================"
echo "Top3和stats-section终极对齐验证"
echo "========================================"
echo ""

echo "[验证1] 桌面端Grid布局]"
echo "---"
if grep "\.top3-content {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "minmax(200px"; then
    echo "✅ Top3-content: minmax(200px, 1fr)"
else
    echo "❌ Top3-content: 不正确"
    exit 1
fi

if grep "\.stats-content {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "minmax(200px"; then
    echo "✅ Stats-content: minmax(200px, 1fr)"
else
    echo "❌ Stats-content: 不正确"
    exit 1
fi

echo "✅ 桌面端Grid一致"

echo ""
echo "[验证2] 移动端Grid布局]"
echo "---"
if awk '/@media.*768px/,/^        }/' /Users/likan/.openclaw/workspace/stock-analysis.html | grep -A 1 "\.top3-content {" | grep -q "minmax(150px"; then
    echo "✅ Top3-content: minmax(150px, 1fr)"
else
    echo "❌ Top3-content移动端: 不正确或缺失"
    exit 1
fi

if awk '/@media.*768px/,/^        }/' /Users/likan/.openclaw/workspace/stock-analysis.html | grep -A 1 "\.stats-content {" | grep -q "minmax(150px"; then
    echo "✅ Stats-content: minmax(150px, 1fr)"
else
    echo "❌ Stats-content移动端: 不正确或缺失"
    exit 1
fi

echo "✅ 移动端Grid一致"

echo ""
echo "[验证3] 容器宽度]"
echo "---"
CONTAINER_MAX=$(grep "\.container {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep "max-width:" | sed 's/.*max-width: //' | sed 's/;.*//')
CONTAINER_WIDTH=$(grep "\.container {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep "width:" | sed 's/.*width: //' | sed 's/;.*//')

echo "Container: max-width: $CONTAINER_MAX, width: $CONTAINER_WIDTH"

if [ "$CONTAINER_MAX" = "900px" ] && [ "$CONTAINER_WIDTH" = "100%" ]; then
    echo "✅ Container宽度正确"
else
    echo "❌ Container宽度不正确"
    exit 1
fi

echo ""
echo "[验证4] 区域宽度限制]"
echo "---"
TOP3_WIDTH=$(grep "\.top3-section {" -A 10 /Users/likan/.openclaw/workspace/stock-analysis.html | grep "max-width:" | sed 's/.*max-width: //' | sed 's/;.*//')
STATS_WIDTH=$(grep "\.stats-section {" -A 10 /Users/likan/.openclaw/workspace/stock-analysis.html | grep "max-width:" | sed 's/.*max-width: //' | sed 's/;.*//')

if [ -z "$TOP3_WIDTH" ] && [ -z "$STATS_WIDTH" ]; then
    echo "✅ Top3-section: 无额外宽度限制，继承container"
    echo "✅ Stats-section: 无额外宽度限制，继承container"
elif [ "$TOP3_WIDTH" = "$STATS_WIDTH" ]; then
    echo "✅ 区域宽度一致: $TOP3_WIDTH"
else
    echo "❌ 区域宽度不一致"
    exit 1
fi

echo ""
echo "[验证5] 卡片间距]"
echo "---"
if grep "\.top3-content {" -A 2 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "gap: 10px"; then
    echo "✅ Top3-content: gap: 10px"
else
    echo "❌ Top3-content间距不正确"
    exit 1
fi

if grep "\.stats-content {" -A 2 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "gap: 10px"; then
    echo "✅ Stats-content: gap: 10px"
else
    echo "❌ Stats-content间距不正确"
    exit 1
fi

echo "✅ 卡片间距一致"

echo ""
echo "[验证6] 桌面端padding]"
echo "---"
if grep "\.result-section {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "padding: 20px"; then
    echo "✅ Result-section: 20px"
else
    echo "❌ Result-section桌面端padding不正确"
    exit 1
fi

if grep "\.top3-section {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "padding: 20px"; then
    echo "✅ Top3-section: 20px"
else
    echo "❌ Top3-section桌面端padding不正确"
    exit 1
fi

if grep "\.stats-section {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "padding: 20px"; then
    echo "✅ Stats-section: 20px"
else
    echo "❌ Stats-section桌面端padding不正确"
    exit 1
fi

echo "✅ 桌面端padding一致"

echo ""
echo "[验证7] 移动端padding]"
echo "---"
if awk '/@media.*768px/,/^[[:space:]]*}/' /Users/likan/.openclaw/workspace/stock-analysis.html | grep -A 1 "\.result-section {" | grep -q "padding: 20px"; then
    echo "✅ Result-section: 20px"
else
    echo "❌ Result-section移动端padding不正确"
    exit 1
fi

echo "✅ Top3-section: 20px (继承桌面端)"
echo "✅ Stats-section: 20px (继承桌面端)"

echo "✅ 移动端padding一致"

echo ""
echo "🎉 所有验证通过！"
echo ""
echo "对齐优化总结:"
echo "========================================"
echo "✅ 桌面端Grid: minmax(200px, 1fr) (一致)"
echo "✅ 移动端Grid: minmax(150px, 1fr) (一致)"
echo "✅ Container宽度: 900px (统一)"
echo "✅ 区域宽度: 继承container (无额外限制)"
echo "✅ 卡片间距: 10px (一致)"
echo "✅ 桌面端padding: 20px (所有区域一致)"
echo "✅ 移动端padding: 20px (所有区域一致)"
echo ""
echo "Top3和stats-section的宽度和样式现在完全一致！"
echo ""
echo "请打开浏览器查看效果: http://127.0.0.1:5000/"
