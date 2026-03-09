#!/bin/bash
# 检查Top3和stats-section的内容宽度一致性

echo "========================================"
echo "Top3和stats-section内容宽度一致性检查"
echo "========================================"
echo ""

# 检查桌面端Grid布局
echo "[桌面端Grid布局]"
echo "---"
TOP3_GRID=$(sed -n '203p' /Users/likan/.openclaw/workspace/stock-analysis.html | sed 's/^[[:space:]]*//')
STATS_GRID=$(sed -n '940p' /Users/likan/.openclaw/workspace/stock-analysis.html | sed 's/^[[:space:]]*//')

echo "Top3-content: $TOP3_GRID"
echo "Stats-content: $STATS_GRID"

if [ "$TOP3_GRID" = "$STATS_GRID" ]; then
    echo "✅ 桌面端Grid布局一致"
else
    echo "❌ 桌面端Grid布局不一致"
    exit 1
fi

# 检查移动端Grid布局
echo ""
echo "[移动端Grid布局]"
echo "---"
TOP3_GRID_MOBILE=$(sed -n '1004p' /Users/likan/.openclaw/workspace/stock-analysis.html | sed 's/^[[:space:]]*//')
STATS_GRID_MOBILE=$(sed -n '996p' /Users/likan/.openclaw/workspace/stock-analysis.html | sed 's/^[[:space:]]*//')

echo "Top3-content: $TOP3_GRID_MOBILE"
echo "Stats-content: $STATS_GRID_MOBILE"

if [ "$TOP3_GRID_MOBILE" = "$STATS_GRID_MOBILE" ]; then
    echo "✅ 移动端Grid布局一致"
else
    echo "❌ 移动端Grid布局不一致"
    exit 1
fi

# 检查卡片间距
echo ""
echo "[卡片间距]"
echo "---"
TOP3_GAP=$(sed -n '204p' /Users/likan/.openclaw/workspace/stock-analysis.html | sed 's/.*gap: //' | sed 's/;.*//')
STATS_GAP=$(sed -n '941p' /Users/likan/.openclaw/workspace/stock-analysis.html | sed 's/.*gap: //' | sed 's/;.*//')

echo "Top3-content: $TOP3_GAP"
echo "Stats-content: $STATS_GAP"

if [ "$TOP3_GAP" = "$STATS_GAP" ]; then
    echo "✅ 卡片间距一致"
else
    echo "❌ 卡片间距不一致"
    exit 1
fi

# 检查卡片padding
echo ""
echo "[卡片padding]"
echo "---"
TOP3_PADDING=$(awk 'NR==211' /Users/likan/.openclaw/workspace/stock-analysis.html | sed 's/.*padding: //' | sed 's/;.*//' | tr -d ' ')
STATS_PADDING=$(awk 'NR>=944 && NR<=950' /Users/likan/.openclaw/workspace/stock-analysis.html | grep "padding" | sed 's/.*padding: //' | sed 's/;.*//' | tr -d ' ')

echo "Top3-stock-card: $TOP3_PADDING"
echo "Stats-item: $STATS_PADDING"

if [ "$TOP3_PADDING" = "$STATS_PADDING" ]; then
    echo "✅ 卡片padding一致"
else
    echo "❌ 卡片padding不一致"
    exit 1
fi

echo ""
echo "🎉 所有宽度检查通过！"
echo ""
echo "Top3和stats-section的内容宽度完全一致:"
echo "========================================"
echo ""
echo "桌面端:"
echo "  Top3-content: $TOP3_GRID"
echo "  Stats-content: $STATS_GRID"
echo "  ✅ 一致"
echo ""
echo "移动端:"
echo "  Top3-content: $TOP3_GRID_MOBILE"
echo "  Stats-content: $STATS_GRID_MOBILE"
echo "  ✅ 一致"
echo ""
echo "卡片间距: $TOP3_GAP"
echo "卡片padding: $TOP3_PADDING"
echo ""
echo "请打开浏览器查看效果: http://127.0.0.1:5000/"
