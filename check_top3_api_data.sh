#!/bin/bash
# 检查Top3 API返回的数据字段

echo "========================================"
echo "检查Top3 API数据字段"
echo "========================================"
echo ""

echo "[检查1] API返回的数据"
echo "---"
curl -s http://127.0.0.1:5000/api/top3-today | python3 -m json.tool | head -100
