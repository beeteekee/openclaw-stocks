#!/bin/bash
# 验证融合区域的美感优化

echo "========================================"
echo "验证融合区域的美感优化"
echo "========================================"
echo ""

echo "[验证1] 统一区域容器样式]"
echo "---"
if grep "\.unified-section {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "linear-gradient"; then
    echo "✅ 背景使用渐变色: linear-gradient"
else
    echo "❌ 背景未使用渐变色"
    exit 1
fi

if grep "\.unified-section {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "box-shadow"; then
    echo "✅ 添加了阴影效果: box-shadow"
else
    echo "❌ 未添加阴影效果"
    exit 1
fi

if grep "\.unified-section {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "border.*rgba(255, 255, 255, 0.15)"; then
    echo "✅ 边框使用浅色: rgba(255, 255, 255, 0.15)"
else
    echo "❌ 边框颜色未优化"
    exit 1
fi

echo ""
echo "[验证2] 标题样式优化]"
echo "---"
if grep "\.unified-title {" -A 2 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "text-shadow"; then
    echo "✅ Top3标题添加了阴影: text-shadow"
else
    echo "❌ Top3标题未添加阴影"
    exit 1
fi

if grep "\.unified-title {" -A 2 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "letter-spacing"; then
    echo "✅ Top3标题添加了字间距: letter-spacing"
else
    echo "❌ Top3标题未添加字间距"
    exit 1
fi

if grep "\.unified-subtitle {" -A 2 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "text-shadow"; then
    echo "✅ 查询统计标题添加了阴影: text-shadow"
else
    echo "❌ 查询统计标题未添加阴影"
    exit 1
fi

echo ""
echo "[验证3] Top3内容容器样式]"
echo "---"
if grep "\.top3-content {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "background: rgba(255, 215, 0, 0.03)"; then
    echo "✅ Top3容器使用微弱金色背景: rgba(255, 215, 0, 0.03)"
else
    echo "❌ Top3容器背景颜色未优化"
    exit 1
fi

if grep "\.top3-content {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "border: 1px solid rgba(255, 215, 0, 0.1)"; then
    echo "✅ Top3容器使用金色边框: rgba(255, 215, 0, 0.1)"
else
    echo "❌ Top3容器边框颜色未优化"
    exit 1
fi

echo ""
echo "[验证4] 查询统计内容容器样式]"
echo "---"
if grep "\.stats-content {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "background: rgba(76, 175, 80, 0.03)"; then
    echo "✅ 查询统计容器使用微弱绿色背景: rgba(76, 175, 80, 0.03)"
else
    echo "❌ 查询统计容器背景颜色未优化"
    exit 1
fi

if grep "\.stats-content {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "border: 1px solid rgba(76, 175, 80, 0.1)"; then
    echo "✅ 查询统计容器使用绿色边框: rgba(76, 175, 80, 0.1)"
else
    echo "❌ 查询统计容器边框颜色未优化"
    exit 1
fi

echo ""
echo "[验证5] Top3股票卡片样式]"
echo "---"
if grep "\.top3-stock-name {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "0.95"; then
    echo "✅ Top3股票名称使用更亮的颜色: rgba(255, 255, 255, 0.95)"
else
    echo "❌ Top3股票名称颜色未优化"
    exit 1
fi

if grep "\.top3-stock-code {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "letter-spacing"; then
    echo "✅ Top3股票代码添加了字间距: letter-spacing"
else
    echo "❌ Top3股票代码未添加字间距"
    exit 1
fi

echo ""
echo "[验证6] Top3信息行样式]"
echo "---"
if grep "\.top3-stock-stats-row {" -A 2 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "font-weight: 500"; then
    echo "✅ Top3信息行使用中粗字体: font-weight: 500"
else
    echo "❌ Top3信息行字体粗细未优化"
    exit 1
fi

if grep "\.top3-stock-stats-row {" -A 2 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "letter-spacing"; then
    echo "✅ Top3信息行添加了字间距: letter-spacing"
else
    echo "❌ Top3信息行未添加字间距"
    exit 1
fi

if grep "\.top3-stock-stats-row {" -A 2 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "0.85"; then
    echo "✅ Top3信息行使用更亮的颜色: rgba(255, 255, 255, 0.85)"
else
    echo "❌ Top3信息行颜色未优化"
    exit 1
fi

echo ""
echo "[验证7] Top3卡片悬停效果]"
echo "---"
if grep "\.top3-stock-card:hover {" -A 3 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "box-shadow"; then
    echo "✅ Top3卡片悬停添加了阴影: box-shadow"
