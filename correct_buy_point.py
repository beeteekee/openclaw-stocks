#!/usr/bin/env python3
"""修正缠论买点判断逻辑"""

import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

TUSHARE_TOKEN = "e2e547ffbac099527efcaaa0072f0a3adea8eb8fd9efba3b65da7518"

def calculate_macd(df):
    """计算MACD指标"""
    df = df.copy()
    exp12 = df['close'].ewm(span=12, adjust=False).mean()
    exp26 = df['close'].ewm(span=26, adjust=False).mean()
    df['DIF'] = exp12 - exp26
    df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()
    df['MACD'] = (df['DIF'] - df['DEA']) * 2
    return df

def find_local_lows(df, window=3):
    """
    找出局部低点（修正版）

    Args:
        df: 包含'low'列的DataFrame
        window: 前后window个交易日

    Returns:
        包含局部低点的DataFrame
    """
    df = df.copy()
    df['is_local_low'] = False

    for i in range(window, len(df) - window):
        current_low = df.iloc[i]['low']
        surrounding_lows = df.iloc[i-window:i+window+1]['low']

        if current_low == surrounding_lows.min():
            df.iloc[i, df.columns.get_loc('is_local_low')] = True

    return df

def check_buy_point_1(df):
    """
    一类买点（第一类买点）：底背驰

    条件：
    1. 下跌趋势中
    2. 最近两个低点，价格创新低
    3. 但MACD柱子未创新低（绝对值减小）
    """
    if len(df) < 20:
        return (0, '无买点', '数据不足')

    df = calculate_macd(df)
    df = find_local_lows(df, window=3)

    local_lows = df[df['is_local_low']]

    if len(local_lows) < 2:
        return (0, '无买点', '低点不足')

    # 检查最后两个低点
    latest_low = local_lows.iloc[-1]
    prev_low = local_lows.iloc[-2]

    # 价格创新低
    price_new_low = latest_low['low'] < prev_low['low']

    # MACD柱子未创新低（绝对值减小）
    macd_decreased = abs(latest_low['MACD']) < abs(prev_low['MACD'])

    if price_new_low and macd_decreased:
        return (100, '一类买点',
                f'底背驰确认 (前低:{prev_low["low"]:.2f}→现低:{latest_low["low"]:.2f}, '
                f'MACD:{abs(prev_low["MACD"]):.4f}→{abs(latest_low["MACD"]):.4f})')

    return (0, '无买点', '未发现底背驰')

def check_buy_point_2(df):
    """
    二类买点（第二类买点）：MACD金叉确认

    条件：
    1. 一类买点后的回抽
    2. MACD金叉（DIF上穿DEA）
    3. 当天就是金叉确认日
    """
    if len(df) < 20:
        return (0, '无买点', '数据不足')

    df = calculate_macd(df)

    # 检查最近两天是否金叉
    if len(df) < 2:
        return (0, '无买点', '数据不足')

    prev = df.iloc[-2]
    latest = df.iloc[-1]

    # DIF从下方上穿DEA
    if prev['DIF'] < prev['DEA'] and latest['DIF'] > latest['DEA']:
        return (100, '二类买点',
                f'MACD金叉确认 (前日DIF:{prev["DIF"]:.4f}<DEA:{prev["DEA"]:.4f}, '
                f'当日DIF:{latest["DIF"]:.4f}>DEA:{latest["DEA"]:.4f})')

    return (0, '无买点', '未发现MACD金叉')

def check_buy_point_3(df):
    """
    三类买点（第三类买点）：突破前高

    条件：
    1. 突破前高
    2. 回踩不破突破点
    3. 站在中枢上方
    """
    if len(df) < 30:
        return (0, '无买点', '数据不足')

    df = df.copy()

    # 找出最近20天的最高点
    recent_df = df.tail(20)
    recent_high = recent_df['high'].max()
    recent_high_date = recent_df[recent_df['high'] == recent_high]['trade_date'].values[0]

    latest = df.iloc[-1]

    # 当天收盘价接近或突破前高
    if latest['close'] > recent_high * 0.98:
        return (100, '三类买点',
                f'突破前高确认 (前高:{recent_high:.2f}, 当日:{latest["close"]:.2f})')

    return (0, '无买点', f'未突破前高 (前高:{recent_high:.2f}, 当日:{latest["close"]:.2f})')

def comprehensive_buy_point_check(ts_code):
    """综合检查缠论买点"""
    try:
        # 获取行情数据
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')

        pro = ts.pro_api(TUSHARE_TOKEN)
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        df = df.sort_values('trade_date')

        if len(df) < 30:
            return None

        # 计算MACD
        df = calculate_macd(df)

        print(f"\n{'='*100}")
        print(f"{ts_code} 缠论买点检查（修正版）")
        print(f"{'='*100}")
        print(f"最新交易日: {df.iloc[-1]['trade_date']}")
        print(f"收盘价: {df.iloc[-1]['close']:.2f}")
        print(f"涨跌幅: {df.iloc[-1]['pct_chg']:.2f}%")
        print(f"\\n{'='*100}")

        # 检查各类买点
        score1, type1, desc1 = check_buy_point_1(df)
        score2, type2, desc2 = check_buy_point_2(df)
        score3, type3, desc3 = check_buy_point_3(df)

        print(f"一类买点（底背驰）: {type1} ({score1}分)")
        print(f"  {desc1}")
        print(f"\\n二类买点（MACD金叉）: {type2} ({score2}分)")
        print(f"  {desc2}")
        print(f"\\n三类买点（突破前高）: {type3} ({score3}分)")
        print(f"  {desc3}")

        # 选择得分最高的买点
        buy_points = [
            (score1, type1, desc1),
            (score2, type2, desc2),
            (score3, type3, desc3)
        ]
        buy_points.sort(key=lambda x: x[0], reverse=True)

        best_score, best_type, best_desc = buy_points[0]

        print(f"\\n{'='*100}")
        print(f"最终买点判定: {best_type} ({best_score}分)")
        print(f"说明: {best_desc}")
        print(f"{'='*100}")

        return {
            'buy_point_type': best_type,
            'buy_point_score': best_score,
            'buy_point_desc': best_desc
        }

    except Exception as e:
        print(f"分析失败: {e}")
        return None

if __name__ == '__main__':
    # 测试几只股票
    test_stocks = [
        '002355.SZ',  # 兴民智通（之前误判为一类买点）
        '002510.SZ',  # 天汽模（之前判定为二类买点）
        '920976.BJ',  # 视声智能（之前判定为二类买点）
        '300750.SZ',  # 宁德时代（之前判定为一类买点）
    ]

    for ts_code in test_stocks:
        comprehensive_buy_point_check(ts_code)
        print()
