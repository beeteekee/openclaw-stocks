#!/usr/bin/env python3
"""批量分析全市场股票，找出评分最高的股票"""

import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from technical_analysis import calculate_technical_score

# Tushare Token
TUSHARE_TOKEN = "e2e547ffbac099527efcaaa0072f0a3adea8eb8fd9efba3b65da7518"

# 行业成长系数表
INDUSTRY_GROWTH = {
    # 高成长 (1.0)
    '锂电': 1.0, '锂电池': 1.0, '磷酸铁锂': 1.0, '储能': 1.0, '新能源': 1.0,
    '特斯拉': 1.0, '比亚迪': 1.0, '蔚来': 1.0, '小鹏': 1.0, '理想': 1.0,
    'AI算力': 1.0, '半导体': 1.0, '新能源车': 1.0, '光伏': 1.0, '机器人': 1.0,
    # 中成长 (0.7)
    '医药生物': 0.7, '5G': 0.7, '6G': 0.7, '新材料': 0.7, '高端制造': 0.7, '汽车电子': 0.7,
    '通信设备': 0.7, '通信': 0.7, '元器件': 0.7, '电子': 0.7, '专用设备': 0.7,
    '汽车整车': 0.7, '汽车制造': 0.7,
    # 低成长 (0.3)
    '农业': 0.3, '银行': 0.3, '钢铁': 0.3, '煤炭': 0.3, '白酒': 0.3, '公用事业': 0.3, '食品': 0.3,
    # 无成长 (0.1)
    '综合类': 0.1, '建筑装饰': 0.1, '商业贸易': 0.1, '纺织服装': 0.1, '机械基件': 0.1
}

# 初始化Tushare API
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

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

def get_market_cap_penalty(total_mv):
    """市值扣分逻辑"""
    if total_mv < 50:
        return 0
    elif total_mv < 100:
        return 2
    elif total_mv < 200:
        return 5
    elif total_mv < 300:
        return 8
    elif total_mv < 500:
        return 12
    elif total_mv < 1000:
        return 18
    elif total_mv < 3000:
        return 25
    elif total_mv < 5000:
        return 32
    else:
        return 40

def calculate_financial_score_simple(financial, industry=None):
    """
    简化版财务评分（用于批量分析）

    评分结构（0-100分）：
    - 盈利能力（30分）：ROE 15分 + 毛利率 15分
    - 成长性（30分）：营收增长 15分 + 净利润增长 15分
    - 安全性（30分）：资产负债率 15分 + 流动比率 15分
    - 质量与可持续性（10分）：经营现金流/净利润 10分
    """
    financial_score = 0

    if len(financial) == 0:
        return 0

    latest = financial.iloc[0]

    # 提取财务数据
    roe = latest.get('roe')
    grossprofit_margin = latest.get('grossprofit_margin')
    profit_to_gr_yoy = latest.get('profit_to_gr_yoy')
    or_yoy = latest.get('or_yoy')
    debt_to_assets = latest.get('debt_to_assets')
    current_ratio = latest.get('current_ratio')
    ocf_to_profit = latest.get('ocf_to_profit')

    # ROE评分（15分）
    if pd.notna(roe):
        if roe > 20:
            financial_score += 15
        elif roe > 15:
            financial_score += 12
        elif roe > 10:
            financial_score += 8
        elif roe > 5:
            financial_score += 4

    # 毛利率评分（15分）
    if pd.notna(grossprofit_margin):
        if grossprofit_margin > 50:
            financial_score += 15
        elif grossprofit_margin > 40:
            financial_score += 12
        elif grossprofit_margin > 30:
            financial_score += 8
        elif grossprofit_margin > 20:
            financial_score += 4

    # 营收增长评分（15分）
    if pd.notna(or_yoy):
        if or_yoy > 30:
            financial_score += 15
        elif or_yoy > 20:
            financial_score += 12
        elif or_yoy > 10:
            financial_score += 8
        elif or_yoy > 0:
            financial_score += 4

    # 净利润增长评分（15分）
    if pd.notna(profit_to_gr_yoy):
        if profit_to_gr_yoy > 30:
            financial_score += 15
        elif profit_to_gr_yoy > 20:
            financial_score += 12
        elif profit_to_gr_yoy > 10:
            financial_score += 8
        elif profit_to_gr_yoy > 0:
            financial_score += 4

    # 资产负债率评分（15分）
    if pd.notna(debt_to_assets):
        if debt_to_assets < 40:
            financial_score += 15
        elif debt_to_assets < 60:
            financial_score += 10
        elif debt_to_assets < 80:
            financial_score += 5

    # 流动比率评分（15分）
    if pd.notna(current_ratio):
        if current_ratio > 2:
            financial_score += 15
        elif current_ratio > 1.5:
            financial_score += 10
        elif current_ratio > 1:
            financial_score += 5

    # 经营现金流/净利润评分（10分）
    if pd.notna(ocf_to_profit):
        if ocf_to_profit > 1:
            financial_score += 10
        elif ocf_to_profit > 0.8:
            financial_score += 7
        elif ocf_to_profit > 0.5:
            financial_score += 4

    return financial_score

