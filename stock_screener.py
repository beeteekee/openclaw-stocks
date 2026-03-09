#!/usr/bin/env python3
"""养家心法选股系统 - 批量筛选符合买股三原则的股票

买股三原则：
1. 当天有买点（缠论买点确认）
2. 价格站上线（股价 > 250日均线）
3. 养家心法过（综合评分 > 60）

"""

import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import warnings
warnings.filterwarnings('ignore')

# 从MEMORY.md中获取的token
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

def check_chantou_buy_point(df):
    """检查缠论买点（修正版）

    一类买点：股价创新低，但MACD柱子未创新低（底背驰）
    二类买点：MACD金叉（DIF上穿DEA）
    三类买点：突破前高后的回踩确认

    Returns:
        (buy_point_score, buy_point_type, description)
        buy_point_score: 0-100分
        buy_point_type: '一类买点', '二类买点', '三类买点', '无买点'
        description: 买点描述
    """
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

    # 三类买点：突破前高后回踩
    if len(df) >= 20:
        recent_high = df['high'].tail(20).max()
        if latest['close'] > recent_high * 0.98:  # 接近前高
            return (100, '三类买点',
                    f'突破前高确认 (前高:{recent_high:.2f}, 当日:{latest["close"]:.2f})')

    return (0, '无买点', '未发现明确的缠论买点')

def analyze_stock(ts_code, pro):
    """分析单只股票，返回完整的评分信息"""
    try:
        # 获取股票基本信息
        stock_info = pro.stock_basic(ts_code=ts_code)
        if len(stock_info) == 0:
            return None

        stock_info = stock_info.iloc[0]

        # 基础筛选
        if 'ST' in stock_info['name'] or '*ST' in stock_info['name']:
            # print(f"    ST股票: {stock_info['name']}")
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
            # 调试信息
            # print(f"    数据不足: 只有{len(df)}天数据")
            return None

        latest = df.iloc[-1]
        prev = df.iloc[-2]

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

        # 财务质量（简化版）
        try:
            financial = pro.fina_indicator(
                ts_code=ts_code,
                start_date=(datetime.now() - timedelta(days=120)).strftime('%Y%m%d'),
                end_date=end_date
            )
            if len(financial) > 0:
                fin = financial.iloc[0]
                roe = fin.get('roe', 0) or 0
                gross_margin = fin.get('grossprofit_margin', 0) or 0
                revenue_growth = fin.get('or_yoy', 0) or 0
                profit_growth = fin.get('profit_yoy', 0) or 0

                finance_score = 60  # 基础分
                if roe > 15: finance_score += 10
                if gross_margin > 30: finance_score += 10
                if revenue_growth > 10: finance_score += 10
                if profit_growth > 10: finance_score += 10
                finance_score = min(finance_score, 100)
            else:
                finance_score = 60
        except:
            finance_score = 60

        # 中期得分
        mid_term_score = theme_score * 0.5 + finance_score * 0.3 + tech_score * 0.2

        # 短期得分（技术面80% + 情绪周期20% - 市值扣分）
        emotion_cycle_score = 60  # 默认中性
        short_term_score = tech_score * 0.8 + emotion_cycle_score * 0.2

        # 综合得分
        overall_score = short_term_score * 0.6 + mid_term_score * 0.3 + long_term_score * 0.1

        # 市值
        try:
            basic = pro.daily_basic(ts_code=ts_code, trade_date=latest['trade_date'])
            if len(basic) > 0:
                total_mv = basic.iloc[0]['total_mv'] / 10000  # 亿元
            else:
                total_mv = 100  # 默认
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

        # 买股三原则检查
        has_buy_point = buy_point_score > 0  # 有买点
        price_above_ma250 = price > ma250    # 股价站上线
        yangjia_pass = overall_score > 60      # 养家心法过

        return {
            'ts_code': ts_code,
            'name': stock_info['name'],
            'industry': stock_info['industry'],
            'price': price,
            'pct_chg': latest['pct_chg'],
            'ma250': ma250,
            'price_to_ma250': price_to_ma250,
            'ma250_score': ma250_score,
            'buy_point_type': buy_point_type,
            'buy_point_desc': buy_point_desc,
            'buy_point_score': buy_point_score,
            'tech_score': tech_score,
            'limit_up_count': limit_up_count,
            'limit_up_score': limit_up_score,
            'growth_coeff': growth_coeff,
            'long_term_score': long_term_score,
            'theme_score': theme_score,
            'finance_score': finance_score,
            'mid_term_score': mid_term_score,
            'short_term_score': short_term_score,
            'overall_score': overall_score,
            'total_mv': total_mv,
            'has_buy_point': has_buy_point,
            'price_above_ma250': price_above_ma250,
            'yangjia_pass': yangjia_pass,
            'all_three_passed': has_buy_point and price_above_ma250 and yangjia_pass
        }

    except Exception as e:
        print(f"  ⚠ 分析{ts_code}失败: {e}")
        return None

def screen_stocks(stock_list, pro, limit=None):
    """批量筛选股票"""
    results = []

    print(f"\n开始筛选 {len(stock_list)} 只股票...")
    print("="*80)

    for i, ts_code in enumerate(stock_list):
        if limit and i >= limit:
            break

        print(f"\n[{i+1}/{len(stock_list)}] 正在分析 {ts_code}...", end=' ')

        result = analyze_stock(ts_code, pro)
        if result:
            print(f"✓ 综合:{result['overall_score']:.1f} | "
                  f"买点:{result['buy_point_type']} | "
                  f"250线:{'✓' if result['price_above_ma250'] else '✗'}")
            results.append(result)
        else:
            print("✗ 不符合基础筛选（可能是ST、数据不足或其他原因）")

    return results

