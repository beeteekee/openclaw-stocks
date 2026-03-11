#!/usr/bin/env python3
"""每日精选股票舆情分析 - 对每日精选10只股票进行舆情分析并按热度重新排序"""

import os
import sys
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict
import warnings
warnings.filterwarnings('ignore')

# 导入相关模块
sys.path.insert(0, '/Users/likan/.openclaw/workspace')

from sentiment_analysis import calculate_sentiment_score

# 读取TOP3结果文件
TOP3_RESULT_FILE = '/Users/likan/.openclaw/workspace/top3_today_result.csv'
SENTIMENT_RESULT_FILE = '/Users/likan/.openclaw/workspace/daily_sentiment_ranking.csv'


def read_top3_stocks(limit: int = 10) -> List[Dict]:
    """
    读取TOP3结果文件，获取每日精选股票

    Args:
        limit: 读取数量限制

    Returns:
        股票列表
    """
    try:
        df = pd.read_csv(TOP3_RESULT_FILE, encoding='utf-8')

        if len(df) == 0:
            print(f"⚠️ TOP3结果文件为空")
            return []

        # 按赢面率排序，取前N只
        df_sorted = df.sort_values('win_rate', ascending=False)
        top_stocks = df_sorted.head(limit).to_dict('records')

        print(f"✅ 从TOP3结果中读取到 {len(top_stocks)} 只股票")
        return top_stocks

    except FileNotFoundError:
        print(f"⚠️ TOP3结果文件不存在: {TOP3_RESULT_FILE}")
        return []
    except Exception as e:
        print(f"⚠️ 读取TOP3结果文件失败: {e}")
        return []


def analyze_sentiment_for_stocks(stocks: List[Dict]) -> List[Dict]:
    """
    对股票列表进行舆情分析

    Args:
        stocks: 股票列表

    Returns:
        包含舆情分析结果的股票列表
    """
    results = []

    for i, stock in enumerate(stocks, 1):
        stock_code = stock.get('stock_code', '')
        stock_name = stock.get('stock_name', '')
        limit_up_count = stock.get('limit_up_count', 0)
        growth_coeff = stock.get('growth_coeff', 0.3)

        print(f"\n[{i}/{len(stocks)}] 分析 {stock_name}（{stock_code}）的舆情...")

        try:
            # 计算舆情热度分
            sentiment_result = calculate_sentiment_score(
                stock_code=stock_code,
                stock_name=stock_name,
                limit_up_count=limit_up_count,
                growth_coeff=growth_coeff,
                concepts=[]
            )

            # 合并结果
            stock_with_sentiment = stock.copy()
            stock_with_sentiment['sentiment_heat_score'] = sentiment_result['sentiment_heat_score']
            stock_with_sentiment['sentiment_level'] = sentiment_result['sentiment_level']
            stock_with_sentiment['sentiment_detail'] = json.dumps(sentiment_result['sentiment_detail'], ensure_ascii=False)
            stock_with_sentiment['bettafish_enabled'] = sentiment_result['bettafish_enabled']

            print(f"   舆情热度: {sentiment_result['sentiment_heat_score']:.1f}/100")
            print(f"   舆情级别: {sentiment_result['sentiment_level']}")

            results.append(stock_with_sentiment)

        except Exception as e:
            print(f"   ⚠️ 舆情分析失败: {e}")
            # 失败时设置默认值
            stock_with_sentiment = stock.copy()
            stock_with_sentiment['sentiment_heat_score'] = 0.0
            stock_with_sentiment['sentiment_level'] = '未知'
            stock_with_sentiment['sentiment_detail'] = json.dumps({'error': str(e)}, ensure_ascii=False)
            stock_with_sentiment['bettafish_enabled'] = False
            results.append(stock_with_sentiment)

    return results


