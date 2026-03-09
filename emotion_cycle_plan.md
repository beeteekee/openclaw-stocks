# 情绪周期分析方案 - 重新评估与细化

## 当前实现的问题

### 1. 数据维度过于单一
**当前：** 只基于上证指数涨跌幅

**缺失的核心数据：**
- 涨停板数量（衡量市场热度）
- 跌停板数量（衡量恐慌程度）
- 核按钮数量（跌幅>5%，衡量亏钱效应）
- 大幅上涨数量（涨幅>5%，衡量赚钱效应）
- 市场总成交额（衡量资金活跃度）
- 换手率（衡量市场活跃度）
- 主力资金净流入（衡量机构态度）

### 2. 判断逻辑过于简单
**当前：**
- 当日涨跌幅 + 近3日累计涨跌
- 硬编码阈值（如>2%大涨，<-2%大跌）

**问题：**
- 没有考虑市场的整体氛围
- 无法区分单日暴涨和持续上涨
- 无法识别震荡市中的情绪转换
- 阈值设定不够科学

### 3. 时间范围不足
**当前：** 只看最近10天的数据

**问题：**
- 无法识别更长期的趋势
- 无法判断情绪的转换节点
- 缺少历史对比

### 4. 缺少板块和龙头效应
**当前：** 只看上证指数，整体判断

**问题：**
- 无法识别板块轮动
- 无法识别龙头炸板对市场的影响
- 无法识别领涨板块的情绪

---

## 改进方案 - 多维度情绪评估体系

### 核心原则
基于养家心法V8.0的情绪周期理论，结合实际市场数据，建立科学、客观的情绪评估体系。

### 情绪周期定义

| 阶段 | 市场特征 | 情绪特征 | 操作策略 | 评分 |
|------|---------|---------|---------|------|
| **冰点** | 涨停板极少，跌停板多，核按钮频现 | 极度恐慌，无人敢买 | 准备抄底，等待拐点 | 100 |
| **启动** | 涨停板开始增加，出现连板 | 情绪回暖，资金试探 | 大胆出击，黄金期 | 80 |
| **发酵** | 涨停板多，连板高度提升，板块效应明显 | 情绪高涨，赚钱效应扩散 | 控制仓位，参与但谨慎 | 60 |
| **高潮** | 涨停板数量多，连板高度高，市场亢奋 | 情绪一致，全民追高 | 减仓或空仓，准备卖出 | 40 |
| **退潮** | 龙头炸板，连板断板，亏钱效应显现 | 情绪分化，分歧加大 | 减仓或空仓，观望 | 20 |
| **绝望** | 跌停板多，核按钮频现，无连板 | 极度恐慌，不计成本出逃 | 观望等待，不动手 | 0 |

---

## 多维度评分体系

### 维度1：涨停热度（30分）

#### 1.1 涨停板数量（15分）
- 涨停板数量 > 100：15分（市场热度高）
- 涨停板数量 50-100：12分（热度良好）
- 涨停板数量 20-50：8分（热度一般）
- 涨停板数量 10-20：4分（热度低）
- 涨停板数量 < 10：0分（极度冷淡）

#### 1.2 连板高度（10分）
- 最高连板 ≥ 7板：10分（市场极热）
- 最高连板 5-6板：8分（市场热）
- 最高连板 3-4板：5分（市场升温）
- 最高连板 2板：3分（市场一般）
- 最高连板 = 1板：0分（市场冷淡）

#### 1.3 板块效应（5分）
- 有明显领涨板块，且多只涨停：5分
- 有领涨板块，涨停数量一般：3分
- 板块轮动快，无明确领涨：1分
- 无板块效应：0分

### 维度2：亏钱效应（30分）

#### 2.1 跌停板数量（15分）
- 跌停板数量 < 5：15分（亏钱效应弱）
- 跌停板数量 5-20：10分（亏钱效应一般）
- 跌停板数量 20-50：5分（亏钱效应明显）
- 跌停板数量 50-100：2分（亏钱效应强）
- 跌停板数量 > 100：0分（亏钱效应极强）

#### 2.2 核按钮数量（10分）
- 核按钮（跌幅>5%）数量 < 20：10分（恐慌程度低）
- 核按钮数量 20-50：7分（恐慌程度一般）
- 核按钮数量 50-100：3分（恐慌程度高）
- 核按钮数量 > 100：0分（恐慌程度极高）

