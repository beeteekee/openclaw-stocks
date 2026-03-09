#!/bin/bash
# 添加top3-stock-stats-row的CSS样式

echo "========================================"
echo "添加top3-stock-stats-row样式"
echo "========================================"
echo ""

# 检查是否已存在样式
if grep -q "\.top3-stock-stats-row {" /Users/likan/.openclaw/workspace/stock-analysis.html; then
    echo "⚠️  样式已存在，跳过添加"
    exit 0
fi

# 在.top3-stat-value.down之后插入新样式
LINE_NUM=$(grep -n "\.top3-stat-value.down {" /Users/likan/.openclaw/workspace/stock-analysis.html | tail -1 | cut -d':' -f1)

echo "找到样式位置: 第${LINE_NUM}行"

# 插入新样式
sed -i '' "${LINE_NUM}a\\
        .top3-stock-stats-row {\\
            display: flex;\\
            flex-wrap: wrap;\\
            gap: 8px;\\
            font-size: 11px;\\
            align-items: center;\\
            justify-content: space-between;\\
        }\\
\\
        .top3-stock-stats-row .top3-stat-item {\\
            display: inline-block;\\
            color: rgba(255, 255, 255, 0.9);\\
            font-size: 11px;\\
            flex: 0 0 auto;\\
        }\\
\\
        .top3-stock-stats-row .top3-stat-item::before {\\
            content: '|';\\
            margin: 0 8px;\\
            color: rgba(255, 255, 255, 0.3);\\
        }\\
\\
        .top3-stock-stats-row .top3-stat-item:first-child::before {\\
            display: none;\\
        }\\
" /Users/likan/.openclaw/workspace/stock-analysis.html

echo ""
echo "✅ 样式已添加"

# 验证添加
echo ""
echo "[验证]"
echo "---"
if grep -q "\.top3-stock-stats-row {" /Users/likan/.openclaw/workspace/stock-analysis.html; then
    echo "✅ 样式定义存在"
    echo ""
    echo "新增样式内容:"
    grep -A 15 "\.top3-stock-stats-row {" /Users/likan/.openclaw/workspace/stock-analysis.html | head -20
else
    echo "❌ 样式定义不存在"
    exit 1
fi

echo ""
echo "🎉 添加完成！"
echo ""
echo "新样式说明:"
echo "========================================"
echo "1. display: flex - Flexbox布局"
echo "2. flex-wrap: wrap - 自动换行"
echo "3. gap: 8px - 项目间距8px"
echo "4. font-size: 11px - 字体大小11px"
echo "5. align-items: center - 垂直居中"
echo "6. justify-content: space-between - 两端对齐"
echo ""
echo "分隔符样式:"
echo "- 使用::before伪元素添加'|'分隔符"
echo "- 第一个项目不显示分隔符"
echo "- 分隔符颜色: rgba(255, 255, 255, 0.3)"
echo ""
echo "请打开浏览器查看效果: http://127.0.0.1:5000/"