else
    echo "❌ Top3卡片悬停未添加阴影"
    exit 1
fi

if grep "\.top3-stock-card:hover {" -A 3 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "#ffd700"; then
    echo "✅ Top3卡片悬停边框使用金色: #ffd700"
else
    echo "❌ Top3卡片悬停边框颜色未优化"
    exit 1
fi

echo ""
echo "[验证8] 查询统计卡片样式]"
echo "---"
if grep "\.stats-item-name {" -A 1 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "0.95"; then
    echo "✅ 查询统计股票名称使用更亮的颜色: rgba(255, 255, 255, 0.95)"
else
    echo "❌ 查询统计股票名称颜色未优化"
    exit 1
fi

if grep "\.stats-item:hover {" -A 3 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "box-shadow"; then
    echo "✅ 查询统计卡片悬停添加了阴影: box-shadow"
else
    echo "❌ 查询统计卡片悬停未添加阴影"
    exit 1
fi

echo ""
echo "[验证9] 涨跌幅文字阴影]"
echo "---"
if grep "\.top3-stat-value.up {" -A 2 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "text-shadow"; then
    echo "✅ 上涨涨跌幅添加了文字阴影: text-shadow (红色)"
else
    echo "❌ 上涨涨跌幅未添加文字阴影"
    exit 1
fi

if grep "\.top3-stat-value.down {" -A 2 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "text-shadow"; then
    echo "✅ 下跌涨跌幅添加了文字阴影: text-shadow (绿色)"
else
    echo "❌ 下跌涨跌幅未添加文字阴影"
    exit 1
fi

echo ""
echo "[验证10] 得分文字阴影]"
echo "---"
if grep "\.top3-stat-value.high {" -A 2 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "text-shadow"; then
    echo "✅ 得分添加了文字阴影: text-shadow (金色)"
else
    echo "❌ 得分未添加文字阴影"
    exit 1
fi

echo ""
echo "[验证11] 查询统计次数样式]"
echo "---"
if grep "\.stats-item-count {" -A 2 /Users/likan/.openclaw/workspace/stock-analysis.html | grep -q "text-shadow"; then
    echo "✅ 查询次数添加了文字阴影: text-shadow (绿色)"
else
    echo "❌ 查询次数未添加文字阴影"
    exit 1
fi

echo ""
echo "📊 美感优化验证总结"
echo "========================================"
echo "✅ 统一区域: 使用渐变背景和阴影"
echo "✅ 标题样式: 添加了文字阴影和字间距"
echo "✅ Top3容器: 微弱金色背景和边框"
echo "✅ 查询统计容器: 微弱绿色背景和边框"
echo "✅ Top3股票卡片: 优化名称和代码颜色，添加悬停阴影"
echo "✅ Top3信息行: 使用中粗字体，添加字间距"
echo "✅ Top3卡片悬停: 金色边框和阴影效果"
echo "✅ 查询统计卡片: 优化名称颜色，添加悬停阴影"
echo "✅ 涨跌幅和得分: 添加了文字阴影（红涨绿跌金分)"
echo "✅ 查询次数: 添加了文字阴影（绿色）"
echo ""
echo "设计美感提升:"
echo "========================================"
echo "1. 🎨 渐变背景：深色渐变，更有层次感"
echo "2. ✨ 微妙背景色：Top3（金色）和查询统计（绿色）有微妙区分"
echo "3. 🌟 阴影效果：卡片悬停时有阴影，更立体"
echo "4. 🎯 文字阴影：标题、涨跌幅、得分、查询次数都有文字阴影"
echo "5. 📏 字间距：标题和代码都有字间距，更精致"
echo "6. 🎨 颜色层次：不同元素使用不同透明度，更有层次"
echo "7. ✨ 悬停效果：Top3卡片悬停金色边框，查询统计绿色边框"
echo "8. 🌙 边框优化：边框使用浅色，更精致"
echo "9. 📐 布局优化：Grid布局，响应式设计"
echo "10. 🎭 字体优化：标题使用中粗，信息使用中等粗细"
echo ""
echo "请打开浏览器查看效果: http://127.0.0.1:5000/"
echo ""
echo "设计理念:"
echo "========================================"
echo "- Top3区域使用金色系（#ffd700）"
echo "- 查询统计区域使用绿色系（#4CAF50）"
echo "- 背景使用渐变，增加层次感"
echo "- 卡片使用微弱背景色，区分区域"
echo "- 文字使用阴影，增加立体感"
echo "- 悬停效果明显，交互性好"
echo "- 字体颜色有层次，视觉清晰"
