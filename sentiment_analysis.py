#!/usr/bin/env python3
"""舆情分析模块 - 分析个股的市场关注度、讨论热度、情绪倾向
符合养家心法第3条"数据求真原则"
"""

import sys
import os
from typing import Dict, List, Tuple

# 添加BettaFish-skill路径
sys.path.insert(0, '/Users/likan/.openclaw/workspace/BettaFish-skill/scripts')

from sentiment_analyzer import SentimentAnalyzer, SentimentResult

# 导入舆情数据获取器
from sentiment_data_fetcher import SentimentDataFetcher


def calculate_sentiment_score(stock_code: str, stock_name: str,
                              limit_up_count: int, growth_coeff: float,
                              concepts: List[str] = None) -> Dict:
    """
    计算舆情热度分

    Args:
        stock_code: 股票代码
        stock_name: 股票名称
        limit_up_count: 近10日涨停次数
        growth_coeff: 行业成长系数
        concepts: 概念板块列表

    Returns:
        dict: 包含舆情热度分、讨论热度、情绪倾向、龙头关注度等
    """
    print("\n" + "="*60)
    print("舆情热度分析（V10.1 - 集成BettaFish）")
    print("="*60)

    # 初始化BettaFish情感分析器
    try:
        sentiment_analyzer = SentimentAnalyzer()
        print("✅ BettaFish情感分析器加载成功")
    except Exception as e:
        print(f"⚠️ BettaFish情感分析器加载失败: {e}")
        print("  使用降级方案：基于规则的情感分析")
        sentiment_analyzer = None

    # 1. 讨论热度评分（0-100分，权重40%）
    discussion_score = _calculate_discussion_heat(stock_code, stock_name, limit_up_count)

    # 2. 情绪倾向评分（0-100分，权重30%）
    # 使用BettaFish情感分析器进行分析
    if sentiment_analyzer:
        sentiment_score, sentiment_detail = _calculate_sentiment_trend_bettafish(
            sentiment_analyzer, stock_code, stock_name, limit_up_count, growth_coeff
        )
    else:
        sentiment_score = _calculate_sentiment_trend(limit_up_count, growth_coeff)
        sentiment_detail = {}

    # 3. 龙头关注度评分（0-100分，权重30%）
    leader_attention_score = _calculate_leader_attention(limit_up_count, growth_coeff, concepts)

    # 综合舆情热度分
    sentiment_heat_score = (discussion_score * 0.4 +
                           sentiment_score * 0.3 +
                           leader_attention_score * 0.3)

    result = {
        'sentiment_heat_score': round(sentiment_heat_score, 1),
        'discussion_score': discussion_score,
        'sentiment_trend_score': sentiment_score,
        'leader_attention_score': leader_attention_score,
        'sentiment_level': _get_sentiment_level(sentiment_heat_score),
        'sentiment_detail': sentiment_detail,  # BettaFish详细分析
        'bettafish_enabled': sentiment_analyzer is not None
    }

    print(f"\n📊 舆情热度得分: {sentiment_heat_score:.1f}/100")
    print(f"  ├─ 讨论热度: {discussion_score}/100 (权重40%)")
    print(f"  ├─ 情绪倾向: {sentiment_score}/100 (权重30%)")
    if sentiment_detail:
        print(f"  │  └─ {sentiment_detail.get('label', '未知')}（置信度: {sentiment_detail.get('confidence', 0):.2f}）")
    print(f"  └─ 龙头关注: {leader_attention_score}/100 (权重30%)")
    print(f"  舆情级别: {result['sentiment_level']}")

    return result


def _calculate_discussion_heat(stock_code: str, stock_name: str,
                              limit_up_count: int) -> float:
    """
    计算讨论热度

    基于涨停次数和行业成长系数推断热度

    Args:
        stock_code: 股票代码
        stock_name: 股票名称
        limit_up_count: 近10日涨停次数

    Returns:
        讨论热度分（0-100）
    """
    # 涨停次数越高，讨论热度越高
    if limit_up_count >= 3:
        base_score = 100  # 连续涨停，超级热门
    elif limit_up_count == 2:
        base_score = 80   # 两次涨停，热门
    elif limit_up_count == 1:
        base_score = 60   # 一次涨停，较热门
    else:
        base_score = 30   # 无涨停，一般热度

    print(f"  讨论热度: {base_score}/100")
    if limit_up_count >= 2:
        print(f"    （近10日涨停{limit_up_count}次，市场关注度极高）")
    elif limit_up_count == 1:
        print(f"    （近10日涨停1次，有一定关注度）")
    else:
        print(f"    （近10日无涨停，关注度一般）")

    return base_score


