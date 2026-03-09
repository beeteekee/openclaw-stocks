# SKILL.md - Backend Coder Skills

这个文件定义了后端Python工程师的核心技能和使用方法。

## 技能列表

### 技能1：股票数据分析API
**功能**：提供股票分析REST API接口

**使用方法**：
```python
# 启动服务
cd /Users/likan/.openclaw/workspace
python stock_service.py

# 访问API
curl http://localhost:5000/api/analyze/600000.SH
```

**API端点**：
- `GET /api/analyze/<stock_code>` - 分析指定股票
- `POST /api/analyze` - 批量分析股票
- `GET /api/stats` - 获取查询统计

### 技能2：选股分析核心逻辑
**功能**：执行养家心法漏斗筛选流程

**使用方法**：
```bash
# 命令行分析
python analyze_stock.py 600000.SH

# 查看帮助
python analyze_stock.py --help
```

**输出内容**：
- 步骤1：基础筛选
- 步骤2：行业成长判定
- 步骤3：股价位置筛选
- 步骤4：财务质量评分
- 步骤5：技术面评分
- 步骤6：综合评分

### 技能3：技术分析算法
**功能**：计算技术指标和识别买卖点

**实现位置**：`/Users/likan/.openclaw/workspace/technical_analysis.py`

**算法列表**：
- `calculate_ma250()` - 计算250日均线
- `calculate_macd()` - 计算MACD指标
- `detect_divergence()` - 检测背驰信号
- `identify_bottom_fractal()` - 识别底分型
- `classify_buy_point()` - 分类缠论买点

### 技能4：行业成长系数匹配
**功能**：根据行业和概念板块匹配成长系数

**核心函数**：`get_industry_growth_coefficient(industry, concepts)`

**匹配优先级**：
1. 优先匹配概念板块中的高成长概念
2. 如果概念没有匹配，再匹配行业字段
3. 默认返回0.1（无成长）

### 技能5：数据源管理
**功能**：管理Tushare API token和数据获取

**配置位置**：`TUSHARE_TOKEN = os.getenv("TUSHARE_TOKEN")`

**注意**：token保存在MEMORY.md中，不要泄露

## 工作流程

### 任务接收流程
1. 项目经理分配任务（如：修复bug、添加新功能）
2. 理解需求，确认技术方案
3. 实现代码
4. 测试验证
5. 记录到记忆文件
6. 报告进度

### 调试流程
1. 复现问题
2. 添加调试日志
3. 定位根本原因
4. 修复问题
5. 验证修复效果
6. 记录调试过程

### 与前端协作流程
1. 接收前端agent的API需求
2. 确认API接口定义（参数、返回格式）
3. 实现API接口
4. 提供API文档（示例）
5. 联调测试
6. 修复bug

## 调试技巧

### 1. 使用print调试
```python
print(f"DEBUG: stock_info = {stock_info}")
print(f"DEBUG: industry_growth = {industry_growth}")
```

### 2. 查看Tushare API返回
```python
df = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
print(df.head())  # 查看数据格式
```

### 3. 验证数据完整性
```python
if df is None or len(df) == 0:
    print("⚠️ 数据为空")
    return
```

### 4. 异常捕获
```python
try:
    # 尝试代码
    result = some_function()
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
```

## 常见问题

### 问题1：Tushare API限流
**现象**：接口返回限流错误
**解决**：添加请求间隔，使用缓存减少API调用

### 问题2：数据格式不匹配
**现象**：前端无法解析后端返回
**解决**：检查API返回格式，使用json.dumps确保JSON格式正确

### 问题3：计算逻辑错误
**现象**：评分计算结果不正确
**解决**：添加中间结果print，逐步验证计算过程

### 问题4：性能问题
**现象**：API响应缓慢
**解决**：使用缓存，优化数据库查询，减少重复计算

## 最佳实践

1. **先测试，后提交**：每次修改后都要测试功能
2. **记录日志**：重要操作记录到日志文件
3. **代码审查**：自己review代码，检查潜在问题
4. **文档更新**：修改API时同步更新文档
5. **版本控制**：重要修改前备份原文件

## 文件结构

```
/Users/likan/.openclaw/workspace/
├── stock_service.py           # Flask API服务
├── analyze_stock.py           # 选股分析核心逻辑
├── technical_analysis.py      # 技术分析算法
├── query_stats.json           # 查询统计数据
└── agents/backend-coder/
    ├── SOUL.md                # 后端工程师灵魂
    ├── SKILL.md               # 后端工程师技能（本文件）
    └── memory/
        └── debug-YYYY-MM-DD.md # 调试记录
```

## 联系项目经理

遇到问题时，通过以下方式联系项目经理：
- 报告当前进度
- 说明遇到的问题
- 提供可能的解决方案
- 等待指令

---

保持专注，写好每一行代码！💻
