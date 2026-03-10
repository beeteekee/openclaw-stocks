#!/usr/bin/env python3
"""养家心法选股分析 - 漏斗筛选流程"""

import os
import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 从MEMORY.md中获取的token
TUSHARE_TOKEN = os.getenv("TUSHARE_TOKEN")

# 行业成长系数表
INDUSTRY_GROWTH = {
    # 高成长 (1.0)
    'AI算力': 1.0, '半导体': 1.0, '集成电路': 1.0,
    '新能源车': 1.0, '光伏': 1.0, '储能': 1.0, '未来能源': 1.0,
    '机器人': 1.0, '具身智能': 1.0,
    '航空航天': 1.0, '低空经济': 1.0,
    '生物医药': 1.0,
    '量子计算': 1.0, '脑机接口': 1.0, '6G': 1.0,
    '锂电': 1.0, '锂电池': 1.0, '磷酸铁锂': 1.0, '新能源': 1.0,
    '特斯拉': 1.0, '比亚迪': 1.0, '蔚来': 1.0, '小鹏': 1.0, '理想': 1.0,
    # 中成长 (0.7)
    '医药生物': 0.7, '5G': 0.7, '新材料': 0.7, '高端制造': 0.7, '汽车电子': 0.7,
    '通信设备': 0.7, '通信': 0.7, '元器件': 0.7, '电子': 0.7, '专用设备': 0.7,
    '汽车整车': 0.7, '汽车制造': 0.7,
    # 低成长 (0.3)
    '农业': 0.3, '银行': 0.3, '钢铁': 0.3, '煤炭': 0.3, '白酒': 0.3, '公用事业': 0.3, '食品': 0.3,
    # 无成长 (0.1)
    '综合类': 0.1, '建筑装饰': 0.1, '商业贸易': 0.1, '纺织服装': 0.1, '机械基件': 0.1
}

def get_industry_growth_coefficient(industry, concepts=None):
    """
    根据行业名称和概念板块获取成长系数

    优先匹配概念板块中的高成长概念，如果没有匹配则使用行业字段

    Args:
        industry: 行业名称（来自Tushare的industry字段）
        concepts: 概念板块列表（来自Tushare的concept_detail接口）

    Returns:
        成长系数（1.0, 0.7, 0.3, 0.1）
    """
    # 优先匹配概念板块
    if concepts:
        for concept in concepts:
            concept = str(concept)
            for key, value in INDUSTRY_GROWTH.items():
                if key in concept:
                    print(f"  ✓ 概念匹配: {concept} → {key}（成长系数: {value}）")
                    return value

    # 如果概念没有匹配，再匹配行业字段
    industry = str(industry)
    for key, value in INDUSTRY_GROWTH.items():
        if key in industry:
            print(f"  ✓ 行业匹配: {industry} → {key}（成长系数: {value}）")
            return value

    print(f"  ⚠ 未匹配: {industry}，默认无成长（0.1）")
    return 0.1  # 默认无成长

def basic_filter(stock_info):
    """步骤1: 基础筛选"""
    print("\n" + "="*60)
    print("步骤1: 基础筛选")
    print("="*60)

    # 检查是否ST
    is_st = 'ST' in stock_info['name'] or '*ST' in stock_info['name']

    print(f"股票代码: {stock_info['ts_code']}")
    print(f"股票名称: {stock_info['name']}")
    print(f"所属行业: {stock_info['industry']}")
    print(f"上市日期: {stock_info['list_date']}")

    if is_st:
        print("❌ 基础筛选不通过: ST股票，直接排除")
        return False

    print("✓ 基础筛选通过")
    return True

def industry_growth_evaluation(stock_info, pro):
    """步骤2: 行业成长判定"""
    print("\n" + "="*60)
    print("步骤2: 行业成长判定")
    print("="*60)

    industry = stock_info['industry']
    ts_code = stock_info['ts_code']

    # 获取概念板块信息
    concepts = []
    try:
        concept_df = pro.concept_detail(ts_code=ts_code)
        if len(concept_df) > 0:
            concepts = concept_df['concept_name'].tolist()
            print(f"概念板块: {', '.join(concepts)}")
    except Exception as e:
        print(f"  ⚠ 获取概念板块失败: {e}")

    # 使用行业和概念进行匹配
    growth_coeff = get_industry_growth_coefficient(industry, concepts)

    print(f"\n所属行业: {industry}")
    print(f"成长系数: {growth_coeff}")

    if growth_coeff == 1.0:
        print("🚀 高成长行业（1.0）- 国家战略，需求爆发")
    elif growth_coeff == 0.7:
        print("📈 中成长行业（0.7）- 需求刚性，稳健增长")
    elif growth_coeff == 0.3:
        print("📉 低成长行业（0.3）- 需求饱和，缺乏爆发性")
    else:
        print("⚫ 无成长行业（0.1）- 无核心扩张逻辑")

    return growth_coeff

