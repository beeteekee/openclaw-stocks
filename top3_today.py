#!/usr/bin/env python3
"""选出今天评分最靠前的三个股票（排除北交所和科创板）"""

import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

TUSHARE_TOKEN = "e2e547ffbac099527efcaaa0072f0a3adea8eb8fd9efba3b65da7518"

# 行业成长系数表
INDUSTRY_GROWTH = {
    # 高成长 (1.0)
    'AI算力': 1.0, '半导体': 1.0, '新能源车': 1.0, '光伏': 1.0, '机器人': 1.0,
    '锂电': 1.0, '锂电池': 1.0, '磷酸铁锂': 1.0, '储能': 1.0, '新能源': 1.0,
    '特斯拉': 1.0, '比亚迪': 1.0, '蔚来': 1.0, '小鹏': 1.0, '理想': 1.0,
    # 中成长 (0.7)
    '医药生物': 0.7, '5G': 0.7, '6G': 0.7, '新材料': 0.7, '高端制造': 0.7, '汽车电子': 0.7,
    '通信设备': 0.7, '通信': 0.7, '元器件': 0.7, '电子': 0.7, '专用设备': 0.7,
    '汽车整车': 0.7, '汽车制造': 0.7,
    # 低成长 (0.3)
    '农业': 0.3, '银行': 0.3, '钢铁': 0.3, '煤炭': 0.3, '白酒': 0.3, '公用事业': 0.3, '食品': 0.3,
    # 无成长 (0.1)
    '综合类': 0.1, '建筑装饰': 0.1, '商业贸易': 0.1, '纺织服装': 0.1, '机械基件': 0.1
}

def get_industry_growth_coefficient(industry, concepts=None):
    """根据行业名称和概念板块获取成长系数"""
    # 优先匹配概念板块
    if concepts:
        for concept in concepts:
            concept = str(concept)
            for key, value in INDUSTRY_GROWTH.items():
                if key in concept:
                    return value

    # 如果概念没有匹配，再匹配行业字段
    industry = str(industry)
    for key, value in INDUSTRY_GROWTH.items():
        if key in industry:
            return value

    return 0.1  # 默认无成长

def get_250_day_avg(df):
    """计算250日均线价格"""
    if len(df) < 250:
        return None
    return df['close'].tail(250).mean()