def _calculate_sentiment_trend_bettafish(analyzer: SentimentAnalyzer,
                                        stock_code: str,
                                        stock_name: str,
                                        limit_up_count: int,
                                        growth_coeff: float) -> Tuple[float, Dict]:
    """
    使用BettaFish情感分析器计算情绪倾向

    从真实数据源（东方财富股吧等）获取舆情数据并分析

    Args:
        analyzer: BettaFish情感分析器
        stock_code: 股票代码
        stock_name: 股票名称
        limit_up_count: 近10日涨停次数
        growth_coeff: 行业成长系数

    Returns:
        (情绪倾向分, 情感分析详情)
    """
    print(f"  正在获取 {stock_name}（{stock_code}）的真实舆情数据...")

    # 使用舆情数据获取器获取真实数据
    fetcher = SentimentDataFetcher()
    sentiment_data = fetcher.fetch_from_eastmoney_guba(stock_code, stock_name, limit=30)

    if not sentiment_data:
        print(f"  ⚠️ 未能获取到真实舆情数据")
        print(f"  ⚠️ 数据源可能不可用或股票代码不正确")
        return 0.0, {
            'label': 'neutral',
            'confidence': 0.0,
            'avg_positive': 0.0,
            'avg_negative': 0.0,
            'text_count': 0,
            'details': [],
            'data_source_missing': True,
            'reason': '未能获取到真实舆情数据'
        }

    print(f"  ✅ 成功获取 {len(sentiment_data)} 条舆情数据")

    # 提取文本内容进行情感分析
    texts = [item['content'] for item in sentiment_data]

    # 批量情感分析
    sentiment_results = []
    for text in texts:
        try:
            result = analyzer.analyze(text)
            sentiment_results.append({
                'label': result.label,
                'confidence': result.confidence,
                'positive_score': result.positive_score,
                'negative_score': result.negative_score,
                'neutral_score': result.neutral_score,
                'fine_emotions': result.fine_emotions
            })
        except Exception as e:
            print(f"  ⚠️ 情感分析失败: {e}")
            continue

    if not sentiment_results:
        print(f"  ⚠️ 情感分析结果为空")
        return 0.0, {
            'label': 'neutral',
            'confidence': 0.0,
            'avg_positive': 0.0,
            'avg_negative': 0.0,
            'text_count': 0,
            'details': [],
            'data_source_missing': True,
            'reason': '情感分析结果为空'
        }

    # 统计情感分布
    from collections import Counter
    label_counts = Counter([r['label'] for r in sentiment_results])
    total = len(sentiment_results)

    positive_count = label_counts.get('positive', 0)
    negative_count = label_counts.get('negative', 0)
    neutral_count = label_counts.get('neutral', 0)

    # 计算平均分数
    avg_positive = sum(r['positive_score'] for r in sentiment_results) / total
    avg_negative = sum(r['negative_score'] for r in sentiment_results) / total
    avg_confidence = sum(r['confidence'] for r in sentiment_results) / total

    # 确定主要情感标签
    if positive_count > negative_count:
        label = 'positive'
    elif negative_count > positive_count:
        label = 'negative'
    else:
        label = 'neutral'

    # 计算情绪倾向分（0-100）
    # 正面情绪越多，分数越高
    sentiment_score = (positive_count / total * 100) if total > 0 else 0

    print(f"  情感统计: 正面{positive_count}条, 负面{negative_count}条, 中性{neutral_count}条")
    print(f"  平均分数: 正面{avg_positive:.2f}, 负面{avg_negative:.2f}, 置信度{avg_confidence:.2f}")
    print(f"  最终情绪倾向: {label} ({sentiment_score:.1f}分)")

    # 返回详细分析结果
    return sentiment_score, {
        'label': label,
        'confidence': avg_confidence,
        'avg_positive': avg_positive,
        'avg_negative': avg_negative,
        'text_count': total,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'neutral_count': neutral_count,
        'details': sentiment_results[:10],  # 返回前10条详细分析
        'data_source': '东方财富股吧',
        'data_source_missing': False
    }