def financial_quality_evaluation(ts_code, pro):
    """步骤3: 财务质量评分"""
    print("\n" + "="*60)
    print("步骤3: 财务质量评分")
    print("="*60)

    try:
        # 获取最新财务指标
        end_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        start_date = '20240101'

        financial = pro.fina_indicator(ts_code=ts_code,
                                      start_date=start_date,
                                      end_date=end_date)

        if len(financial) == 0:
            print("⚠ 无财务数据，财务质量评分：0分")
            return 0

        # 取最新一期
        latest = financial.iloc[0]

        # 财务指标展示
        print(f"报告期: {latest['end_date']}")
        print(f"ROE（净资产收益率）: {latest.get('roe', 'N/A')}%")
        print(f"毛利率: {latest.get('grossprofit_margin', 'N/A')}%")
        print(f"净利润增长率: {latest.get('profit_to_gr_yoy', 'N/A')}%")
        print(f"营收增长率: {latest.get('or_yoy', 'N/A')}%")
        print(f"资产负债率: {latest.get('debt_to_assets', 'N/A')}%")

        # 简化评分（后续可以细化）
        score = 60  # 基础分

        # ROE加分
        if pd.notna(latest.get('roe')) and latest['roe'] > 10:
            score += 10
            print("✓ ROE>10%: +10分")

        # 营收增长加分
        if pd.notna(latest.get('or_yoy')) and latest['or_yoy'] > 10:
            score += 10
            print("✓ 营收增长>10%: +10分")

        # 净利润增长加分
        if pd.notna(latest.get('profit_to_gr_yoy')) and latest['profit_to_gr_yoy'] > 10:
            score += 10
            print("✓ 净利润增长>10%: +10分")

        score = min(score, 100)  # 最高100分
        print(f"\n财务质量得分: {score}/100")

        return score

    except Exception as e:
        print(f"❌ 获取财务数据失败: {e}")
        return 0

def technical_evaluation(ts_code, pro):
    """步骤4: 技术面评分（缠论买卖点简化版）"""
    print("\n" + "="*60)
    print("步骤4: 技术面评分")
    print("="*60)

    try:
        # 获取近60日K线数据
        start_date = (datetime.now() - timedelta(days=120)).strftime('%Y%m%d')
        end_date = datetime.now().strftime('%Y%m%d')

        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        df = df.sort_values('trade_date')

        if len(df) < 20:
            print("⚠ K线数据不足，技术面评分：0分")
            return 0, 0, 0, 0, 0

        latest = df.iloc[-1]
        latest_trade_date = latest['trade_date']

        # 使用最新交易日获取市值数据
        basic_df = pro.daily_basic(ts_code=ts_code, trade_date=latest_trade_date,
                                   fields='ts_code,total_mv,circ_mv')
        if len(basic_df) > 0:
            total_mv = basic_df.iloc[0]['total_mv'] / 10000  # 万元转亿元
            circ_mv = basic_df.iloc[0]['circ_mv'] / 10000
            print(f"总市值: {total_mv:.2f}亿元")
            print(f"流通市值: {circ_mv:.2f}亿元")
        else:
            total_mv = 0
            circ_mv = 0

        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        df = df.sort_values('trade_date')

        if len(df) < 20:
            print("⚠ K线数据不足，技术面评分：0分")
            return 0, 0, 0, 0, 0

        latest = df.iloc[-1]

        # 基本技术指标
        close = latest['close']
        pre_close = latest['pre_close']
        pct_chg = latest['pct_chg']

        print(f"最新交易日: {latest['trade_date']}")
        print(f"收盘价: {close:.2f}")
        print(f"昨收: {pre_close:.2f}")
        print(f"涨跌幅: {pct_chg:.2f}%")
        print(f"成交量: {latest['vol']:.2f}手")
        print(f"成交额: {latest['amount']:.2f}万元")

        # 计算近10日涨停次数
        recent_df = df.tail(10)
        limit_up_count = len(recent_df[recent_df['pct_chg'] >= 9.5])
        print(f"\n近10日涨停次数（涨幅≥9.5%）: {limit_up_count}次")

        # 涨停热度因子评分
        if limit_up_count == 0:
            limit_up_score = 0
        elif limit_up_count == 1:
            limit_up_score = 40
        elif limit_up_count == 2:
            limit_up_score = 70
        else:
            limit_up_score = 100

        print(f"涨停热度得分: {limit_up_score}/100")

        # 市值扣分逻辑（严格按照养家心法V8.0标准）
        if total_mv > 0:
            if total_mv < 50:
                market_cap_penalty = 0
            elif total_mv < 100:
                market_cap_penalty = 2
            elif total_mv < 200:
                market_cap_penalty = 5
            elif total_mv < 300:
                market_cap_penalty = 8
            elif total_mv < 500:
                market_cap_penalty = 12
            elif total_mv < 1000:
                market_cap_penalty = 18
            elif total_mv < 3000:
                market_cap_penalty = 25
            elif total_mv < 5000:
                market_cap_penalty = 32
            else:
                market_cap_penalty = 40
            print(f"\n市值扣分: -{market_cap_penalty}分（短期操作难度大）")
        else:
            market_cap_penalty = 0

        # 导入技术分析工具，使用标准的技术面评分方法
        from technical_analysis import calculate_technical_score

        # 使用标准的技术面评分方法（250日均线 + 缠论买点）
        tech_result = calculate_technical_score(df)
        score = tech_result['tech_score']

        print(f"\n技术面得分: {score:.1f}/100 (250日均线×50% + 缠论买点×50%)")

        return score, limit_up_count, limit_up_score, market_cap_penalty, total_mv

    except Exception as e:
        print(f"❌ 获取技术数据失败: {e}")
        return 0, 0, 0, 0, 0