def calculate_financial_score_v2(financial, industry=None):
    """
    计算财务质量得分（优化版V2.0）

    改进点：
    1. 数据缺失时使用替代指标估算
    2. 调整成长性评分，对成熟行业更友好
    3. 增加ROE和毛利率的额外加分
    4. 增加盈利质量综合评分

    评分结构（0-120分，最终归一化到100分）：
    - 盈利能力（50分）：ROE 20分 + 毛利率 15分 + 净利率 10分 + 盈利质量 5分
    - 成长性（30分）：营收增长 15分 + 净利润增长 15分
    - 安全性（25分）：资产负债率 15分 + 流动比率 5分 + 财务稳健性 5分
    - 成熟行业奖励（15分）：针对茅台等成熟期公司的额外加分
    """
    financial_score = 0
    financial_data = {}

    if len(financial) == 0:
        return 0, financial_data

    latest = financial.iloc[0]

    # 提取财务数据
    roe = latest.get('roe')
    grossprofit_margin = latest.get('grossprofit_margin')
    netprofit_margin = latest.get('netprofit_margin')
    profit_to_gr_yoy = latest.get('profit_to_gr_yoy')
    or_yoy = latest.get('or_yoy')
    debt_to_assets = latest.get('debt_to_assets')
    current_ratio = latest.get('current_ratio')
    ocf_to_profit = latest.get('ocf_to_profit')

    financial_data = {
        'roe': roe,
        'grossprofit_margin': grossprofit_margin,
        'profit_to_gr_yoy': profit_to_gr_yoy,
        'or_yoy': or_yoy,
        'debt_to_assets': debt_to_assets,
        'current_ratio': current_ratio,
        'ocf_to_profit': ocf_to_profit,
        'end_date': latest['end_date']
    }

    # ========== 盈利能力（50分） ==========

    # ROE评分（20分）
    if pd.notna(roe):
        if roe > 30:
            financial_score += 20  # 极优秀
        elif roe > 25:
            financial_score += 18  # 优秀
        elif roe > 20:
            financial_score += 15  # 优秀
        elif roe > 15:
            financial_score += 12  # 良好
        elif roe > 10:
            financial_score += 8  # 一般
        elif roe > 5:
            financial_score += 4  # 较差
        # ROE ≤ 5%: 0分

    # 毛利率评分（15分）
    if pd.notna(grossprofit_margin):
        if grossprofit_margin > 80:
            financial_score += 15  # 极高毛利（茅台类）
        elif grossprofit_margin > 50:
            financial_score += 15  # 高毛利
        elif grossprofit_margin > 40:
            financial_score += 12  # 良好
        elif grossprofit_margin > 30:
            financial_score += 8  # 一般
        elif grossprofit_margin > 20:
            financial_score += 4  # 较低
        # 毛利率 ≤ 20%: 0分

    # 净利率评分（10分）
    if pd.notna(netprofit_margin):
        if netprofit_margin > 30:
            financial_score += 10  # 极优秀
        elif netprofit_margin > 20:
            financial_score += 10  # 优秀
        elif netprofit_margin > 15:
            financial_score += 10  # 优秀
        elif netprofit_margin > 10:
            financial_score += 8  # 良好
        elif netprofit_margin > 5:
            financial_score += 5  # 一般
        # 净利率 ≤ 5%: 0分
    else:
        # 数据缺失：用毛利率估算净利率（假设净利率约为毛利率的50-70%）
        if pd.notna(grossprofit_margin) and grossprofit_margin > 30:
            financial_score += 8  # 高毛利公司，净利率通常较高

    # 盈利质量综合评分（5分）- 新增
    # 综合考虑ROE、毛利率、资产负债率
    quality_score = 0
    if pd.notna(roe) and pd.notna(grossprofit_margin):
        # 超高ROE + 超高毛利率 = 顶级公司
        if roe > 25 and grossprofit_margin > 80:
            quality_score += 5
        # 高ROE + 高毛利率 = 优秀公司
        elif roe > 20 and grossprofit_margin > 50:
            quality_score += 4
        # 中等ROE + 中等毛利率 = 良好公司
        elif roe > 15 and grossprofit_margin > 30:
            quality_score += 3
        # 高ROE但毛利率一般
        elif roe > 20:
            quality_score += 2
        # 高毛利率但ROE一般
        elif grossprofit_margin > 50:
            quality_score += 2

    if quality_score > 0:
        financial_score += quality_score
        financial_data['quality_bonus'] = quality_score

    # ========== 成长性（30分）- 优化版 ==========

    # 判断是否为成熟行业
    mature_industries = ['白酒', '银行', '公用事业', '食品']
    is_mature = any(ind in str(industry) if industry else '' for ind in mature_industries)

    # 营收增长评分（15分）
    if pd.notna(or_yoy):
        if is_mature:
            # 成熟行业标准更低
            if or_yoy > 15:
                financial_score += 15  # 高成长
            elif or_yoy > 10:
                financial_score += 12  # 良好
            elif or_yoy > 5:
                financial_score += 10  # 稳定增长（茅台6.36%能得10分）
            elif or_yoy > 0:
                financial_score += 6  # 缓慢增长
            elif or_yoy <= 0:
                financial_score -= 3  # 倒退（扣分）
        else:
            # 成长行业标准
            if or_yoy > 30:
                financial_score += 15  # 高成长
            elif or_yoy > 20:
                financial_score += 12  # 良好
            elif or_yoy > 10:
                financial_score += 8  # 一般
            elif or_yoy > 0:
                financial_score += 4  # 缓慢
            elif or_yoy <= 0:
                financial_score -= 5  # 倒退（扣分）
    else:
        # 数据缺失：无法评分
        pass

    # 净利润增长评分（15分）
    if pd.notna(profit_to_gr_yoy):
        if is_mature:
            # 成熟行业标准
            if profit_to_gr_yoy > 15:
                financial_score += 15
            elif profit_to_gr_yoy > 10:
                financial_score += 12
            elif profit_to_gr_yoy > 5:
                financial_score += 10
            elif profit_to_gr_yoy > 0:
                financial_score += 6
            elif profit_to_gr_yoy <= 0:
                financial_score -= 3
        else:
            # 成长行业标准
            if profit_to_gr_yoy > 30:
                financial_score += 15
            elif profit_to_gr_yoy > 20:
                financial_score += 12
            elif profit_to_gr_yoy > 10:
                financial_score += 8
            elif profit_to_gr_yoy > 0:
                financial_score += 4
            elif profit_to_gr_yoy <= 0:
                financial_score -= 5
    else:
        # 数据缺失：用营收增长估算
        if pd.notna(or_yoy) and or_yoy > 0:
            financial_score += min(6, or_yoy)  # 给部分分数

    # ========== 安全性（25分）- 优化版 ==========

    # 资产负债率评分（15分）
    if pd.notna(debt_to_assets):
        if debt_to_assets < 20:
            financial_score += 15  # 极稳健（茅台12.81%）
        elif debt_to_assets < 40:
            financial_score += 15  # 稳健
        elif debt_to_assets < 60:
            financial_score += 10  # 健康
        elif debt_to_assets < 80:
            financial_score += 5  # 较高
        # 资产负债率 ≥ 80%: 0分（高风险）

    # 流动比率评分（5分）
    if pd.notna(current_ratio):
        if current_ratio > 5:
            financial_score += 5  # 极好流动性
        elif current_ratio > 2:
            financial_score += 5  # 流动性好
        elif current_ratio > 1.5:
            financial_score += 3  # 正常
        elif current_ratio > 1:
            financial_score += 1  # 偏低
        # 流动比率 ≤ 1: 0分（流动性差）

    # 财务稳健性评分（5分）- 新增
    # 综合考虑资产负债率和流动比率
    stability_score = 0
    if pd.notna(debt_to_assets) and pd.notna(current_ratio):
        # 超低负债 + 高流动性 = 极稳健
        if debt_to_assets < 20 and current_ratio > 3:
            stability_score += 5
        # 低负债 + 良好流动性 = 稳健
        elif debt_to_assets < 40 and current_ratio > 2:
            stability_score += 4
        # 中等负债 + 正常流动性 = 健康
        elif debt_to_assets < 60 and current_ratio > 1.5:
            stability_score += 3
        # 较高负债 = 有风险
        elif debt_to_assets < 80:
            stability_score += 1

    if stability_score > 0:
        financial_score += stability_score
        financial_data['stability_bonus'] = stability_score

    # ========== 质量与可持续性（5分） ==========

    # 经营现金流/净利润评分（5分）
    if pd.notna(ocf_to_profit):
        if ocf_to_profit > 1:
            financial_score += 5  # 盈利质量高
        elif ocf_to_profit > 0.8:
            financial_score += 3  # 良好
        elif ocf_to_profit > 0.5:
            financial_score += 1  # 一般
        # 经营现金流/净利润 ≤ 0.5: 0分（盈利质量差）
    else:
        # 数据缺失：用ROE和负债率估算
        if pd.notna(roe) and pd.notna(debt_to_assets):
            if roe > 20 and debt_to_assets < 40:
                financial_score += 3  # 高ROE + 低负债 = 现金流应该好

    # ROE连续性评分（0分，因为需要历史数据）
    financial_data['roe_continuity'] = '未知'

    # ========== 归一化到100分 ==========

    # 最高可能得分是120分，需要归一化
    # 但大部分情况下达不到120分
    # 这里采用分段归一化：
    # - 0-90分：不变
    # - 90-105分：100分
    # - 105-120分：100-110分（额外奖励）

    if financial_score > 105:
        financial_score = min(110, financial_score - 10)  # 超优秀公司，最高110分
    elif financial_score > 90:
        financial_score = 100  # 优秀公司，直接给100分

    # 确保评分在0-110范围内
    financial_score = max(0, min(110, financial_score))

    return financial_score, financial_data