def get_market_emotion_simple():
    """
    简化版市场情绪判断

    Returns:
        tuple: (情绪周期, 情绪评分)
    """
    try:
        today = datetime.now().strftime('%Y%m%d')

        # 获取指数数据（上证指数）
        index_data = pro.index_daily(
            ts_code='000001.SH',
            start_date=(datetime.now() - timedelta(days=5)).strftime('%Y%m%d'),
            end_date=today
        )

        if len(index_data) == 0:
            return 'unknown', 50

        # 获取全市场数据
        all_stocks = pro.daily(
            trade_date=today,
            fields='ts_code,pct_chg'
        )

        if len(all_stocks) == 0:
            return 'unknown', 50

        # 计算涨停跌停统计
        limit_up = len(all_stocks[all_stocks['pct_chg'] >= 9.5])
        limit_down = len(all_stocks[all_stocks['pct_chg'] <= -9.5])

        # 指数数据
        latest_index = index_data.iloc[-1]
        index_pct_chg = latest_index['pct_chg']

        # 简化判断情绪
        if limit_up > 50 and index_pct_chg > 1:
            emotion = 'start'  # 启动
            emotion_score = 80
        elif limit_up > 100:
            emotion = 'climax'  # 高潮
            emotion_score = 40
        elif limit_down > 20:
            emotion = 'recede'  # 退潮
            emotion_score = 20
        elif limit_up < 10:
            emotion = 'freeze'  # 冰点
            emotion_score = 100
        elif index_pct_chg > 0:
            emotion = 'ferment'  # 发酵
            emotion_score = 60
        else:
            emotion = 'neutral'  # 中性
            emotion_score = 50

        return emotion, emotion_score

    except Exception as e:
        print(f"获取市场情绪失败: {e}")
        return 'neutral', 50

def analyze_single_stock(stock_code, stock_name, industry):
    """
    分析单个股票并返回综合评分

    Returns:
        dict: 分析结果，包括各项评分
    """
    try:
        # 基础筛选
        is_st = 'ST' in stock_name or '*ST' in stock_name
        if is_st:
            return None  # 跳过ST股票

        # 获取概念板块信息（简化：不查询概念板块，使用行业）
        # 为了性能，不查询concept_detail

        # 行业成长系数
        growth_coeff = get_industry_growth_coefficient(industry)
        growth_score = growth_coeff * 100

        # 第一关：行业成长筛选（只保留高成长和中成长）
        if growth_coeff < 0.7:
            return None  # 跳过低成长和无成长行业

        # 获取财务数据
        end_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        start_date = '20240101'

        try:
            financial = pro.fina_indicator(ts_code=stock_code,
                                          start_date=start_date,
                                          end_date=end_date)
        except:
            financial = pd.DataFrame()

        financial_score = calculate_financial_score_simple(financial, industry)

        # 获取技术数据
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=400)).strftime('%Y%m%d')

        try:
            df = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
        except:
            df = pd.DataFrame()

        if len(df) == 0:
            return None

        df = df.sort_values('trade_date').reset_index(drop=True)

        # 第二关：技术面筛选（需要至少250天数据）
        if len(df) < 250:
            return None

        # 获取市值数据
        try:
            basic_df = pro.daily_basic(ts_code=stock_code, trade_date=end_date,
                                      fields='ts_code,total_mv')
            if len(basic_df) > 0:
                total_mv = basic_df.iloc[0]['total_mv'] / 10000  # 万元转亿元
            else:
                return None
        except:
            return None

        # 第三关：市值筛选（超大盘股票不适合短线）
        if total_mv > 3000:
            return None

        # 技术面分析
        tech_result = calculate_technical_score(df)
        ma250_score = tech_result['ma250_score']
        chanlun_score = tech_result['chanlun']['score']
        tech_score = tech_result['tech_score']

        # 第四关：技术面筛选（250日均线必须>60分）
        if ma250_score < 60:
            return None

        # 近10日涨停统计
        recent_df = df.tail(10)
        limit_up_count = len(recent_df[recent_df['pct_chg'] >= 9.5])

        if limit_up_count == 0:
            limit_up_score = 0
        elif limit_up_count == 1:
            limit_up_score = 40
        elif limit_up_count == 2:
            limit_up_score = 70
        else:
            limit_up_score = 100

        # 市值扣分
        market_cap_penalty = get_market_cap_penalty(total_mv)

        # 催化逻辑评分
        if limit_up_count >= 3:
            catalyst_score = 100
        elif growth_coeff >= 0.7:
            catalyst_score = 80
        else:
            catalyst_score = 30

        # 题材热度指数
        theme_heat_index = (limit_up_score * 0.3) + (catalyst_score * 0.3) + (growth_score * 0.4)

        # 获取市场情绪
        current_emotion, emotion_score = get_market_emotion_simple()
        if emotion_score is None:
            emotion_score = 50
            current_emotion = 'neutral'

        # 计算各项评分
        long_term_score = growth_score
        medium_term_score = (theme_heat_index * 0.5) + (financial_score * 0.3) + (tech_score * 0.2)

        # 短期评分
        short_term_score = (tech_score * 0.7) + (emotion_score * 0.3) - market_cap_penalty
        short_term_score = max(0, min(100, short_term_score))

        # 综合得分（V9.0：短线60% + 中期30% + 长期10%）
        overall_score = (short_term_score * 0.6) + (medium_term_score * 0.3) + (long_term_score * 0.1)

        # 赢面评估（V9.5）
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
        else:
            mv_coeff = 0.68

        # 情绪周期系数
        emotion_coeff = {
            'despair': 0.5,
            'recede': 0.7,
            'climax': 0.6,
            'ferment': 0.8,
            'start': 1.0,
            'freeze': 0.9,
            'neutral': 0.75
        }

        win_rate = (overall_score / 100) * mv_coeff * emotion_coeff.get(current_emotion, 0.75)
        win_rate = max(0, min(1, win_rate))
        win_score = int(win_rate * 100)

        # 综合评级
        if overall_score >= 75:
            overall_rating = "优秀"
        elif overall_score >= 60:
            overall_rating = "良好"
        else:
            overall_rating = "一般"

        # 返回分析结果
        return {
            'code': stock_code,
            'name': stock_name,
            'industry': industry,
            'total_mv': round(total_mv, 2),
            'long_term_score': round(long_term_score, 1),
            'medium_term_score': round(medium_term_score, 1),
            'short_term_score': round(short_term_score, 1),
            'overall_score': round(overall_score, 1),
            'win_rate': win_score,
            'overall_rating': overall_rating,
            'financial_score': financial_score,
            'tech_score': tech_score,
            'limit_up_count': limit_up_count,
            'growth_coeff': growth_coeff,
            'current_emotion': current_emotion
        }

    except Exception as e:
        print(f"分析股票 {stock_code} 失败: {e}")
        return None

