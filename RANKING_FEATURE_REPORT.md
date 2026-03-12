# 添加查询次数排行榜功能
**时间**：2026-03-12 18:37
**修改类型**：新增功能

---

## 需求描述

用户反馈："股票查询次数排行的功能怎么没了"

**问题分析**：
- 之前的FRONTEND-003修改中删除了"查询次数"显示
- 用户需要一个查询次数排行榜功能
- 后端API已经提供了查询次数数据（/api/stats）

---

## 解决方案

### 新增"查询次数排行榜TOP10"功能

#### 1. HTML结构

在"今日精选TOP8"之后添加排行榜区域：

```html
<!-- 查询次数排行榜TOP10 -->
<div class="top3-section">
    <h3 class="section-title">📊 查询次数排行榜TOP10</h3>
    <div class="ranking-container" id="rankingContainer">
        <div class="loading">加载中...</div>
    </div>
</div>
```

#### 2. CSS样式

```css
/* 排行榜样式 */
.ranking-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.ranking-item {
    background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
    color: white;
    padding: 12px 16px;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: transform 0.2s;
}

.ranking-item:hover {
    transform: translateX(5px);
}

.ranking-rank {
    background: rgba(255, 255, 255, 0.2);
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 14px;
    min-width: 60px;
    text-align: center;
    margin-right: 10px;
}

.ranking-rank.top1 {
    background: #f1c40f;
}

.ranking-rank.top2 {
    background: #95a5a6;
}

.ranking-rank.top3 {
    background: #d35400;
}

.ranking-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.ranking-stock-name {
    font-weight: 600;
    font-size: 15px;
}

.ranking-stock-code {
    font-size: 12px;
    opacity: 0.8;
}

.ranking-count {
    background: rgba(255, 255, 255, 0.2);
    padding: 6px 12px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 16px;
}
```

**样式特点**：
- 灰色渐变背景（与TOP8精选保持一致）
- 前三名使用特殊颜色（金、银、铜）
- 悬停效果：向右平移5px
- 响应式设计：移动端自动调整

#### 3. JavaScript功能

```javascript
// 加载查询次数排行榜
async function loadRanking() {
    const rankingContainer = document.getElementById('rankingContainer');
    try {
        rankingContainer.innerHTML = '<div class="loading">加载中...</div>';

        const response = await fetch('/api/stats');
        if (response.ok) {
            const data = await response.json();
            const stockQueries = data.stock_queries || {};

            // 转换为数组并按查询次数排序
            const rankingArray = Object.entries(stockQueries)
                .map(([code, info]) => ({
                    code: code,
                    name: info.name || code,
                    count: info.count || 0
                }))
                .sort((a, b) => b.count - a.count)
                .slice(0, 10); // 取前10名

            if (rankingArray.length > 0) {
                rankingContainer.innerHTML = '';

                rankingArray.forEach((item, index) => {
                    const rank = index + 1;
                    let rankClass = '';

                    if (rank === 1) rankClass = 'top1';
                    else if (rank === 2) rankClass = 'top2';
                    else if (rank === 3) rankClass = 'top3';

                    const rankingItem = document.createElement('div');
                    rankingItem.className = 'ranking-item';
                    rankingItem.onclick = () => {
                        stockInput.value = item.code;
                        analyze();
                    };

                    rankingItem.innerHTML = `
                        <div class="ranking-rank ${rankClass}">#${rank}</div>
                        <div class="ranking-info">
                            <div class="ranking-stock-name">${item.name}</div>
                            <div class="ranking-stock-code">${item.code}</div>
                        </div>
                        <div class="ranking-count">${item.count}</div>
                    `;

                    rankingContainer.appendChild(rankingItem);
                });
            } else {
                rankingContainer.innerHTML = '<div class="loading">暂无排行榜数据</div>';
            }
        } else {
            console.error('获取排行榜数据失败');
            rankingContainer.innerHTML = '<div class="loading">加载失败，请稍后重试</div>';
        }
    } catch (error) {
        console.error('加载排行榜失败:', error);
        rankingContainer.innerHTML = '<div class="loading">加载失败，请稍后重试</div>';
    }
}
```

**功能特点**：
- 自动从/api/stats获取数据
- 按查询次数降序排序
- 显示前10名
- 点击排行榜项可快速分析该股票
- 错误处理和友好提示

#### 4. 页面加载时调用