def check_chantou_buy_point(df):
    """检查缠论买点（修正版）"""
    if len(df) < 20:
        return (0, '无买点', '数据不足')

    # 计算MACD
    df = df.copy()
    exp12 = df['close'].ewm(span=12, adjust=False).mean()
    exp26 = df['close'].ewm(span=26, adjust=False).mean()
    df['DIF'] = exp12 - exp26
    df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()
    df['MACD'] = (df['DIF'] - df['DEA']) * 2

    # 检查是否当天有买点确认
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # 一类买点：底背驰（修正版：使用正确的局部低点识别）
    if len(df) >= 20:
        # 找出局部低点（前3天和后3天的最小值）
        df['is_local_low'] = False
        for i in range(3, len(df)-3):
            if df.iloc[i]['low'] == df.iloc[i-3:i+4]['low'].min():
                df.iloc[i, df.columns.get_loc('is_local_low')] = True

        local_lows = df[df['is_local_low']]

        if len(local_lows) >= 2:
            latest_low = local_lows.iloc[-1]
            prev_low = local_lows.iloc[-2]

            # 价格创新低且MACD柱子未创新低（绝对值减小）
            if (latest_low['low'] < prev_low['low'] and
                abs(latest_low['MACD']) < abs(prev_low['MACD'])):
                return (100, '一类买点',
                        f'底背驰确认 (价:{prev_low["low"]:.2f}→{latest_low["low"]:.2f}, '
                        f'MACD:{abs(prev_low["MACD"]):.4f}→{abs(latest_low["MACD"]):.4f})')

    # 二类买点：MACD金叉确认
    if prev['DIF'] < prev['DEA'] and latest['DIF'] > latest['DEA']:
        return (100, '二类买点',
                f'MACD金叉确认 (前日DIF:{prev["DIF"]:.4f}<DEA:{prev["DEA"]:.4f}, '
                f'当日DIF:{latest["DIF"]:.4f}>DEA:{latest["DEA"]:.4f})')

    # 三类买点：突破前高
    if len(df) >= 20:
        recent_high = df['high'].tail(20).max()
        if latest['close'] > recent_high * 0.98:
            return (100, '三类买点',
                    f'突破前高确认 (前高:{recent_high:.2f}, 当日:{latest["close"]:.2f})')

    return (0, '无买点', '未发现明确的缠论买点')