#### 2.3 炸板率（5分）
- 炸板率 < 20%：5分（分歧小）
- 炸板率 20-40%：3分（分歧一般）
- 炸板率 40-60%：1分（分歧大）
- 炸板率 > 60%：0分（分歧极大）

### 维度3：资金活跃度（20分）

#### 3.1 市场成交额（10分）
- 成交额 > 1.5万亿：10分（资金活跃）
- 成交额 1-1.5万亿：8分（资金较活跃）
- 成交额 0.8-1万亿：5分（资金一般）
- 成交额 0.5-0.8万亿：3分（资金较少）
- 成交额 < 0.5万亿：0分（资金冷淡）

#### 3.2 换手率（10分）
- 换手率 > 2%：10分（市场活跃）
- 换手率 1.5-2%：8分（市场较活跃）
- 换手率 1-1.5%：5分（市场一般）
- 换手率 0.8-1%：3分（市场较冷）
- 换手率 < 0.8%：0分（市场冷淡）

### 维度4：趋势指标（20分）

#### 4.1 指数表现（10分）
- 当日指数涨幅 > 2%：10分（强势上涨）
- 当日指数涨幅 1-2%：8分（上涨）
- 当日指数涨幅 0-1%：5分（微涨）
- 当日指数跌幅 0-1%：3分（微跌）
- 当日指数跌幅 > 1%：0分（下跌）

#### 4.2 近3日趋势（10分）
- 近3日累计涨幅 > 5%：10分（持续上涨）
- 近3日累计涨幅 2-5%：8分（上涨趋势）
- 近3日累计涨幅 0-2%：5分（震荡偏强）
- 近3日累计跌幅 0-2%：3分（震荡偏弱）
- 近3日累计跌幅 > 2%：0分（下跌趋势）

---

## 情绪周期判断算法

### 算法流程

```
1. 获取当日市场数据：
   - 涨停板数量
   - 跌停板数量
   - 核按钮数量
   - 炸板率
   - 市场成交额
   - 换手率
   - 指数涨跌幅
   - 近3日累计涨跌

2. 计算各维度得分：
   - 涨停热度得分（30分）
   - 亏钱效应得分（30分）
   - 资金活跃度得分（20分）
   - 趋势指标得分（20分）

3. 计算总分：
   总分 = 涨停热度得分 + 亏钱效应得分 + 资金活跃度得分 + 趋势指标得分

4. 根据总分判断情绪周期：
   - 总分 ≥ 85：高潮（40分）
   - 75 ≤ 总分 < 85：发酵（60分）
   - 60 ≤ 总分 < 75：启动（80分）
   - 40 ≤ 总分 < 60：冰点（100分）
   - 20 ≤ 总分 < 40：退潮（20分）
   - 总分 < 20：绝望（0分）

5. 辅助判断：
   - 如果当日跌停板 > 涨停板 * 2：直接判断为绝望
   - 如果当日涨停板 < 10：直接判断为冰点
   - 如果涨停板 > 100且连续3日上涨：判断为高潮
```

### 特殊情况处理

#### 情绪突变
- 如果昨日是高潮，今日跌停板突增：判断为退潮
- 如果昨日是绝望，今日涨停板突增：判断为启动
- 如果龙头炸板：权重降低涨停热度得分

#### 节假日效应
- 节假日前：成交额权重降低
- 节假日后：成交额权重提高

#### 重大事件
- 重大利好：提高涨停热度权重
- 重大利空：提高亏钱效应权重

---

## 数据获取方案

### Tushare可用的数据

#### 1. 涨停跌停统计
使用 `pro.daily_basic()` 获取每日基本数据：
- `trade_date`：交易日期
- `turnover_rate`：换手率
- `pe_ttm`, `pb`：估值指标

#### 2. 指数数据
使用 `pro.index_daily()` 获取指数数据：
- `ts_code`：指数代码（000001.SH上证指数）
- `close`：收盘价
- `pct_chg`：涨跌幅
- `vol`：成交量
- `amount`：成交额

#### 3. 市场概览数据
使用 `pro.daily()` 获取全市场数据：
- 筛选涨幅 ≥ 9.5%：涨停板
- 筛选跌幅 ≤ -9.5%：跌停板
- 筛选跌幅 ≤ -5%：核按钮