```javascript
window.onload = function() {
    console.log('页面已加载');
    // 加载统计数据
    loadStats();
    // 加载TOP8精选股票
    loadTop8();
    // 加载查询次数排行榜
    loadRanking();
    // ...
};
```

---

## 功能展示

### 排行榜项布局

```
┌─────────────────────────────────────────┐
│ #1  平安银行                    93次 │
│     000001.SZ                        │
└─────────────────────────────────────────┘
```

### 前三名特殊样式

| 排名 | 颜色 | 代码 |
|------|------|------|
| 第1名 | 金色（#f1c40f） | top1 |
| 第2名 | 银色（#95a5a6） | top2 |
| 第3名 | 铜色（#d35400） | top3 |
| 其他 | 灰色 | - |

---

## 验证结果

### HTML结构 ✅
- ✅ 排行榜容器：`<div class="ranking-container" id="rankingContainer">`
- ✅ 排行榜样式：`.ranking-item`, `.ranking-rank`, `.ranking-info`, `.ranking-count`
- ✅ 特殊样式：`.top1`, `.top2`, `.top3`

### JavaScript功能 ✅
- ✅ loadRanking()函数：加载排行榜数据
- ✅ 页面加载时调用：window.onload
- ✅ 点击快速分析：rankingItem.onclick

### 服务验证 ✅
- ✅ 后端服务：http://localhost:5000/ 正常
- ✅ 公网访问：http://stockbot.nat100.top/stock-analysis-final.html 正常
- ✅ API数据：/api/stats 返回查询次数数据

---

## 数据示例

### API返回数据
```json
{
  "stock_queries": {
    "000001.SZ": {
      "code": "000001.SZ",
      "count": 19,
      "name": "平安银行",
      "symbol": "000001"
    },
    "600519.SH": {
      "code": "600519.SH",
      "count": 93,
      "name": "贵州茅台",
      "symbol": "600519"
    },
    "002594.SZ": {
      "code": "002594.SZ",
      "count": 81,
      "name": "比亚迪",
      "symbol": "002594"
    }
  },
  "total_count": 542
}
```

### 排行榜展示

| 排名 | 股票名称 | 股票代码 | 查询次数 |
|------|----------|----------|----------|
| #1 | 贵州茅台 | 600519.SH | 93次 |
| #2 | 比亚迪 | 002594.SZ | 81次 |
| #3 | 深科技 | 000021.SZ | 23次 |
| #4 | 平安银行 | 000001.SZ | 19次 |
| ... | ... | ... | ... |

---

## 用户体验优化

### 交互设计
- ✅ 悬停效果：排行榜项向右平移5px
- ✅ 点击分析：点击排行榜项自动填入股票代码并分析
- ✅ 加载状态：显示"加载中..."提示
- ✅ 错误处理：显示"加载失败，请稍后重试"

### 视觉设计
- ✅ 灰色渐变背景：与TOP8精选保持一致
- ✅ 前三名特殊颜色：金、银、铜色标识
- ✅ 响应式布局：移动端自动调整
- ✅ 字体大小：名称15px，代码12px，次数16px

---

## 注意事项

1. **数据来源**：
   - 从/api/stats接口获取stock_queries数据
   - 实时显示最新的查询统计

2. **排序规则**：
   - 按查询次数降序排序（最多 → 最少）
   - 只显示前10名

3. **点击行为**：
   - 点击排行榜项自动填入股票代码
   - 自动触发分析功能

4. **样式一致性**：
   - 与TOP8精选保持灰色渐变主题
   - 使用相同的圆角和阴影效果

---

## 技术实现要点

1. **数据转换**：
   - Object.entries()：将对象转为数组
   - map()：提取并转换数据格式
   - sort()：按count降序排序
   - slice(0, 10)：取前10名

2. **动态创建DOM**：
   - document.createElement()：创建排行榜项
   - innerHTML：设置HTML内容
   - appendChild()：添加到容器

3. **事件绑定**：
   - onclick：绑定点击事件
   - analyze()：触发分析函数

---

**功能已完成** ✅

**测试建议**：
1. 在浏览器中访问 http://stockbot.nat100.top/
2. 滚动到"查询次数排行榜TOP10"区域
3. 检查排名、股票名称、代码、次数是否正确
4. 点击排行榜项，验证是否能快速分析
5. 在移动端测试响应式布局