def calculate_win_rate(overall_score, total_mv, current_emotion='neutral'):
    """计算赢面率（V9.5优化版）"""
    # 市值系数
    if total_mv < 50:
        mv_coeff = 1.0
    elif total_mv < 100:
        mv_coeff = 0.98
    elif total_mv < 200:
        mv_coeff = 0.95
    elif total_mv < 300:
        mv_coeff = 0.92
    elif total_mv < 500:
        mv_coeff = 0.88
    elif total_mv < 1000:
        mv_coeff = 0.82
    elif total_mv < 3000:
        mv_coeff = 0.75
    elif total_mv < 5000:
        mv_coeff = 0.68
    else:
        mv_coeff = 0.60

    # 情绪周期系数
    emotion_coeff = {
        'despair': 0.5,
        'recede': 0.7,
        'climax': 0.6,
        'ferment': 0.8,
        'start': 1.0,
        'freeze': 0.9,
        'neutral': 0.75,
    }

    # 计算赢面率
    win_rate = (overall_score / 100) * mv_coeff * emotion_coeff.get(current_emotion, 0.75)
    return max(0, min(1, win_rate))

def calculate_position_advice(win_rate, total_mv):
    """计算仓位建议（V9.5优化版）"""
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
        position_advice = '空仓'
    elif final_position <= 0.05:
        position_advice = '极小仓试错'
    elif final_position <= 0.2:
        position_advice = f'小仓（约{int(final_position*100)}%）'
    elif final_position <= 0.5:
        position_advice = f'中仓（约{int(final_position*100)}%）'
    elif final_position <= 0.8:
        position_advice = f'中高仓（约{int(final_position*100)}%）'
    else:
        position_advice = '重仓（约80%-100%）'

    return position_advice

