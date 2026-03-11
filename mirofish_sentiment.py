#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiroFish 舆情分析模块
基于MiroFish架构的简化版舆情分析
使用真实数据源（东方财富股吧）
"""

import re
import json
from typing import List, Dict, Tuple
from collections import Counter


class MiroFishSentimentAnalyzer:
    """
    MiroFish情感分析器 - 基于规则的轻量级实现
    用于分析股票评论和舆情数据
    """

    def __init__(self):
        self._load_dictionaries()

    def _load_dictionaries(self):
        """加载情感词典"""

        # 正面词汇词典
        self.positive_words = {
            '好', '棒', '优秀', '喜欢', '爱', '赞', '完美', '推荐', '满意', '不错',
            '开心', '快乐', '幸福', '成功', '漂亮', '厉害', '强', '牛', '给力',
            '值得', '惊喜', '超预期', '优质', '专业', '贴心', '靠谱', '真香',
            '突破', '上涨', '涨停', '反弹', '企稳', '向好', '反转', '拉升',
            '业绩', '增长', '盈利', '分红', '回购', '增持', '利好', '政策',
            '技术领先', '创新', '领先', '龙头', '龙头股', '第一', '霸主',
            '潜力', '成长', '爆发', '加速', '扩张', '增长', '提升',
            '买入', '持有', '看好', '推荐', '增持', '目标价', '上涨空间',
            'good', 'great', 'excellent', 'amazing', 'love', 'best', 'perfect',
            'awesome', 'happy', 'wonderful', 'fantastic', 'awesome', 'nice'
        }

        # 负面词汇词典
        self.negative_words = {
            '差', '糟', '烂', '讨厌', '恨', '失望', '垃圾', '恶心', '差劲', '不好',
            '难过', '伤心', '失败', '丑', '弱', '惨', '麻烦', '问题', '坑', '雷',
            '骗', '假', '贵', '不值', '后悔', '踩雷', '避雷', '智商税', '翻车',
            '下跌', '暴跌', '跌停', '调整', '回调', '崩盘', '破位', '跳水',
            '亏损', '业绩下滑', '下滑', '减持', '利空', '风险', '负面',
            '技术落后', '衰退', '萎缩', '困难', '危机', '债务', '违约',
            '卖出', '回避', '不看好', '减持', '下调', '风险大',
            'bad', 'terrible', 'awful', 'hate', 'worst', 'disappointing', 'sad',
            'angry', 'fail', 'poor', 'horrible', 'disgusting'
        }

        # 情感增强词
        self.intensifiers = {
            '非常', '特别', '很', '十分', '极其', '超级', '真的', '太', '相当',
            '绝对', '完全', '确实', '实在', '尤其', '格外', '分外',
            'so', 'very', 'extremely', 'really', 'too', 'quite', 'absolutely',
            'completely', 'especially', 'particularly'
        }

        # 否定词
        self.negations = {
            '不', '没', '无', '非', '莫', '勿', '没有', '不是', '别',
            'no', 'not', 'never', 'none', 'without', 'dont', 'doesnt', 'didnt'
        }

        # 细分情绪词典
        self.fine_emotions = {
            'joy': ['开心', '高兴', '兴奋', '愉快', '欢乐', '喜悦', 'happy', 'excited', 'joyful'],
            'trust': ['信任', '信赖', '可靠', '放心', '安心', 'trust', 'reliable'],
            'anticipation': ['期待', '盼望', '憧憬', '看好', '希望', 'expect', 'hope', 'look forward'],
            'anger': ['愤怒', '生气', '气愤', '恼火', '愤怒', 'angry', 'furious', 'mad'],
            'disappointment': ['失望', '失落', '遗憾', '沮丧', 'disappointed', 'frustrated'],
            'worry': ['担心', '焦虑', '忧虑', '害怕', '恐惧', 'worry', 'anxious', 'fear'],
            'disgust': ['厌恶', '反感', '讨厌', '恶心', 'disgust', 'dislike', 'hate'],
            'surprise': ['惊讶', '震惊', '意外', 'surprise', 'shocked', 'amazed']
        }

        # 金融情感词
        self.financial_positive = [
            '业绩增长', '净利润', '营收增长', '同比增长', '环比增长',
            '毛利率', '净利率', 'ROE', 'ROA',
            '分红', '回购', '增持', '目标价', '上涨空间',
            '突破', '企稳', '向好', '反转', '拉升'
        ]

        self.financial_negative = [
            '业绩下滑', '净利润下降', '营收下降', '同比下滑',
            '净亏损', '减值', '减持', '利空', '风险',
            '违约', '债务', '危机', '调整', '回调', '崩盘'
        ]

    def analyze(self, text: str) -> Dict:
        """
        执行情感分析

        Args:
            text: 待分析的文本

        Returns:
            分析结果字典
        """
        text_lower = text.lower()
        words = self._tokenize(text_lower)

        # 基础情感分析
        sentiment_scores = self._calculate_sentiment_scores(words, text_lower)

        # 细分情绪分析
        fine_emotions = self._identify_fine_emotions(text_lower)

        # 金融情感分析
        financial_sentiment = self._analyze_financial_sentiment(text_lower)

        return {
            'text': text,
            'label': sentiment_scores['label'],
            'confidence': sentiment_scores['confidence'],
            'positive_score': sentiment_scores['positive'],
            'negative_score': sentiment_scores['negative'],
            'neutral_score': sentiment_scores['neutral'],
            'fine_emotions': fine_emotions,
            'financial_sentiment': financial_sentiment
        }

    def _tokenize(self, text: str) -> List[str]:
        """简单的分词实现"""
        # 中文词汇（2-4字）
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
        # 英文单词
        english_words = re.findall(r'[a-z]+', text)
        return chinese_words + english_words

    def _calculate_sentiment_scores(self, words: List[str], text: str) -> Dict:
        """计算情感分数"""
        positive_count = 0
        negative_count = 0
        intensity = 1.0
        negation_active = False

        for i, word in enumerate(words):
            # 检查否定词
            if word in self.negations:
                negation_active = True
                continue

            # 检查情感增强词
            if word in self.intensifiers:
                intensity = 1.5
                continue

            # 检查情感词
            if word in self.positive_words:
                if negation_active:
                    negative_count += intensity
                    negation_active = False
                else:
                    positive_count += intensity
                intensity = 1.0

            elif word in self.negative_words:
                if negation_active:
                    positive_count += intensity
                    negation_active = False
                else:
                    negative_count += intensity
                intensity = 1.0

        # 计算最终分数
        total = positive_count + negative_count
        if total == 0:
            return {
                'label': 'neutral',
                'confidence': 0.5,
                'positive': 0.33,
                'negative': 0.33,
                'neutral': 0.34
            }

        positive_ratio = positive_count / total
        negative_ratio = negative_count / total
        neutral_ratio = 0

        # 判断情感极性
        if positive_ratio > negative_ratio * 1.5:
            label = 'positive'
            confidence = min(positive_ratio, 0.95)
        elif negative_ratio > positive_ratio * 1.5:
            label = 'negative'
            confidence = min(negative_ratio, 0.95)
        else:
            label = 'neutral'
            confidence = 0.5 + abs(positive_ratio - negative_ratio) * 0.5
            neutral_ratio = 1 - (positive_count + negative_count) / (total + 1)

        return {
            'label': label,
            'confidence': confidence,
            'positive': positive_count / (total + 1),
            'negative': negative_count / (total + 1),
            'neutral': neutral_ratio if neutral_ratio > 0 else 0.1
        }

    def _identify_fine_emotions(self, text: str) -> List[Dict]:
        """识别细分情绪"""
        emotions = []
        for emotion_type, keywords in self.fine_emotions.items():
            for keyword in keywords:
                if keyword in text:
                    emotions.append({
                        'type': emotion_type,
                        'keyword': keyword,
                        'intensity': 0.8
                    })
                    break
        return emotions

    def _analyze_financial_sentiment(self, text: str) -> Dict:
        """分析金融情感"""
        positive_count = sum(1 for kw in self.financial_positive if kw in text)
        negative_count = sum(1 for kw in self.financial_negative if kw in text)

        total = positive_count + negative_count
        if total == 0:
            return {'label': 'neutral', 'positive': 0, 'negative': 0}

        if positive_count > negative_count:
            label = 'bullish'
        elif negative_count > positive_count:
            label = 'bearish'
        else:
            label = 'neutral'

        return {
            'label': label,
            'positive': positive_count,
            'negative': negative_count
        }

    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """批量情感分析"""
        return [self.analyze(text) for text in texts]

    def calculate_sentiment_distribution(self, results: List[Dict]) -> Dict:
        """分析情感分布统计"""
        labels = [r['label'] for r in results]
        counter = Counter(labels)
        total = len(labels)

        # 计算平均置信度
        avg_confidence = sum(r['confidence'] for r in results) / total if total > 0 else 0

        # 统计细分情绪
        all_emotions = []
        for r in results:
            all_emotions.extend([e['type'] for e in r.get('fine_emotions', [])])
        emotion_counter = Counter(all_emotions)

        # 统计金融情感
        financial_labels = [r.get('financial_sentiment', {}).get('label', 'neutral') for r in results]
        financial_counter = Counter(financial_labels)

        return {
            'positive_count': counter.get('positive', 0),
            'negative_count': counter.get('negative', 0),
            'neutral_count': counter.get('neutral', 0),
            'positive_pct': round(counter.get('positive', 0) / total * 100, 2) if total > 0 else 0,
            'negative_pct': round(counter.get('negative', 0) / total * 100, 2) if total > 0 else 0,
            'neutral_pct': round(counter.get('neutral', 0) / total * 100, 2) if total > 0 else 0,
            'total': total,
            'average_confidence': round(avg_confidence, 2),
            'emotion_distribution': dict(emotion_counter.most_common(5)),
            'financial_sentiment_distribution': dict(financial_counter.most_common(3))
        }


# 便捷函数接口
def simple_sentiment_analyze(text: str) -> Dict:
    """简单情感分析接口"""
    analyzer = MiroFishSentimentAnalyzer()
    result = analyzer.analyze(text)
    return {
        'label': result['label'],
        'confidence': result['confidence'],
        'positive_score': result['positive_score'],
        'negative_score': result['negative_score'],
        'neutral_score': result['neutral_score'],
        'fine_emotions': result['fine_emotions'],
        'financial_sentiment': result['financial_sentiment']
    }


def batch_sentiment_analyze(texts: List[str]) -> List[Dict]:
    """批量情感分析接口"""
    analyzer = MiroFishSentimentAnalyzer()
    results = analyzer.analyze_batch(texts)
    return [
        {
            'label': r['label'],
            'confidence': r['confidence'],
            'positive_score': r['positive_score'],
            'negative_score': r['negative_score'],
            'neutral_score': r['neutral_score'],
            'fine_emotions': r['fine_emotions'],
            'financial_sentiment': r['financial_sentiment']
        }
        for r in results
    ]


if __name__ == '__main__':
    print("MiroFish Sentiment Analyzer")
    print("基于规则的轻量级情感分析模块")
    print("\nUsage:")
    print("  from mirofish_sentiment import MiroFishSentimentAnalyzer")
    print("  analyzer = MiroFishSentimentAnalyzer()")
    print("  result = analyzer.analyze('这个产品真的很棒！')")
    print("\n注意：本模块用于分析从东方财富股吧获取的真实数据")
    print("      严禁使用模拟数据。")
