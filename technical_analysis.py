#!/usr/bin/env python3
"""技术分析工具 - 250日均线、MACD、缠论买点"""

import pandas as pd
import numpy as np

def calculate_ema(data, period):
    """计算指数移动平均线"""
    return data.ewm(span=period, adjust=False).mean()

def calculate_macd(df):
    """
    计算MACD指标

    参数:
        df: 包含close列的DataFrame

    返回:
        DataFrame: 添加了dif, dea, macd列
    """
    # 计算DIF（快速线）
    ema12 = calculate_ema(df['close'], 12)
    ema26 = calculate_ema(df['close'], 26)
    dif = ema12 - ema26

    # 计算DEA（慢速线，也叫MACD线）
    dea = calculate_ema(dif, 9)

    # 计算MACD柱状图
    macd = (dif - dea) * 2

    return dif, dea, macd

def identify_fenxing(df, window=3):
    """
    识别底分型和顶分型

    参数:
        df: 包含high, low, close列的DataFrame
        window: 分型窗口，默认为3

    返回:
        df: 添加了top_fenxing, bottom_fenxing列
            top_fenxing: 1表示顶分型，0表示非顶分型
            bottom_fenxing: 1表示底分型，0表示非底分型
    """
    df['top_fenxing'] = 0
    df['bottom_fenxing'] = 0

    for i in range(window, len(df) - window):
        # 底分型判断
        # 中间K线的最低点 ≤ 左边K线的最低点
        # 中间K线的最低点 ≤ 右边K线的最低点
        low_mid = df.iloc[i]['low']
        low_left = df.iloc[i-1]['low']
        low_right = df.iloc[i+1]['low']

        if low_mid <= low_left and low_mid <= low_right:
            df.iloc[i, df.columns.get_loc('bottom_fenxing')] = 1

        # 顶分型判断
        # 中间K线的最高点 ≥ 左边K线的最高点
        # 中间K线的最高点 ≥ 右边K线的最高点
        high_mid = df.iloc[i]['high']
        high_left = df.iloc[i-1]['high']
        high_right = df.iloc[i+1]['high']

        if high_mid >= high_left and high_mid >= high_right:
            df.iloc[i, df.columns.get_loc('top_fenxing')] = 1

    return df

def check_divergence(prices, indicators, lookback=5):
    """
    检查背驰

    参数:
        prices: 价格序列
        indicators: 指标序列（如MACD柱子）
        lookback: 回溯窗口

    返回:
        bool: 是否出现背驰
    """
    if len(prices) < lookback or len(indicators) < lookback:
        return False

    # 找到最近lookback个周期内的最低价格
    price_min_idx = prices.tail(lookback).idxmin()

    # 找到之前lookback个周期内的最低价格
    if price_min_idx - lookback >= 0:
        prev_price_idx = prices.iloc[price_min_idx - lookback : price_min_idx].idxmin()
    else:
        prev_price_idx = prices.iloc[0:price_min_idx].idxmin()

    # 比较价格
    current_price = prices.loc[price_min_idx]
    prev_price = prices.loc[prev_price_idx]

    # 当前价格创新低
    if current_price >= prev_price:
        return False

    # 比较对应的指标值
    current_indicator = indicators.loc[price_min_idx]
    prev_indicator = indicators.loc[prev_price_idx]

    # 指标没有创新低（或更低），出现背驰
    if current_indicator > prev_indicator:
        return True

    return False