def analyze_stock(ts_code, pro, latest_date=None):
    """分析单只股票，返回完整的评分信息

    Args:
        ts_code: 股票代码
        pro: Tushare API对象
        latest_date: 指定的最新交易日（可选），如果不指定则自动获取最新交易日
    """
    try:
        # 获取股票基本信息
        stock_info = pro.stock_basic(ts_code=ts_code)
        if len(stock_info) == 0:
            return None

        stock_info = stock_info.iloc[0]

        # 基础筛选
        if 'ST' in stock_info['name'] or '*ST' in stock_info['name']:
            return None

        # 获取概念板块
        concepts = []
        try:
            concept_df = pro.concept_detail(ts_code=ts_code)
            if len(concept_df) > 0:
                concepts = concept_df['concept_name'].tolist()
        except:
            pass

        # 获取行情数据
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=500)).strftime('%Y%m%d')

        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        df = df.sort_values('trade_date')

        if len(df) < 50:
            return None

        # 获取最新交易日数据
        if latest_date:
            # 如果指定了最新交易日，使用指定的日期
            df_latest = df[df['trade_date'] == latest_date]
            if len(df_latest) == 0:
                # 如果指定日期没有数据，使用最新的可用数据
                latest = df.iloc[-1]
            else:
                latest = df_latest.iloc[-1]
        else:
            # 否则自动获取最新的交易日数据
            latest = df.iloc[-1]

        # 250日均线
        ma250 = get_250_day_avg(df)
        if ma250 is None:
            return None

        price = latest['close']
        price_to_ma250 = price / ma250

        # 250日均线得分
        if price > ma250:
            if price_to_ma250 > 1.05:
                ma250_score = 100
            elif price_to_ma250 > 1.02:
                ma250_score = 80
            else:
                ma250_score = 60
        else:
            if price_to_ma250 > 0.98:
                ma250_score = 40
            elif price_to_ma250 > 0.95:
                ma250_score = 20
            else:
                ma250_score = 0

        # 缠论买点
        buy_point_score, buy_point_type, buy_point_desc = check_chantou_buy_point(df)

        # 技术面得分
        tech_score = ma250_score * 0.5 + buy_point_score * 0.5

        # 涨停热度（近10日）
        limit_up_count = len(df.tail(10)[df.tail(10)['pct_chg'] >= 9.5])
        if limit_up_count == 0:
            limit_up_score = 0
        elif limit_up_count == 1:
            limit_up_score = 40
        elif limit_up_count == 2:
            limit_up_score = 70
        else:
            limit_up_score = 100

        # 行业成长系数
        growth_coeff = get_industry_growth_coefficient(stock_info['industry'], concepts)
        long_term_score = growth_coeff * 100

        # 催化逻辑得分
        if growth_coeff >= 1.0:
            catalyst_score = 100
        elif growth_coeff >= 0.7:
            catalyst_score = 80
        elif growth_coeff >= 0.3:
            catalyst_score = 50
        else:
            catalyst_score = 30

        # 题材热度指数
        theme_score = limit_up_score * 0.3 + catalyst_score * 0.3 + long_term_score * 0.4

        # 财务质量（V2.0优化版，与stock_service.py保持一致）
        try:
            financial = pro.fina_indicator(
                ts_code=ts_code,
                start_date=(datetime.now() - timedelta(days=120)).strftime('%Y%m%d'),
                end_date=end_date
            )
            if len(financial) > 0:
                finance_score, _ = calculate_financial_score_v2(financial, stock_info['industry'])
            else:
                finance_score = 0
        except:
            finance_score = 0

        # 中期得分
        mid_term_score = theme_score * 0.5 + finance_score * 0.3 + tech_score * 0.2

        # 短期得分
        emotion_cycle_score = 60
        short_term_score = tech_score * 0.8 + emotion_cycle_score * 0.2

        # 综合得分
        overall_score = short_term_score * 0.6 + mid_term_score * 0.3 + long_term_score * 0.1

        # 市值
        try:
            basic = pro.daily_basic(ts_code=ts_code, trade_date=latest['trade_date'])
            if len(basic) > 0:
                total_mv = basic.iloc[0]['total_mv'] / 10000  # 亿元
            else:
                total_mv = 100
        except:
            total_mv = 100

        # 市值扣分
        if total_mv < 50:
            market_cap_deduction = 0
        elif total_mv < 100:
            market_cap_deduction = 2
        elif total_mv < 200:
            market_cap_deduction = 5
        elif total_mv < 300:
            market_cap_deduction = 8
        elif total_mv < 500:
            market_cap_deduction = 12
        elif total_mv < 1000:
            market_cap_deduction = 18
        elif total_mv < 3000:
            market_cap_deduction = 25
        elif total_mv < 5000:
            market_cap_deduction = 32
        else:
            market_cap_deduction = 40

        short_term_score = max(0, short_term_score - market_cap_deduction)

        # 重新计算综合得分（考虑市值扣分）
        overall_score = short_term_score * 0.6 + mid_term_score * 0.3 + long_term_score * 0.1

        # 赢面率
        win_rate = calculate_win_rate(overall_score, total_mv)

        # 仓位建议
        position_advice = calculate_position_advice(win_rate, total_mv)

        return {
            'ts_code': ts_code,
            'name': stock_info['name'],
            'industry': stock_info['industry'],
            'price': price,
            'pct_chg': latest['pct_chg'],
            'trade_date': latest['trade_date'],  # 添加交易日期
            'total_mv': total_mv,
            'overall_score': overall_score,
            'win_rate': win_rate,
            'position_advice': position_advice,
            'buy_point_type': buy_point_type,
            'buy_point_score': buy_point_score,
            'ma250': ma250,
            'price_above_ma250': price > ma250,
            'long_term_score': long_term_score,
            'mid_term_score': mid_term_score,
            'short_term_score': short_term_score,
            'growth_coeff': growth_coeff,
            'limit_up_count': limit_up_count,
        }

    except Exception as e:
        print(f"分析 {ts_code} 时出错: {e}")
        return None