def catalyst_logic_evaluation(stock_info, limit_up_count, growth_coeff, concepts=None):
    """催化逻辑评分"""
    print("\n" + "="*60)
    print("催化逻辑评分")
    print("="*60)

    # 根据涨停次数和行业成长系数判断催化逻辑
    if limit_up_count >= 3:
        score = 100
        reason = "国家级战略/技术革命（连续涨停验证）"
    elif growth_coeff >= 0.7:
        score = 80
        reason = "行业周期反转/高成长赛道"
    elif growth_coeff >= 0.3:
        score = 50
        reason = "传统行业复苏"
    else:
        score = 30
        reason = "纯情绪炒作"

    print(f"催化逻辑得分: {score}/100")
    print(f"原因: {reason}")

    return score

def calculate_comprehensive_score(growth_coeff, financial_score, tech_score, limit_up_score, catalyst_score, sentiment_heat_score=None):
    """综合评分"""
    print("\n" + "="*60)
    print("综合评分")
    print("="*60)

    # 题材热度指数 = 近期涨停热度分×30% + 催化逻辑分×30% + 行业成长系数×40%（归一化）
    # 行业成长系数1.0对应100分
    growth_score = growth_coeff * 100
    theme_heat_index = (limit_up_score * 0.3) + (catalyst_score * 0.3) + (growth_score * 0.4)

    print(f"\n题材热度指数: {theme_heat_index:.1f}/100")
    print(f"  ├─ 近期涨停热度: {limit_up_score}/100 (权重30%)")
    print(f"  ├─ 催化逻辑: {catalyst_score}/100 (权重30%)")
    print(f"  └─ 行业成长: {growth_score}/100 (权重40%)")

    # 长期综合得分 = 行业成长系数×50% + 财务质量分×30% + 长期趋势分×20%
    # 简化：用技术面分替代长期趋势分
    long_term_score = (growth_score * 0.5) + (financial_score * 0.3) + (tech_score * 0.2)

    # 中期综合得分 = 题材热度指数×50% + 财务质量分×30% + 中期趋势分×20%
    medium_term_score = (theme_heat_index * 0.5) + (financial_score * 0.3) + (tech_score * 0.2)

    # V10.0: 融合舆情热度分到短期评分
    # 新公式：短期综合得分 = 技术面分×70% + 舆情热度分×20% + 题材热度指数×10%
    if sentiment_heat_score is not None:
        short_term_score = (tech_score * 0.7) + (sentiment_heat_score * 0.2) + (theme_heat_index * 0.1)
        print(f"\n📊 舆情热度得分: {sentiment_heat_score:.1f}/100（已融入短期评分）")
    else:
        # 降级：未提供舆情热度分时，使用旧公式
        short_term_score = (tech_score * 0.6) + (theme_heat_index * 0.4)
        print(f"\n⚠ 舆情热度得分: 未提供（使用降级公式）")

    print(f"\n长期综合得分: {long_term_score:.1f}/100")
    print(f"中期综合得分: {medium_term_score:.1f}/100")
    print(f"短期综合得分: {short_term_score:.1f}/100 (技术面70% + 舆情热度20% + 题材热度10%)")

    # V9.5: 综合得分优化（直接综合得分，市值扣分已在短期评分中体现）
    overall_score = (short_term_score * 0.6) + (medium_term_score * 0.3) + (long_term_score * 0.1)
    print(f"综合得分: {overall_score:.1f}/100 (短期60% + 中期30% + 长期10%)")

    return {
        'long_term': long_term_score,
        'medium_term': medium_term_score,
        'short_term': short_term_score,
        'theme_heat': theme_heat_index,
        'sentiment_heat': sentiment_heat_score
    }

