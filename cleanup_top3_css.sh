#!/bin/bash
# 删除旧的top3-stock-stats样式并验证

echo "========================================"
echo "删除旧的top3-stock-stats样式"
echo "========================================"
echo ""

# 查找旧的样式块起始行
START_LINE=$(grep -n "\.top3-stock-stats {" /Users/likan/.openclaw/workspace/stock-analysis.html | tail -1 | cut -d':' -f1)
END_LINE=$(awk "NR>$START_LINE && /^[[:space:]]*}/ {print NR; exit}" /Users/likan/.openclaw/workspace/stock-analysis.html | head -1)

echo "旧样式块位置: 第${START_LINE}行到第${END_LINE}行"
echo ""

# 删除旧的样式块
sed -i '' "${START_LINE},${END_LINE}d" /Users/likan/.openclaw/workspace/stock-analysis.html

echo "✅ 旧样式已删除"
echo ""

# 验证新的样式是否正确
echo "[验证新样式]"
echo "---"
if grep -q "\.top3-stock-stats-row {" /Users/likan/.openclaw/workspace/stock-analysis.html; then
    echo "✅ 新的top3-stock-stats-row样式存在"
    echo ""
    echo "新样式内容:"
    sed -n '/\.top3-stock-stats-row {/,/^        }/' /Users/likan/.openclaw/workspace/stock-analysis.html
else
    echo "❌ 新的top3-stock-stats-row样式不存在"
    exit 1
fi

echo ""
echo "[检查冲突]"
echo "---"
if grep -q "\.top3-stock-stats {" /Users/likan/.openclaw/workspace/stock-analysis.html; then
    echo "❌ 旧的top3-stock-stats样式仍然存在"
    echo ""
    echo "找到的样式:"
    grep -n "\.top3-stock-stats {" /Users/likan/.openclaw/workspace/stock-analysis.html
    exit 1
else
    echo "✅ 没有冲突的样式"
fi

echo ""
echo "[验证HTML]"
echo "---"
if grep -q 'top3-stock-stats-row' /Users/likan/.openclaw/workspace/stock-analysis.html; then
    echo "✅ HTML中使用top3-stock-stats-row"
    echo ""
    echo "使用位置:"
    grep -n 'top3-stock-stats-row' /Users/likan/.openclaw/workspace/stock-analysis.html | grep 'class='
else
    echo "❌ HTML中未使用top3-stock-stats-row"
    exit 1
fi

echo ""
echo "🎉 清理完成！"
echo ""
echo "修改总结:"
echo "========================================"
echo "1. ✅ 删除旧的top3-stock-stats样式"
echo "2. ✅ 保留新的top3-stock-stats-row样式"
echo "3. ✅ HTML中使用top3-stock-stats-row"
echo "4. ✅ 没有样式冲突"
echo ""
echo "新样式说明:"
echo "- 使用flex布局"
echo "- 支持自动换行(flex-wrap: wrap)"
echo "- 项目间距8px(gap: 8px)"
echo "- 字体大小11px(font-size: 11px)"
echo "- 两端对齐(justify-content: space-between)"
echo ""
echo "请打开浏览器查看效果: http://127.0.0.1:5000/"