def analyze_chanlun_buy_point(df):
    """
    分析缠论买点（修正版 - 使用正确的局部低点识别）

    参数:
        df: K线数据DataFrame，需包含close, high, low列

    返回:
        dict: {
            'type': 1/2/3 (一类/二类/三类买点),
            'score': 100/80/60/0 (买点得分),
            'desc': '买点描述'
        }
    """
    if len(df) < 20:
        return {'type': 0, 'score': 0, 'desc': '数据不足，无法分析'}

    # 添加索引列
    df = df.reset_index(drop=True)

    # 计算MACD
    dif, dea, macd = calculate_macd(df)
    df['dif'] = dif
    df['dea'] = dea
    df['macd'] = macd

    # 获取最新K线
    latest_idx = len(df) - 1
    latest = df.iloc[latest_idx]

    # === 一类买点判断（修正版：使用正确的局部低点识别）===
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
                abs(latest_low['macd']) < abs(prev_low['macd'])):
                return {
                    'type': 1,
                    'score': 100,
                    'desc': f'一类买点：底背驰确认 (价:{prev_low["low"]:.2f}→{latest_low["low"]:.2f}, MACD:{abs(prev_low["macd"]):.4f}→{abs(latest_low["macd"]):.4f})'
                }

    # === 二类买点判断：MACD金叉确认 ===
    if latest_idx > 0:
        if df.iloc[latest_idx]['dif'] > df.iloc[latest_idx]['dea'] and \
           df.iloc[latest_idx - 1]['dif'] <= df.iloc[latest_idx - 1]['dea']:
            return {
                'type': 2,
                'score': 60,
                'desc': f'二类买点：MACD金叉确认 (前日DIF:{df.iloc[latest_idx - 1]["dif"]:.4f}<DEA:{df.iloc[latest_idx - 1]["dea"]:.4f}, 当日DIF:{df.iloc[latest_idx]["dif"]:.4f}>DEA:{df.iloc[latest_idx]["dea"]:.4f})'
            }

    # === 三类买点判断：突破前高 ===
    if len(df) >= 20:
        recent_high = df['high'].tail(20).max()
        if latest['close'] > recent_high * 0.98:
            return {
                'type': 3,
                'score': 80,
                'desc': f'三类买点：突破前高确认 (前高:{recent_high:.2f}, 当日:{latest["close"]:.2f})'
            }

    # 无明确买点
    return {
        'type': 0,
        'score': 0,
        'desc': '无明确买点：当前不满足任何缠论买点条件'
    }

def calculate_technical_score(df):
    """
    计算技术面综合得分

    参数:
        df: K线数据DataFrame

    返回:
        dict: {
            'ma250_score': 250日均线得分,
            'ma250': 250日均线值,
            'chanlun': 缠论买点分析结果,
            'tech_score': 技术面综合得分
        }
    """
    if len(df) < 20:
        return {
            'ma250_score': 0,
            'ma250': None,
            'chanlun': {'type': 0, 'score': 0, 'desc': '数据不足'},
            'tech_score': 0
        }

    # 获取最新数据
    latest = df.iloc[-1]
    close_price = latest['close']

    # === 250日均线评分（严格按照养家心法V8.0标准）===
    if len(df) >= 250:
        ma250 = df['close'].tail(250).mean()
        ratio = close_price / ma250

        if close_price > ma250:
            # 股价在MA250上方
            if ratio > 1.05:
                ma250_score = 100  # 长线强势
            elif ratio > 1.02:
                ma250_score = 80   # 长线强势
            else:
                ma250_score = 60   # 刚站上长线
        else:
            # 股价在MA250下方（严格按照养家心法标准）
            if ratio > 0.98:
                ma250_score = 40   # 刚跌破长线
            elif ratio > 0.95:
                ma250_score = 20   # 长线弱势
            else:
                ma250_score = 0     # 长线弱势，必须回避
    else:
        ma250 = None
        ma250_score = 0

    # === 缠论买点分析 ===
    chanlun_result = analyze_chanlun_buy_point(df)

    # === 技术面综合得分（严格按照养家心法V8.0标准）===
    # 技术面综合得分 = 250日均线得分 × 50% + 缠论买点得分 × 50%
    tech_score = (ma250_score * 0.5) + (chanlun_result['score'] * 0.5)

    return {
        'ma250_score': ma250_score,
        'ma250': ma250,
        'chanlun': chanlun_result,
        'tech_score': tech_score
    }

if __name__ == '__main__':
    # 测试代码
    print("技术分析工具模块")
    print("功能：250日均线、MACD、缠论买点分析")