def calculate_win_rate_and_position(overall_score, total_mv, current_emotion='neutral'):
    """
    计算赢面评估和仓位建议（V9.5优化版）

    Args:
        overall_score: 综合得分（0-100）
        total_mv: 总市值（亿元）
        current_emotion: 当前市场情绪周期

    Returns:
        dict: 包含赢面得分、赢面率、仓位建议等
    """
    # 1. 市值系数（市值越大，赢面越低）
    if total_mv < 50:
        mv_coeff = 1.0      # <50亿：超小盘，灵活
    elif total_mv < 100:
        mv_coeff = 0.98    # 50-100亿：小盘，相对灵活
    elif total_mv < 200:
        mv_coeff = 0.95    # 100-200亿：中小盘
    elif total_mv < 300:
        mv_coeff = 0.92    # 200-300亿：中盘
    elif total_mv < 500:
        mv_coeff = 0.88    # 300-500亿：中大盘
    elif total_mv < 1000:
        mv_coeff = 0.82    # 500-1000亿：大盘
    elif total_mv < 3000:
        mv_coeff = 0.75    # 1000-3000亿：超大盘
    elif total_mv < 5000:
        mv_coeff = 0.68    # 3000-5000亿：巨型市值
    else:
        mv_coeff = 0.60    # >5000亿：巨无霸

    # 2. 情绪周期系数
    emotion_coeff = {
        'despair': 0.5,    # 绝望：极高风险
        'recede': 0.7,     # 退潮：高风险
        'climax': 0.6,     # 高潮：中等风险
        'ferment': 0.8,    # 发酵：中低风险
        'start': 1.0,      # 启动：低风险（黄金期）
        'freeze': 0.9,     # 冰点：低风险（拐点期）
        'neutral': 0.75,   # 中性情绪
        'unknown': 0.75    # 未知时使用中性系数
    }

    # 3. 计算赢面（综合得分 × 市值系数 × 情绪周期系数）
    win_rate = (overall_score / 100) * mv_coeff * emotion_coeff.get(current_emotion, 0.75)
    win_rate = max(0, min(1, win_rate))  # 确保在0-1之间

    # 4. 赢面得分（0-100分，用于展示）
    win_score = int(win_rate * 100)

    # 5. 仓位建议（基于赢面和市值）
    # 基础仓位（基于赢面）
    if win_rate < 0.5:
        base_position = 0.0  # 空仓
    elif win_rate < 0.6:
        base_position = 0.05  # 极小仓试错
    elif win_rate < 0.7:
        base_position = 0.2   # ≤20%仓位
    elif win_rate < 0.8:
        base_position = 0.4   # 30%-50%中仓
    elif win_rate < 0.9:
        base_position = 0.6   # 60%-80%中高仓
    else:
        base_position = 0.8   # 80%-100%重仓

    # 市值调整（大市值降低仓位，小市值提高仓位）
    # 市值调整系数：0.5-1.5之间
    if total_mv < 100:
        mv_adjust = 1.5  # 超小盘，可提高仓位
    elif total_mv < 200:
        mv_adjust = 1.2  # 小盘，适当提高仓位
    elif total_mv < 500:
        mv_adjust = 1.0  # 中盘，正常仓位
    elif total_mv < 1000:
        mv_adjust = 0.8  # 大盘，降低仓位
    elif total_mv < 3000:
        mv_adjust = 0.6  # 超大盘，大幅降低仓位
    else:
        mv_adjust = 0.5  # 巨无霸，极低仓位

    # 最终仓位建议
    final_position = base_position * mv_adjust
    final_position = max(0, min(1.0, final_position))  # 确保在0-100%之间

    # 仓位描述
    if final_position == 0:
        position_advice = "空仓"
    elif final_position <= 0.05:
        position_advice = "极小仓试错（≤5%）"
    elif final_position <= 0.2:
        position_advice = f"小仓（约{int(final_position*100)}%）"
    elif final_position <= 0.5:
        position_advice = f"中仓（约{int(final_position*100)}%）"
    elif final_position <= 0.8:
        position_advice = f"中高仓（约{int(final_position*100)}%）"
    else:
        position_advice = "重仓（约80%-100%）"

    return {
        'win_score': win_score,
        'win_rate': win_rate,
        'mv_coeff': mv_coeff,
        'emotion_coeff': emotion_coeff.get(current_emotion, 0.75),
        'position_advice': position_advice,
        'final_position': final_position
    }