def batch_analyze_top_stocks(limit=10):
    """
    批量分析全市场股票，找出评分最高的股票

    Args:
        limit: 返回的股票数量
    """
    print("="*60)
    print("开始批量分析全市场股票...")
    print("="*60)

    # 获取市场情绪
    emotion, emotion_score = get_market_emotion_simple()
    print(f"当前市场情绪: {emotion} (评分: {emotion_score})")
    print()

    # 获取所有股票列表
    print("正在获取股票列表...")
    all_stocks = pro.stock_basic(fields='ts_code,symbol,name,area,industry,list_date')
    print(f"共找到 {len(all_stocks)} 只股票")
    print()

    # 批量分析
    print("开始分析股票...")

    results = []
    total = len(all_stocks)

    for idx, stock in all_stocks.iterrows():
        stock_code = stock['ts_code']
        stock_name = stock['name']
        industry = stock['industry']

        # 显示进度
        if (idx + 1) % 100 == 0:
            print(f"已分析 {idx + 1}/{total} 只股票，找到 {len(results)} 只符合要求的股票")

        # 分析股票
        result = analyze_single_stock(stock_code, stock_name, industry)

        if result and result['overall_score'] >= 60:
            results.append(result)

        # 限制结果数量（为了性能）
        if len(results) >= 100:
            break

    print()
    print("="*60)
    print("分析完成！")
    print(f"共分析 {total} 只股票，找到 {len(results)} 只符合要求的股票")
    print("="*60)
    print()

    # 按综合得分排序
    results = sorted(results, key=lambda x: x['overall_score'], reverse=True)

    # 输出前limit只股票
    print(f"评分最高的 {limit} 只股票：")
    print("="*60)

    for i, stock in enumerate(results[:limit], 1):
        print(f"\n【第{i}名】{stock['name']} ({stock['code']})")
        print(f"  行业: {stock['industry']}")
        print(f"  总市值: {stock['total_mv']}亿元")
        print(f"  综合得分: {stock['overall_score']}分")
        print(f"  赢面: {stock['win_rate']}%")
        print(f"  综合评级: {stock['overall_rating']}")
        print(f"  长期得分: {stock['long_term_score']}分 (行业成长)")
        print(f"  中期得分: {stock['medium_term_score']}分 (题材热度+财务+技术)")
        print(f"  短期得分: {stock['short_term_score']}分 (技术面+情绪周期)")
        print(f"  财务得分: {stock['financial_score']}分")
        print(f"  技术得分: {stock['tech_score']}分")
        print(f"  近10日涨停: {stock['limit_up_count']}次")
        print(f"  行业成长系数: {stock['growth_coeff']}")

    return results[:limit]

if __name__ == '__main__':
    top_stocks = batch_analyze_top_stocks(limit=10)

    # 保存结果到JSON文件
    output_file = '/Users/likan/.openclaw/workspace/top_stocks_result.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(top_stocks, f, ensure_ascii=False, indent=2)

    print()
    print("="*60)
    print(f"分析结果已保存到: {output_file}")
    print("="*60)
