#!/bin/bash
# 检查Top3和stats-section的背景样式一致性

echo "========================================"
echo "Top3和stats-section样式对比检查"
echo "========================================"
echo ""

echo "[Top3-section样式]"
echo "---"
grep -A 6 "\.top3-section {" /Users/likan/.openclaw/workspace/stock-analysis.html | head -7
echo ""

echo "[stats-section样式]"
echo "---"
grep -A 6 "\.stats-section {" /Users/likan/.openclaw/workspace/stock-analysis.html | head -7
echo ""

echo "[检查一致性]"
echo "---"

# 提取background值
TOP3_BG=$(grep "\.top3-section {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep "background" | sed 's/.*background: //' | sed 's/;.*//')
STATS_BG=$(grep "\.stats-section {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep "background" | sed 's/.*background: //' | sed 's/;.*//')

echo "Top3 background: $TOP3_BG"
echo "Stats background: $STATS_BG"

if [ "$TOP3_BG" = "$STATS_BG" ]; then
    echo "✅ 背景颜色一致"
else
    echo "❌ 背景颜色不一致"
    exit 1
fi

# 提取border值
TOP3_BORDER=$(grep "\.top3-section {" -A 2 /Users/likan/.openclaw/workspace/stock-analysis.html | grep "border:" | sed 's/.*border: //' | sed 's/;.*//')
STATS_BORDER=$(grep "\.stats-section {" -A 2 /Users/likan/.openclaw/workspace/stock-analysis.html | grep "border:" | sed 's/.*border: //' | sed 's/;.*//')

echo "Top3 border: $TOP3_BORDER"
echo "Stats border: $STATS_BORDER"

if [ "$TOP3_BORDER" = "$STATS_BORDER" ]; then
    echo "✅ 边框样式一致"
else
    echo "❌ 边框样式不一致"
    exit 1
fi

# 提取padding值
TOP3_PADDING=$(grep "\.top3-section {" -A 3 /Users/likan/.openclaw/workspace/stock-analysis.html | grep "padding:" | sed 's/.*padding: //' | sed 's/;.*//')
STATS_PADDING=$(grep "\.stats-section {" -A 3 /Users/likan/.openclaw/workspace/stock-analysis.html | grep "padding:" | sed 's/.*padding: //' | sed 's/;.*//')

echo "Top3 padding: $TOP3_PADDING"
echo "Stats padding: $STATS_PADDING"

if [ "$TOP3_PADDING" = "$STATS_PADDING" ]; then
    echo "✅ 内边距一致"
else
    echo "❌ 内边距不一致"
    exit 1
fi

# 提取border-radius值
TOP3_RADIUS=$(grep "\.top3-section {" -A 5 /Users/likan/.openclaw/workspace/stock-analysis.html | grep "border-radius:" | sed 's/.*border-radius: //' | sed 's/;.*//')
STATS_RADIUS=$(grep "\.stats-section {" -A 5 /Users/likan/.openclaw/workspace/stock-analysis.html | grep "border-radius:" | sed 's/.*border-radius: //' | sed 's/;.*//')

echo "Top3 border-radius: $TOP3_RADIUS"
echo "Stats border-radius: $STATS_RADIUS"

if [ "$TOP3_RADIUS" = "$STATS_RADIUS" ]; then
    echo "✅ 圆角一致"
else
    echo "❌ 圆角不一致"
    exit 1
fi

# 检查内联样式
echo ""
echo "[内联样式检查]"
echo "---"
if grep 'id="top3Section"' /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "style="; then
    echo "⚠️  Top3-section有内联样式"
    grep 'id="top3Section"' /Users/likan/.openclaw/workspace/stock-analysis.html | grep "style="
else
    echo "✅ Top3-section无内联样式"
fi

if grep 'class="stats-section"' /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "style="; then
    echo "⚠️  Stats-section有内联样式"
    grep 'class="stats-section"' /Users/likan/.openclaw/workspace/stock-analysis.html | grep "style="
else
    echo "✅ Stats-section无内联样式"
fi

echo ""
echo "🎉 样式检查完成"