def _calculate_sentiment_trend(limit_up_count: int, growth_coeff: float) -> float:
    """
    计算情绪倾向（降级方案）

    基于涨停情况和行业成长判断市场情绪

    Args:
        limit_up_count: 近10日涨停次数
        growth_coeff: 行业成长系数

    Returns:
        情绪倾向分（0-100）
    """
    # 涨停次数多 + 高成长行业 = 正面情绪主导
    if limit_up_count >= 2 and growth_coeff >= 0.7:
        score = 100  # 正面情绪主导
        print(f"  情绪倾向: {score}/100（正面情绪主导，涨停密集+高成长）")
    elif limit_up_count >= 1 and growth_coeff >= 0.7:
        score = 80   # 正面情绪
        print(f"  情绪倾向: {score}/100（正面情绪，有涨停+高成长）")
    elif limit_up_count >= 1:
        score = 60   # 中性偏正面
        print(f"  情绪倾向: {score}/100（中性偏正面，有涨停）")
    else:
        score = 40   # 中性
        print(f"  情绪倾向: {score}/100（中性，无涨停表现）")

    return score


def _calculate_leader_attention(limit_up_count: int, growth_coeff: float,
                                concepts: List[str] = None) -> float:
    """
    计算龙头关注度

    基于涨停次数和行业成长判断是否被市场认可为龙头

    Args:
        limit_up_count: 近10日涨停次数
        growth_coeff: 行业成长系数
        concepts: 概念板块列表

    Returns:
        龙头关注度分（0-100）
    """
    # 涨停次数多 + 高成长 = 龙头关注度高
    if limit_up_count >= 3:
        score = 100  # 龙一/龙二
        print(f"  龙头关注: {score}/100（市场龙头，连续涨停）")
    elif limit_up_count >= 2 and growth_coeff >= 0.7:
        score = 90   # 潜在龙头
        print(f"  龙头关注: {score}/100（潜在龙头，多次涨停+高成长）")
    elif limit_up_count == 1 and growth_coeff >= 0.7:
        score = 70   # 板块内关注
        print(f"  龙头关注: {score}/100（板块内关注，有涨停+高成长）")
    elif limit_up_count == 1:
        score = 50   # 一般关注
        print(f"  龙头关注: {score}/100（一般关注，有涨停）")
    else:
        score = 30   # 跟风股
        print(f"  龙头关注: {score}/100（跟风股，无涨停）")

    return score


def _get_sentiment_level(score: float) -> str:
    """根据舆情热度分返回级别"""
    if score >= 80:
        return "🔥 爆热"
    elif score >= 60:
        return "📈 热门"
    elif score >= 40:
        return "😐 一般"
    else:
        return "❄️ 冷门"


# 测试代码
if __name__ == "__main__":
    # 测试案例1：高成长龙头
    print("测试案例1：高成长龙头（近10日涨停3次）")
    result = calculate_sentiment_score(
        stock_code="002594.SZ",
        stock_name="比亚迪",
        limit_up_count=3,
        growth_coeff=1.0,
        concepts=["新能源车", "特斯拉"]
    )

    print(f"\nBettaFish详细分析:")
    if result.get('sentiment_detail'):
        detail = result['sentiment_detail']
        print(f"  情感极性: {detail.get('label', '未知')}")
        print(f"  置信度: {detail.get('confidence', 0):.2f}")
        print(f"  正面分: {detail.get('avg_positive', 0):.2f}")
        print(f"  负面分: {detail.get('avg_negative', 0):.2f}")
        print(f"  分析文本数: {detail.get('text_count', 0)}")

    # 测试案例2：一般股票
    print("\n" + "="*60)
    print("测试案例2：一般股票（近10日无涨停）")
    result = calculate_sentiment_score(
        stock_code="600000.SH",
        stock_name="浦发银行",
        limit_up_count=0,
        growth_coeff=0.3,
        concepts=["银行"]
    )