def analyze_stock(stock_code):
    """完整分析流程"""
    print("\n" + "="*60)
    print(f"养家心法选股分析 - {stock_code}")
    print("="*60)

    # 初始化API
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()

    # 获取股票基本信息
    stock_info = pro.stock_basic(ts_code=stock_code,
                                  fields='ts_code,symbol,name,area,industry,list_date')
    if len(stock_info) == 0:
        print(f"❌ 未找到股票 {stock_code}")
        return

    stock_info = stock_info.iloc[0]

    # 步骤1: 基础筛选
    if not basic_filter(stock_info):
        return

    # 步骤2: 行业成长判定
    growth_coeff = industry_growth_evaluation(stock_info, pro)

    # 步骤3: 财务质量评分
    financial_score = financial_quality_evaluation(stock_code, pro)

    # 步骤4: 技术面评分
    tech_score, limit_up_count, limit_up_score, market_cap_penalty, total_mv = technical_evaluation(stock_code, pro)

    # 催化逻辑评分
    catalyst_score = catalyst_logic_evaluation(stock_info, limit_up_count, growth_coeff)

    # 步骤5: 舆情热度分析（V10.0新增）
    from sentiment_analysis import calculate_sentiment_score

    # 获取概念板块信息（前面已经获取过，这里直接使用）
    concepts = []
    try:
        concept_df = pro.concept_detail(ts_code=stock_code)
        if len(concept_df) > 0:
            concepts = concept_df['concept_name'].tolist()
    except Exception as e:
        print(f"⚠ 获取概念板块失败: {e}")

    sentiment_result = calculate_sentiment_score(stock_code, stock_info['name'],
                                                   limit_up_count, growth_coeff, concepts)
    sentiment_heat_score = sentiment_result['sentiment_heat_score']

    # 步骤6: 龙头识别优化（V10.2新增）
    from dragon_leader_identifier import DragonLeaderIdentifier

    dragon_identifier = DragonLeaderIdentifier()
    dragon_result = dragon_identifier.identify_leader(
        stock_code=stock_code,
        stock_name=stock_info['name'],
        industry=stock_info['industry'],
        limit_up_count=limit_up_count,
        growth_coeff=growth_coeff,
        concepts=concepts,
        market_cap=total_mv,
        limit_up_time=None  # TODO: 需要从K线数据中获取封板时间
    )

    # 综合评分
    scores = calculate_comprehensive_score(growth_coeff, financial_score, tech_score,
                                          limit_up_score, catalyst_score, sentiment_heat_score)

    # 计算综合得分（V9.5）
    overall_score = (scores['short_term'] * 0.6) + (scores['medium_term'] * 0.3) + (scores['long_term'] * 0.1)

    # V9.5: 赢面评估和仓位建议
    print("\n" + "="*60)
    print("赢面评估与仓位建议（V9.5优化版）")
    print("="*60)

    win_result = calculate_win_rate_and_position(overall_score, total_mv, current_emotion='neutral')

    print(f"\n综合得分: {overall_score:.1f}/100")
    print(f"赢面得分: {win_result['win_score']}/100")
    print(f"市值系数: {win_result['mv_coeff']:.2f}")
    print(f"情绪系数: {win_result['emotion_coeff']:.2f}")
    print(f"赢面率: {win_result['win_rate']*100:.1f}%")
    print(f"仓位建议: {win_result['position_advice']}")

    # 最终结论
    print("\n" + "="*60)
    print("分析结论")
    print("="*60)

    if overall_score >= 75:
        print("✅ 综合评级：优秀（综合得分≥75）")
        print(f"   建议：符合养家心法核心标准，可纳入观察池")
    elif overall_score >= 60:
        print("⚠️ 综合评级：良好（综合得分≥60）")
        print(f"   建议：有一定投资价值，需结合具体策略")
    else:
        print("❌ 综合评级：一般（综合得分<60）")
        print(f"   建议：暂不纳入选股池")

    print("\n" + "="*60)
    print("分析完成")
    print("="*60)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        stock_code = sys.argv[1]
    else:
        stock_code = '000001.SZ'  # 默认分析平安银行

    analyze_stock(stock_code)