def main():
    pro = ts.pro_api(TUSHARE_TOKEN)

    print("正在获取沪深A股最新行情...")
    print("="*80)

    # 获取最新交易日
    today = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')

    df = pro.daily(start_date=start_date, end_date=today)

    if len(df) == 0:
        print("未找到行情数据")
        return

    # 获取最新交易日
    latest_date = df['trade_date'].max()
    df_latest = df[df['trade_date'] == latest_date]

    print(f"最新交易日: {latest_date}")
    print(f"交易股票数: {len(df_latest)}")

    # 过滤掉北交所（.BJ）和科创板（688开头）的股票
    df_filtered = df_latest[
        ~df_latest['ts_code'].str.endswith('.BJ') &
        ~df_latest['ts_code'].str.startswith('688.')
    ]

    print(f"过滤北交所和科创板后: {len(df_filtered)}只股票")
    print("="*80)

    # 选择分析策略：分析涨幅前300名
    df_sorted = df_filtered.sort_values('pct_chg', ascending=False)
    top_stocks = df_sorted.head(300)['ts_code'].tolist()

    print(f"\n开始分析涨幅前300名股票...")
    print("="*80)

    results = []
    for i, ts_code in enumerate(top_stocks):
        print(f"[{i+1}/300] 分析 {ts_code}...", end=' ')

        result = analyze_stock(ts_code, pro, latest_date=latest_date)
        if result:
            results.append(result)
            print(f"✓ 赢面:{result['win_rate']*100:.1f}% | 综合:{result['overall_score']:.1f}")
        else:
            print("✗")

    if len(results) == 0:
        print("\n没有找到符合条件的股票")
        return

    # 按综合得分排序
    results_sorted = sorted(results, key=lambda x: x['overall_score'], reverse=True)

    print("\n" + "="*80)
    print(f"综合得分最高的前10只股票（共{len(results)}只）")
    print("="*80)

    for i, stock in enumerate(results_sorted[:10], 1):
        print(f"\n{i}. {stock['name']} ({stock['ts_code']})")
        print(f"   价格: {stock['price']:.2f} | 涨跌幅: {stock['pct_chg']:.2f}% | 市值: {stock['total_mv']:.1f}亿")
        print(f"   综合得分: {stock['overall_score']:.1f} | 赢面率: {stock['win_rate']*100:.1f}%")
        print(f"   买点: {stock['buy_point_type']} | 250线: {stock['ma250']:.2f} | "
              f"价格>250线: {'✓' if stock['price_above_ma250'] else '✗'}")

    print("\n" + "="*80)
    print("🏆 综合得分最高的3只股票")
    print("="*80)

    for i, stock in enumerate(results_sorted[:3], 1):
        print(f"\n{'='*80}")
        print(f"第{i}名：{stock['name']} ({stock['ts_code']})")
        print(f"{'='*80}")
        print(f"价格: {stock['price']:.2f}元 | 涨跌幅: {stock['pct_chg']:.2f}%")
        print(f"总市值: {stock['total_mv']:.1f}亿元")
        print(f"交易日期: {stock['trade_date']}")
        print(f"\n综合得分: {stock['overall_score']:.1f}/100")
        print(f"  长期得分: {stock['long_term_score']:.1f}（行业成长系数: {stock['growth_coeff']}）")
        print(f"  中期得分: {stock['mid_term_score']:.1f}（题材热度+财务质量）")
        print(f"  短期得分: {stock['short_term_score']:.1f}（技术面+情绪周期）")
        print(f"\n技术面:")
        print(f"  250日均线: {stock['ma250']:.2f}")
        print(f"  价格>250线: {'✓ 是' if stock['price_above_ma250'] else '✗ 否'}")
        print(f"  缠论买点: {stock['buy_point_type']} (得分: {stock['buy_point_score']})")
        print(f"  近10日涨停: {stock['limit_up_count']}次")
        print(f"\n赢面评估:")
        print(f"  赢面率: {stock['win_rate']*100:.1f}%")
        print(f"  仓位建议: {stock['position_advice']}")

    # 保存结果到CSV
    df_result = pd.DataFrame(results_sorted)
    df_result.to_csv('top3_today_result.csv', index=False, encoding='utf-8-sig')
    print(f"\n已保存完整结果到 top3_today_result.csv")

if __name__ == '__main__':
    main()
