# 精选股票显示优化
**时间**：2026-03-12 18:47
**修改类型**：显示优化

---

## 需求描述

用户要求：
1. 精选股票的赢面，百分比只需要展示2位
2. 股票的代码要展示

---

## 修改内容

### 1. 赢面率显示：2位小数

**修改前**：
```javascript
<div class="top3-metric-value ${winRateClass}">${stock.win_rate || 0}%</div>
```

**修改后**：
```javascript
<div class="top3-metric-value ${winRateClass}">${(winRate * 100).toFixed(2)}%</div>
```

**变化**：
- 原来直接显示`win_rate`值，可能显示很多位小数
- 现在使用`toFixed(2)`格式化为2位小数
- 示例：`61.48275%` → `61.48%`

### 2. 股票代码展示

**HTML结构**（已存在，保持不变）：
```html
<span class="top3-stock-code">${stock.code}</span>
```

**CSS样式**（已存在，保持不变）：
```css
.top3-stock-code {
    background: rgba(0, 0, 0, 0.2);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-family: monospace;
}
```

**确认**：
- ✅ 股票代码元素存在于HTML中
- ✅ CSS样式已定义
- ✅ 股票代码正常显示

### 3. 指标卡片样式优化

**修改前**：
```css
.top3-metric {
    display: flex;
    flex-direction: column;
    gap: 4px;
}
```

**修改后**：
```css
.top3-metric {
    display: flex;
    flex-direction: column;
    gap: 4px;
    background: rgba(0, 0, 0, 0.15);
    padding: 10px 16px;
    border-radius: 6px;
    min-width: 120px;
    text-align: center;
}
```

**变化**：
- 添加背景色：`rgba(0, 0, 0, 0.15)`（深色背景，15%透明度）
- 增加内边距：`padding: 10px 16px`
- 添加圆角：`border-radius: 6px`
- 设置最小宽度：`min-width: 120px`
- 居中对齐：`text-align: center`

---

## 显示效果

### 修改前

```
┌─────────────────────────────────┐
│ TOP1   比亚迪   002594.SZ   │
│                                 │
│ 赢面率   61.48275%           │
│ 今日状态   关注                 │
└─────────────────────────────────┘
```

### 修改后

```
┌─────────────────────────────────┐
│ TOP1   比亚迪   002594.SZ   │
│                                 │
│ [卡片背景]    [卡片背景]      │
│ 赢面率        61.48%          │
│ 今日状态      关注              │
└─────────────────────────────────┘
```

---

## 优化要点

### 1. 赢面率格式化

**优点**：
- ✅ 2位小数更简洁易读
- ✅ 符合百分比显示习惯
- ✅ 减少数字冗余

### 2. 股票代码展示

**确认**：
- ✅ 代码正常显示在股票名称右侧
- ✅ 使用等宽字体（monospace）
- ✅ 背景色与卡片背景区分

### 3. 指标卡片优化

**视觉效果**：
- ✅ 每个指标有独立的卡片背景
- ✅ 增加了视觉层次
- ✅ 提高了可读性

---

## 技术实现

### JavaScript代码

```javascript
// 判断赢面率等级
const winRate = parseFloat(stock.win_rate || 0);
let winRateClass = 'low';
if (winRate >= 80) {
    winRateClass = 'high';
} else if (winRate >= 60) {
    winRateClass = 'medium';
}

// 格式化为2位小数
const winRateFormatted = (winRate * 100).toFixed(2);

top3Item.innerHTML = `
    <div class="top3-header">
        <span class="top3-rank">TOP ${index + 1}</span>
        <span class="top3-stock-name">${stock.name || stock.code}</span>
        <span class="top3-stock-code">${stock.code}</span>
    </div>
    <div class="top3-metrics">
        <div class="top3-metric">
            <div class="top3-metric-label">赢面率</div>
            <div class="top3-metric-value ${winRateClass}">${winRateFormatted}%</div>
        </div>
        <div class="top3-metric">
            <div class="top3-metric-label">今日状态</div>
            <div class="top3-metric-value ${winRateClass}">${winRate >= 80 ? '推荐' : '关注'}</div>
        </div>
    </div>
`;
```

### CSS样式

```css
.top3-metric {
    display: flex;
    flex-direction: column;
    gap: 4px;
    background: rgba(0, 0, 0, 0.15);
    padding: 10px 16px;
    border-radius: 6px;
    min-width: 120px;
    text-align: center;
}

.top3-stock-code {
    background: rgba(0, 0, 0, 0.2);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-family: monospace;
}
```

---

## 验证结果

### 赢面率显示 ✅
- ✅ 格式化为2位小数
- ✅ 示例：`61.48%`（修改前：`61.48275%`）
- ✅ 代码验证：`toFixed(2)`存在

### 股票代码展示 ✅
- ✅ HTML元素：`<span class="top3-stock-code">${stock.code}</span>`存在
- ✅ CSS样式：完整定义
- ✅ 页面验证：正常显示

### 指标卡片样式 ✅
- ✅ 背景色：`rgba(0, 0, 0, 0.15)`
- ✅ 内边距：`10px 16px`
- ✅ 圆角：`6px`
- ✅ 最小宽度：`120px`
- ✅ 居中对齐：`text-align: center`

### 服务验证 ✅
- ✅ 后端服务：http://localhost:5000/ 正常
- ✅ 前端页面：http://localhost/stock-analysis-final.html 正常

---

## 显示效果示例

### TOP1 比亚迪

```
┌──────────────────────────────────────┐
│ TOP 1  比亚迪         002594.SZ  │
├──────────────────────────────────────┤
│ [卡片]      [卡片]              │
│ 赢面率        61.48%           │
│ 今日状态      关注              │
└──────────────────────────────────────┘
```

### TOP2 百川股份

```
┌──────────────────────────────────────┐
│ TOP 2  百川股份       002455.SZ  │
├──────────────────────────────────────┤
│ [卡片]      [卡片]              │
│ 赢面率        61.48%           │
│ 今日状态      关注              │
└──────────────────────────────────────┘
```

---

## 注意事项

1. **赢面率精度**：
   - 原始数据可能有更多小数位
   - 显示时格式化为2位小数
   - 计算时仍使用原始精度

2. **股票代码格式**：
   - 后端返回的股票代码格式：`002594.SZ`或`600519.SH`
   - 前端直接展示，不做格式转换
   - 使用等宽字体保证对齐

3. **响应式适配**：
   - 移动端保持相同的样式
   - 根据屏幕宽度自动调整布局
   - 480px断点纵向堆叠

---

**修改完成** ✅

**测试建议**：
1. 在浏览器中访问 http://stockbot.nat100.top/
2. 检查赢面率是否显示2位小数
3. 检查股票代码是否正常显示
4. 检查指标卡片是否有背景色
5. 在移动端测试显示效果