def print_qualifying_stocks(results):
    """打印符合买股三原则的股票"""
    print("\n" + "="*80)
    print("符合买股三原则的股票")
    print("="*80)
    print("买股三原则：")
    print("  1. 当天有买点（缠论买点确认）")
    print("  2. 价格站上线（股价 > 250日均线）")
    print("  3. 养家心法过（综合评分 > 60）")
    print("="*80)

    qualifying = [r for r in results if r['all_three_passed']]

    if len(qualifying) == 0:
        print("\n⚠️ 没有找到完全符合买股三原则的股票")
        print("\n接近符合条件的股票（满足2个原则）：")
        partial = [r for r in results if
                   (r['has_buy_point'] + r['price_above_ma250'] + r['yangjia_pass']) >= 2]
        partial = sorted(partial, key=lambda x: x['overall_score'], reverse=True)[:5]

        if len(partial) == 0:
            print("  没有")
            return

        for i, stock in enumerate(partial, 1):
            print(f"\n{i}. {stock['name']} ({stock['ts_code']})")
            print(f"   价格: {stock['price']:.2f} | 涨跌幅: {stock['pct_chg']:.2f}% | 市值: {stock['total_mv']:.1f}亿")
            print(f"   综合得分: {stock['overall_score']:.1f} | "
                  f"长线: {stock['long_term_score']:.1f} | "
                  f"中线: {stock['mid_term_score']:.1f} | "
                  f"短线: {stock['short_term_score']:.1f}")
            print(f"   买点: {stock['buy_point_type']} | "
                  f"250线: {stock['ma250']:.2f} | "
                  f"股价/250线: {stock['price_to_ma250']:.4f}")
            print(f"   三原则: "
                  f"买点{'✓' if stock['has_buy_point'] else '✗'} | "
                  f"250线{'✓' if stock['price_above_ma250'] else '✗'} | "
                  f"心法{'✓' if stock['yangjia_pass'] else '✗'}")
    else:
        qualifying = sorted(qualifying, key=lambda x: x['overall_score'], reverse=True)
        for i, stock in enumerate(qualifying, 1):
            print(f"\n{'='*80}")
            print(f"{i}. {stock['name']} ({stock['ts_code']}) - ✅ 符合买股三原则！")
            print(f"{'='*80}")
            print(f"价格: {stock['price']:.2f} | 涨跌幅: {stock['pct_chg']:.2f}% | 市值: {stock['total_mv']:.1f}亿")
            print(f"行业: {stock['industry']} | 成长系数: {stock['growth_coeff']}")
            print(f"\n综合得分: {stock['overall_score']:.1f}")
            print(f"  长期得分: {stock['long_term_score']:.1f}（赛道天花板）")
            print(f"  中期得分: {stock['mid_term_score']:.1f}（题材热度+财务质量）")
            print(f"  短期得分: {stock['short_term_score']:.1f}（技术面+情绪周期）")
            print(f"\n技术面: {stock['tech_score']:.1f}")
            print(f"  250日均线: {stock['ma250']:.2f} (得分:{stock['ma250_score']})")
            print(f"  缠论买点: {stock['buy_point_type']} (得分:{stock['buy_point_score']})")
            print(f"  买点描述: {stock['buy_point_desc']}")
            print(f"\n题材热度: {stock['theme_score']:.1f}")
            print(f"  近10日涨停: {stock['limit_up_count']}次 (得分:{stock['limit_up_score']})")
            print(f"  财务质量: {stock['finance_score']:.1f}")
            print(f"\n三原则:")
            print(f"  1. 当天有买点: {'✓' if stock['has_buy_point'] else '✗'}")
            print(f"  2. 价格站上线: {'✓' if stock['price_above_ma250'] else '✗'} ({stock['price']:.2f} > {stock['ma250']:.2f})")
            print(f"  3. 养家心法过: {'✓' if stock['yangjia_pass'] else '✗'} (综合得分:{stock['overall_score']:.1f} > 60)")

def main():
    # 初始化Tushare
    pro = ts.pro_api(TUSHARE_TOKEN)

    # 定义股票池（热门股票、涨停股票等）
    stock_list = [
        # AI算力
        '300474.SZ',  # 景嘉微
        '300059.SZ',  # 东方通
        '300222.SZ',  # 科大智能

        # 半导体
        '002371.SZ',  # 北方华创
        '600584.SH',  # 长电科技
        '002049.SZ',  # 紫光国微

        # 新能源车
        '002594.SZ',  # 比亚迪
        '300750.SZ',  # 宁德时代
        '002460.SZ',  # 赣锋锂业

        # 光伏
        '002129.SZ',  # 中环股份
        '688599.SH',  # 天合光能
        '300118.SZ',  # 东方日升

        # 机器人
        '300024.SZ',  # 机器人
        '002008.SZ',  # 大族激光

        # 5G通信
        '300762.SZ',  # 上海瀚讯
        '000021.SZ',  # 深科技
        '002281.SZ',  # 光迅科技

        # 医药生物
        '300015.SZ',  # 爱尔眼科
        '000661.SZ',  # 长春高新

        # 高端制造
        '002415.SZ',  # 海康威视
        '600036.SH',  # 招商银行
    ]

    # 批量筛选
    results = screen_stocks(stock_list, pro)

    # 打印结果
    print_qualifying_stocks(results)

if __name__ == '__main__':
    main()
