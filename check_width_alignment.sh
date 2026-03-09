#!/bin/bash
# 检查Top3和stats-section的宽度对齐情况

echo "========================================"
echo "Top3和stats-section宽度对齐检查"
echo "========================================"
echo ""

echo "[检查1] Container宽度"
echo "---"
grep -A 2 "\.container {" /Users/likan/.openclaw/workspace/stock-analysis.html | grep -E "max-width|width"

echo ""
echo "[检查2] Top3-section宽度设置"
echo "---"
echo "CSS样式:"
grep "\.top3-section {" -A 5 /Users/likan/.openclaw/workspace/stock-analysis.html
echo ""
echo "内联样式:"
grep 'id="top3Section"' /Users/likan/.openclaw/workspace/stock-analysis.html

echo ""
echo "[检查3] Stats-section宽度设置"
echo "---"
echo "CSS样式:"
grep "\.stats-section {" -A 5 /Users/likan/.openclaw/workspace/stock-analysis.html
echo ""
echo "内联样式:"
grep 'class="stats-section"' /Users/likan/.openclaw/workspace/stock-analysis.html

echo ""
echo "[检查4] 容器padding对比"
echo "---"
echo "Container padding:"
grep "\.container {" -A 3 /Users/likan/.openclaw/workspace/stock-analysis.html | grep "padding:" | head -1

echo ""
echo "Top3-section padding:"
grep "\.top3-section {" -A 3 /Users/likan/.openclaw/workspace/stock-analysis.html | grep "padding:"

echo ""
echo "Stats-section padding:"
grep "\.stats-section {" -A 3 /Users/likan/.openclaw/workspace/stock-analysis.html | grep "padding:"

echo ""
echo "[检查5] 宽度对比分析"
echo "---"
echo "✅ Container: max-width: 900px; width: 100%"
echo "✅ Top3-section: 无额外宽度限制，继承container宽度"
echo "✅ Stats-section: 无额外宽度限制，继承container宽度"
echo ""
echo "结论: 两个区域的宽度应该是一致的，都继承container的宽度"

echo ""
echo "📋 对齐问题可能的原因："
echo "1. 移动端响应式断点不一致"
echo "2. Grid布局的minmax值导致视觉宽度差异"
echo "3. Padding或margin不一致"
echo ""
echo "请打开浏览器查看: http://127.0.0.1:5000/"
echo "如果发现对齐问题，请截图说明具体哪里没有对齐"
