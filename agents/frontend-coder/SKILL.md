# SKILL.md - Frontend Coder Skills

这个文件定义了前端工程师的核心技能和使用方法。

## 技能列表

### 技能1：股票分析页面
**功能**：展示股票分析结果的完整页面

**文件位置**：`/Users/likan/.openclaw/workspace/stock-analysis.html`

**核心功能**：
- 股票搜索输入框
- 评分展示（综合得分、长期、中期、短期）
- 技术指标K线图
- 赢面评估和仓位建议
- 行业和概念板块信息

### 技能2：数据可视化
**功能**：使用ECharts展示K线图和技术指标

**库依赖**：ECharts（CDN引入）

**图表类型**：
- K线图（股价走势）
- 均线图（250日均线）
- 柱状图（可选，如涨停热度）

### 技能3：API数据交互
**功能**：与后端Flask服务通信

**API端点**：
- `GET /api/analyze/<stock_code>` - 获取股票分析数据

**示例代码**：
```javascript
async function analyzeStock(stockCode) {
    try {
        const response = await fetch(`/api/analyze/${stockCode}`);
        const data = await response.json();

        if (data.success) {
            renderAnalysis(data.result);
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('网络错误，请重试');
    }
}
```

### 技能4：响应式布局
**功能**：适配桌面端和移动端

**布局方案**：
- CSS Grid（整体布局）
- Flexbox（组件对齐）
- 媒体查询（断点适配）

**断点设置**：
- 移动端：< 768px
- 平板端：768px - 1024px
- 桌面端：> 1024px

### 技能5：用户体验优化
**功能**：提升用户交互体验

**优化点**：
- 加载动画（骨架屏）
- 错误提示（Toast消息）
- 数据刷新动画
- 键盘快捷键（回车搜索）

## 工作流程

### 任务接收流程
1. 项目经理分配任务（如：新增功能、优化UI）
2. 理解需求，确认设计方案
3. 实现代码
4. 测试验证（多浏览器测试）
5. 记录到记忆文件
6. 报告进度

### 调试流程
1. 复现问题
2. 打开浏览器开发者工具（F12）
3. 查看Console日志
4. 检查Network请求
5. 定位问题原因
6. 修复问题
7. 记录调试过程

### 与后端协作流程
1. 确认API接口定义（参数、返回格式）
2. 实现前端逻辑
3. 联调API接口
4. 验证数据展示
5. 反馈问题和建议

## 调试技巧

### 1. Console.log调试
```javascript
console.log('DEBUG: data =', data);
console.table(data.scores);  // 表格形式展示
```

### 2. Network查看API请求
```javascript
// 在Network标签查看
// Request URL: http://localhost:5000/api/analyze/600000.SH
// Response Data: {...}
```

### 3. 断点调试
```javascript
// 在Sources标签设置断点
function renderAnalysis(data) {
    debugger;  // 断点
    // ...
}
```

### 4. CSS调试
```javascript
// 在Elements标签查看元素样式
// 修改样式实时预览
element.style.color = 'red';
```

## 常见问题

### 问题1：API请求失败
**现象**：Network显示404或500错误
**解决**：
- 检查API端点是否正确
- 检查Flask服务是否启动
- 检查CORS配置

### 问题2：数据展示不正确
**现象**：页面显示的数据与后端返回不一致
**解决**：
- 打印API返回的数据
- 验证数据格式
- 检查数据绑定逻辑

### 问题3：样式错乱
**现象**：页面布局在移动端显示异常
**解决**：
- 检查媒体查询
- 使用Flexbox自适应
- 调整断点设置

### 问题4：性能问题
**现象**：页面加载缓慢
**解决**：
- 减少HTTP请求
- 使用CDN加载外部库
- 优化图片和图标

## 设计规范

### 色彩系统
```css
/* 主色调 */
--primary-color: #3b82f6;    /* 蓝色 */
--success-color: #10b981;    /* 绿色 */
--warning-color: #f59e0b;    /* 黄色 */
--danger-color: #ef4444;     /* 红色 */

/* 中性色 */
--text-primary: #1f2937;     /* 主要文字 */
--text-secondary: #6b7280;   /* 次要文字 */
--bg-primary: #ffffff;       /* 主要背景 */
--bg-secondary: #f3f4f6;     /* 次要背景 */
```

### 字体规范
```css
/* 字体大小 */
--font-size-xs: 0.75rem;     /* 12px */
--font-size-sm: 0.875rem;    /* 14px */
--font-size-base: 1rem;      /* 16px */
--font-size-lg: 1.125rem;    /* 18px */
--font-size-xl: 1.25rem;     /* 20px */
--font-size-2xl: 1.5rem;     /* 24px */
--font-size-3xl: 1.875rem;   /* 30px */
```

### 间距规范
```css
/* 间距 */
--spacing-xs: 0.25rem;       /* 4px */
--spacing-sm: 0.5rem;        /* 8px */
--spacing-md: 1rem;          /* 16px */
--spacing-lg: 1.5rem;        /* 24px */
--spacing-xl: 2rem;          /* 32px */
```

## 最佳实践

1. **渐进增强**：先实现核心功能，再添加视觉效果
2. **移动优先**：先设计移动端，再适配桌面端
3. **性能优先**：减少重绘和回流
4. **可访问性**：使用语义化标签，支持屏幕阅读器
5. **代码整洁**：保持HTML、CSS、JavaScript分离

## 文件结构

```
/Users/likan/.openclaw/workspace/
├── stock-analysis.html       # 主页面
├── css/
│   └── styles.css           # 样式文件（可选）
├── js/
│   └── app.js               # 脚本文件（可选）
└── agents/frontend-coder/
    ├── SOUL.md              # 前端工程师灵魂
    ├── SKILL.md             # 前端工程师技能（本文件）
    └── memory/
        └── debug-YYYY-MM-DD.md # 调试记录
```

## UI组件清单

### 1. 搜索框组件
- 输入框
- 搜索按钮
- 历史记录（可选）

### 2. 评分卡片组件
- 综合得分（大号显示）
- 评级标签
- 分数说明

### 3. 技术指标组件
- K线图容器
- 图表控制按钮（缩放、刷新）

### 4. 赢面评估组件
- 赢面百分比（进度条）
- 市值系数
- 情绪周期系数
- 仓位建议

### 5. 行业信息组件
- 行业名称
- 概念板块标签
- 成长系数说明

## 联系项目经理

遇到问题时，通过以下方式联系项目经理：
- 报告当前进度
- 说明遇到的问题
- 提供设计稿或截图
- 等待指令

---

保持创意，构建极致用户体验！🎨