def rerank_by_sentiment(stocks: List[Dict]) -> List[Dict]:
    """
    按舆情热度重新排序

    Args:
        stocks: 股票列表

    Returns:
        重新排序后的股票列表
    """
    # 按舆情热度分降序排序
    sorted_stocks = sorted(stocks, key=lambda x: x['sentiment_heat_score'], reverse=True)

    print(f"\n{'='*80}")
    print(f"按舆情热度重新排序后:")
    print(f"{'='*80}")

    for i, stock in enumerate(sorted_stocks, 1):
        print(f"{i}. {stock['stock_name']}（{stock['stock_code']}） - "
              f"舆情热度: {stock['sentiment_heat_score']:.1f}/100")

    return sorted_stocks


def save_results(stocks: List[Dict], output_file: str = SENTIMENT_RESULT_FILE):
    """
    保存结果到CSV

    Args:
        stocks: 股票列表
        output_file: 输出文件路径
    """
    try:
        df = pd.DataFrame(stocks)

        # 选择要保存的列
        columns = [
            'stock_code', 'stock_name', 'price', 'pct_chg', 'total_mv',
            'win_rate', 'overall_score', 'long_term_score', 'mid_term_score', 'short_term_score',
            'sentiment_heat_score', 'sentiment_level', 'limit_up_count', 'growth_coeff',
            'buy_point_type', 'sentiment_detail', 'bettafish_enabled'
        ]

        # 只保留存在的列
        existing_columns = [col for col in columns if col in df.columns]
        df_output = df[existing_columns]

        # 保存到CSV
        df_output.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"\n✅ 舆情分析结果已保存到: {output_file}")
        print(f"   共 {len(stocks)} 只股票")

    except Exception as e:
        print(f"⚠️ 保存结果失败: {e}")


def main():
    """主函数"""
    print("="*80)
    print("每日精选股票舆情分析")
    print("="*80)

    # 1. 读取每日精选股票（TOP3结果的前10只）
    print("\n步骤1: 读取每日精选股票")
    top_stocks = read_top3_stocks(limit=10)

    if not top_stocks:
        print("❌ 未能获取到每日精选股票，程序退出")
        return

    # 2. 对每只股票进行舆情分析
    print("\n步骤2: 进行舆情分析")
    stocks_with_sentiment = analyze_sentiment_for_stocks(top_stocks)

    # 3. 按舆情热度重新排序
    print("\n步骤3: 按舆情热度重新排序")
    reranked_stocks = rerank_by_sentiment(stocks_with_sentiment)

    # 4. 保存结果
    print("\n步骤4: 保存结果")
    save_results(reranked_stocks)

    # 5. 输出汇总信息
    print(f"\n{'='*80}")
    print("舆情分析汇总")
    print(f"{'='*80}")

    avg_sentiment = sum(s['sentiment_heat_score'] for s in reranked_stocks) / len(reranked_stocks)
    high_heat_count = sum(1 for s in reranked_stocks if s['sentiment_heat_score'] >= 80)
    medium_heat_count = sum(1 for s in reranked_stocks if 60 <= s['sentiment_heat_score'] < 80)

    print(f"平均舆情热度: {avg_sentiment:.1f}/100")
    print(f"高热度股票（≥80分）: {high_heat_count}只")
    print(f"中等热度股票（60-80分）: {medium_heat_count}只")
    print(f"低热度股票（<60分）: {len(reranked_stocks) - high_heat_count - medium_heat_count}只")

    print(f"\n{'='*80}")
    print("舆情热度排名TOP3")
    print(f"{'='*80}")

    for i, stock in enumerate(reranked_stocks[:3], 1):
        print(f"\n第{i}名: {stock['stock_name']}（{stock['stock_code']}）")
        print(f"  股价: {stock['price']:.2f} | 涨跌幅: {stock['pct_chg']:.2f}%")
        print(f"  舆情热度: {stock['sentiment_heat_score']:.1f}/100")
        print(f"  舆情级别: {stock['sentiment_level']}")
        print(f"  赢面率: {stock['win_rate']*100:.1f}%")

    print(f"\n{'='*80}")
    print("分析完成!")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()