### 数据获取流程

```python
def get_market_emotion_data():
    """获取市场情绪相关数据"""
    try:
        today = datetime.now().strftime('%Y%m%d')

        # 1. 获取指数数据（上证指数）
        index_data = pro.index_daily(
            ts_code='000001.SH',
            start_date=(datetime.now() - timedelta(days=5)).strftime('%Y%m%d'),
            end_date=today
        )

        # 2. 获取全市场数据（筛选当日）
        all_stocks = pro.daily(
            trade_date=today,
            fields='ts_code,pct_chg,close,vol,amount'
        )

        # 3. 计算涨停跌停统计
        limit_up = len(all_stocks[all_stocks['pct_chg'] >= 9.5])
        limit_down = len(all_stocks[all_stocks['pct_chg'] <= -9.5])
        nuclear = len(all_stocks[all_stocks['pct_chg'] <= -5])

        # 4. 计算市场成交额
        total_amount = all_stocks['amount'].sum() / 100000000  # 转换为亿元

        # 5. 计算换手率（需要daily_basic数据）
        basic_data = pro.daily_basic(trade_date=today, fields='ts_code,turnover_rate')
        avg_turnover = basic_data['turnover_rate'].mean()

        return {
            'index_pct_chg': index_data.iloc[-1]['pct_chg'],
            'limit_up_count': limit_up,
            'limit_down_count': limit_down,
            'nuclear_count': nuclear,
            'total_amount': total_amount,
            'avg_turnover': avg_turnover
        }

    except Exception as e:
        print(f"获取市场情绪数据失败: {e}")
        return None
```

---

## 实现优先级

### 第一阶段（核心功能）
1. ✅ 获取指数涨跌幅
2. ✅ 获取涨停跌停数量
3. ✅ 获取核按钮数量
4. ✅ 获取市场成交额
5. ✅ 获取换手率

### 第二阶段（完善功能）
6. 计算连板高度（需要历史数据）
7. 计算炸板率（需要盘中数据）
8. 识别板块效应（需要分类数据）
9. 实现情绪突变检测
10. 添加特殊情况处理

### 第三阶段（高级功能）
11. 龙头股监测
12. 板块轮动分析
13. 主力资金流向
14. 情绪周期预测
15. 历史情绪对比

---

## 代码实现示例

### 完整的 `get_market_emotion` 函数

