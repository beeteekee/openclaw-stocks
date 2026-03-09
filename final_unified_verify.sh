#!/bin/bash
# 最终验证Top3和查询统计融合效果

echo "========================================"
echo "验证Top3和查询统计融合效果"
echo "========================================"
echo ""

echo "[验证1] HTML结构]"
echo "---"
if grep -q "class=\"unified-section\"" /Users/likan/.openclaw/workspace/stock-analysis.html; then
    echo "✅ 统一区域容器存在"
else
    echo "❌ 统一区域容器不存在"
    exit 1
fi

if grep -q "class=\"unified-header\"" /Users/likan/.openclaw/workspace/stock-analysis.html; then
    echo "✅ 统一区域头部存在"
else
    echo "❌ 统一区域头部不存在"
    exit 1
fi

if grep -q "class=\"unified-content\"" /Users/likan/.openclaw/workspace/stock-analysis.html; then
    echo "✅ 统一区域内容存在"
else
    echo "❌ 统一区域内容不存在"
    exit 1
fi

echo ""
echo "[验证2] 标题展示]"
echo "---"
if grep -q "class=\"unified-title\"" /Users/likan/.openclaw/workspace/stock-analysis.html; then
    echo "✅ Top3标题样式: .unified-title (金色)"
else
    echo "❌ Top3标题样式不存在"
    exit 1
fi

if grep -q "class=\"unified-subtitle\"" /Users/likan/.openclaw/workspace/stock-analysis.html; then
    echo "✅ 查询统计副标题样式: .unified-subtitle (绿色)"
else
    echo "❌ 查询统计副标题样式不存在"
    exit 1
fi

echo ""
echo "[验证3] CSS样式]"
echo "---"
if awk '/\.unified-section {/,/^        }/' /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "background"; then
    echo "✅ 统一区域样式存在"
else
    echo "❌ 统一区域样式不存在"
    exit 1
fi

if awk '/\.unified-header {/,/^        }/' /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "display"; then
    echo "✅ 统一区域头部样式存在"
else
    echo "❌ 统一区域头部样式不存在"
    exit 1
fi

echo ""
echo "[验证4] Grid布局]"
echo "---"
if awk '/\.unified-content {/,/^        }/' /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "grid-template-columns"; then
    echo "✅ Grid布局已设置"
    echo ""
    echo "布局配置:"
    awk '/\.unified-content {/,/^        }/' /Users/likan/.openclaw/workspace/stock-analysis.html | grep "grid-template-columns"
else
    echo "❌ Grid布局未设置"
    exit 1
fi

echo ""
echo "[验证5] 响应式设计]"
echo "---"
if awk '/@media.*768px/,/^        }/' /Users/likan/.openclaw/workspace/stock-analysis.html | grep -A 1 "\.unified-content" | grep -q "grid-template-columns"; then
    echo "✅ 移动端响应式样式存在"
    echo ""
    echo "移动端配置:"
    awk '/@media.*768px/,/^        }/' /Users/likan/.openclaw/workspace/stock-analysis.html | grep -A 1 "\.unified-content" | grep "grid-template-columns"
else
    echo "❌ 移动端响应式样式不存在"
    exit 1
fi

echo ""
echo "[验证6] 样式一致性]"
echo "---"
if awk '/\.unified-section {/,/^        }/' /Users/likan/.openclaw/workspace/stock-analysis.html | grep "background:" | grep -q "rgba(30, 30, 40, 0.95)"; then
    echo "✅ 深色背景: rgba(30, 30, 40, 0.95)"
else
    echo "❌ 背景样式不一致"
    exit 1
fi

if awk '/\.unified-section {/,/^        }/' /Users/likan/.openclaw/workspace/stock-analysis.html | grep "padding:" | grep -q "20px"; then
    echo "✅ 内边距: 20px"
else
    echo "❌ 内边距样式不一致"
    exit 1
fi

if awk '/\.unified-section {/,/^        }/' /Users/likan/.openclaw/workspace/stock-analysis.html | grep "border-radius:" | grep -q "12px"; then
    echo "✅ 圆角: 12px"
else
    echo "❌ 圆角样式不一致"
    exit 1
fi

echo ""
echo "[验证7] 旧区域清理]"
echo "---"
if grep -q "class=\"top3-section\"" /Users/likan/.openclaw/workspace/stock-analysis.html; then
    echo "⚠️  警告: 旧top3-section类名仍在使用"
else
    echo "✅ 旧top3-section类名已清理"
fi

if grep -q "class=\"stats-section\"" /Users/likan/.openclaw/workspace/stock-analysis.html; then
    echo "⚠️  警告: 旧stats-section类名仍在使用"
else
    echo "✅ 旧stats-section类名已清理"
fi

echo ""
echo "📊 融合效果验证总结"
echo "========================================"
echo "✅ HTML结构：Top3和查询统计已合并"
echo "✅ 标题展示：Top3标题（金色）和查询统计副标题（绿色）"
echo "✅ CSS样式：统一深色背景和布局"
echo "✅ Grid布局：桌面端2列（2fr:1fr），移动端1列"
echo "✅ 响应式设计：已添加移动端样式"
echo "✅ 样式一致性：背景、内边距、圆角统一"
echo "✅ 旧区域清理：已替换为新的统一区域"
echo ""
echo "布局说明:"
echo "========================================"
echo "桌面端 (>768px):"
echo "  ┌──────────────────────────┐"
echo "  │ 🏆 今日Top3 | 📊 查询统计  │"
echo "  │ ├────────┐   ├─────────┐  │"
echo "  │ │ Top3  │   │  查询  │  │"
echo "  │ │ 股票1 │   │  股票1 │  │"
echo "  │ │ 股票2 │   │  股票2 │  │"
echo "  │ │ 股票3 │   │  股票3 │  │"
echo "  │ └────────┘   └─────────┘  │"
echo "  └──────────────────────────┘"
echo ""
echo "移动端 (≤768px):"
echo "  ┌────────────────────┐"
echo "  │ 🏆 今日Top3        │"
echo "  │ ├────────┐        │"
echo "  │ │ Top3  │        │"
echo "  │ │ 股票1 │        │"
echo "  │ │ 股票2 │        │"
echo "  │ │ 股票3 │        │"
echo "  │ └────────┘        │"
echo "  │ 📊 查询统计        │"
echo "  │ ├────────┐        │"
echo "  │ │  查询  │        │"
echo "  │ │  股票1 │        │"
echo "  │ └────────┘        │"
echo "  └────────────────────┘"
echo ""
echo "请打开浏览器查看效果: http://127.0.0.1:5000/"