```python
def get_market_emotion():
    """
    获取当前市场情绪周期
    基于多维度数据综合判断
    """
    try:
        # 获取市场情绪数据
        emotion_data = get_market_emotion_data()

        if not emotion_data:
            return 'freeze', 100

        # 维度1：涨停热度（30分）
        limit_up_score = calculate_limit_up_score(emotion_data)

        # 维度2：亏钱效应（30分）
        loss_effect_score = calculate_loss_effect_score(emotion_data)

        # 维度3：资金活跃度（20分）
        capital_activity_score = calculate_capital_activity_score(emotion_data)

        # 维度4：趋势指标（20分）
        trend_score = calculate_trend_score(emotion_data)

        # 计算总分
        total_score = (limit_up_score + loss_effect_score +
                      capital_activity_score + trend_score)

        # 判断情绪周期
        emotion, emotion_score = judge_emotion_cycle(total_score, emotion_data)

        return emotion, emotion_score

    except Exception as e:
        print(f"获取市场情绪失败: {e}")
        return 'freeze', 100


def calculate_limit_up_score(data):
    """计算涨停热度得分（30分）"""
    score = 0

    # 涨停板数量（15分）
    limit_up = data.get('limit_up_count', 0)
    if limit_up > 100:
        score += 15
    elif limit_up > 50:
        score += 12
    elif limit_up > 20:
        score += 8
    elif limit_up > 10:
        score += 4
    else:
        score += 0

    # 连板高度（10分）
    # TODO: 需要历史数据计算
    score += 5  # 临时给中等分数

    # 板块效应（5分）
    # TODO: 需要板块数据
    score += 2  # 临时给低分

    return score


def calculate_loss_effect_score(data):
    """计算亏钱效应得分（30分）"""
    score = 0

    # 跌停板数量（15分）
    limit_down = data.get('limit_down_count', 0)
    if limit_down < 5:
        score += 15
    elif limit_down < 20:
        score += 10
    elif limit_down < 50:
        score += 5
    elif limit_down < 100:
        score += 2
    else:
        score += 0

    # 核按钮数量（10分）
    nuclear = data.get('nuclear_count', 0)
    if nuclear < 20:
        score += 10
    elif nuclear < 50:
        score += 7
    elif nuclear < 100:
        score += 3
    else:
        score += 0

    # 炸板率（5分）
    # TODO: 需要盘中数据
    score += 2  # 临时给低分

    return score


def calculate_capital_activity_score(data):
    """计算资金活跃度得分（20分）"""
    score = 0

    # 市场成交额（10分）
    amount = data.get('total_amount', 0)
    if amount > 1.5:
        score += 10
    elif amount > 1:
        score += 8
    elif amount > 0.8:
        score += 5
    elif amount > 0.5:
        score += 3
    else:
        score += 0

    # 换手率（10分）
    turnover = data.get('avg_turnover', 0)
    if turnover > 2:
        score += 10
    elif turnover > 1.5:
        score += 8
    elif turnover > 1:
        score += 5
    elif turnover > 0.8:
        score += 3
    else:
        score += 0

    return score


def calculate_trend_score(data):
    """计算趋势指标得分（20分）"""
    score = 0

    # 指数表现（10分）
    index_chg = data.get('index_pct_chg', 0)
    if index_chg > 2:
        score += 10
    elif index_chg > 1:
        score += 8
    elif index_chg > 0:
        score += 5
    elif index_chg > -1:
        score += 3
    else:
        score += 0

    # 近3日趋势（10分）
    # TODO: 需要历史数据
    score += 5  # 临时给中等分数

    return score


def judge_emotion_cycle(total_score, emotion_data):
    """
    根据总分判断情绪周期
    """
    limit_up = emotion_data.get('limit_up_count', 0)
    limit_down = emotion_data.get('limit_down_count', 0)

    # 特殊情况：跌停板远多于涨停板
    if limit_down > limit_up * 2:
        return 'despair', 0

    # 特殊情况：涨停板极少
    if limit_up < 10:
        return 'freeze', 100

    # 根据总分判断
    if total_score >= 85:
        return 'climax', 40
    elif total_score >= 75:
        return 'ferment', 60
    elif total_score >= 60:
        return 'start', 80
    elif total_score >= 40:
        return 'freeze', 100
    elif total_score >= 20:
        return 'recede', 20
    else:
        return 'despair', 0
```

---

## 测试与验证

### 测试场景

#### 场景1：高潮期
- 涨停板 > 100
- 跌停板 < 10
- 成交额 > 1.5万亿
- 指数涨幅 > 2%
- **预期结果：高潮期，40分**

#### 场景2：绝望期
- 涨停板 < 20
- 跌停板 > 100
- 核按钮 > 100
- 指数跌幅 > 2%
- **预期结果：绝望期，0分**

#### 场景3：启动期
- 涨停板 50-100
- 跌停板 5-20
- 成交额 1-1.5万亿
- 指数涨幅 1-2%
- **预期结果：启动期，80分**

### 对比验证

与实际市场表现对比，验证情绪判断的准确性：
- 观察涨停板数量的变化
- 观察连板高度的变化
- 观察亏钱效应的变化
- 观察资金流向的变化

---

## 总结

### 核心改进
1. 从单维度（指数涨跌）到四维度（涨停热度、亏钱效应、资金活跃度、趋势指标）
2. 从硬编码阈值到多指标综合评分
3. 从静态判断到动态检测（情绪突变）
4. 从整体判断到板块和龙头效应

### 实现建议
1. 先实现第一阶段的核心功能
2. 验证数据的准确性和可用性
3. 逐步完善第二阶段功能
4. 长期优化第三阶段的高级功能

### 注意事项
1. Tushare数据有延迟，需要考虑实时性
2. 盘中数据和收盘后数据不同，需要区分
3. 情绪判断是概率性的，不是绝对准确
4. 需要持续优化和调整阈值

---

**结论：当前情绪周期分析过于简单，需要按照上述方案进行重构，建立科学、客观、多维度的情绪评估体系。**
