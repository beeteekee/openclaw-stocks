#!/usr/bin/env python3
"""舆情趋势跟踪模块 - 跟踪舆情热度的时间序列，识别舆情拐点"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class SentimentTrendTracker:
    """舆情趋势跟踪器"""

    def __init__(self, cache_file: str = None):
        """
        初始化舆情趋势跟踪器

        Args:
            cache_file: 缓存文件路径，用于存储历史舆情数据
        """
        if cache_file is None:
            cache_file = '/Users/likan/.openclaw/workspace/sentiment_trend_cache.json'
        self.cache_file = cache_file

        # 加载历史舆情数据
        self.history = self._load_history()

    def _load_history(self) -> Dict:
        """加载历史舆情数据"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载历史舆情数据失败: {e}")
                return {}
        return {}

    def _save_history(self):
        """保存历史舆情数据"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存历史舆情数据失败: {e}")

    def record_sentiment(self, stock_code: str, stock_name: str,
                        sentiment_data: Dict, timestamp: str = None):
        """
        记录舆情数据

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            sentiment_data: 舆情数据
            timestamp: 时间戳（默认为当前时间）
        """
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 确保股票代码和名称在历史数据中存在
        if stock_code not in self.history:
            self.history[stock_code] = {
                'code': stock_code,
                'name': stock_name,
                'records': []
            }

        # 添加新的舆情记录
        self.history[stock_code]['records'].append({
            'timestamp': timestamp,
            'sentiment_heat_score': sentiment_data.get('sentiment_heat_score'),
            'discussion_score': sentiment_data.get('discussion_score'),
            'sentiment_trend_score': sentiment_data.get('sentiment_trend_score'),
            'leader_attention_score': sentiment_data.get('leader_attention_score'),
            'sentiment_level': sentiment_data.get('sentiment_level')
        })

        # 只保留最近30天的记录
        self._trim_history(stock_code, days=30)

        # 保存历史数据
        self._save_history()

    def _trim_history(self, stock_code: str, days: int = 30):
        """
        裁剪历史数据，只保留最近N天的记录

        Args:
            stock_code: 股票代码
            days: 保留天数
        """
        if stock_code not in self.history:
            return

        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_timestamp = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')

        # 过滤掉超过cutoff_timestamp的记录
        self.history[stock_code]['records'] = [
            record for record in self.history[stock_code]['records']
            if record['timestamp'] > cutoff_timestamp
        ]

    def get_trend(self, stock_code: str, days: int = 7) -> Dict:
        """
        获取舆情趋势

        Args:
            stock_code: 股票代码
            days: 统计天数

        Returns:
            dict: 舆情趋势数据
        """
        if stock_code not in self.history:
            return {
                'error': f'股票 {stock_code} 没有历史舆情数据'
            }

        records = self.history[stock_code]['records']

        # 只保留最近N天的记录
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_timestamp = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')

        recent_records = [
            record for record in records
            if record['timestamp'] > cutoff_timestamp
        ]

        if len(recent_records) == 0:
            return {
                'error': f'股票 {stock_code} 在最近{days}天内没有舆情数据'
            }

        # 计算趋势数据
        sentiment_scores = [r['sentiment_heat_score'] for r in recent_records]
        discussion_scores = [r['discussion_score'] for r in recent_records]
        sentiment_trend_scores = [r['sentiment_trend_score'] for r in recent_records]
        leader_attention_scores = [r['leader_attention_score'] for r in recent_records]

        # 计算平均值
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        avg_discussion = sum(discussion_scores) / len(discussion_scores)
        avg_sentiment_trend = sum(sentiment_trend_scores) / len(sentiment_trend_scores)
        avg_leader_attention = sum(leader_attention_scores) / len(leader_attention_scores)

        # 计算趋势方向
        trend_direction = self._calculate_trend_direction(sentiment_scores)

        # 计算波动率
        volatility = self._calculate_volatility(sentiment_scores)

        # 识别舆情拐点
        inflection_points = self._identify_inflection_points(sentiment_scores)

        return {
            'stock_code': stock_code,
            'stock_name': self.history[stock_code]['name'],
            'days': days,
            'record_count': len(recent_records),
            'avg_sentiment_heat_score': round(avg_sentiment, 2),
            'avg_discussion_score': round(avg_discussion, 2),
            'avg_sentiment_trend_score': round(avg_sentiment_trend, 2),
            'avg_leader_attention_score': round(avg_leader_attention, 2),
            'trend_direction': trend_direction,
            'volatility': round(volatility, 2),
            'inflection_points': inflection_points,
            'latest_score': sentiment_scores[-1],
            'earliest_score': sentiment_scores[0],
            'score_change': round(sentiment_scores[-1] - sentiment_scores[0], 2)
        }

    def _calculate_trend_direction(self, scores: List[float]) -> str:
        """
        计算趋势方向

        Args:
            scores: 舆情热度分列表

        Returns:
            str: 趋势方向（上升/下降/平稳）
        """
        if len(scores) < 3:
            return 'unknown'

        # 计算线性回归斜率
        x = list(range(len(scores)))
        y = scores

        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))

        # 斜率 = (n*Σxy - Σx*Σy) / (n*Σx² - (Σx)²)
        if n * sum_x2 - sum_x ** 2 == 0:
            return 'stable'

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)

        # 根据斜率判断趋势方向
        if slope > 0.5:
            return 'rising'  # 上升
        elif slope < -0.5:
            return 'falling'  # 下降
        else:
            return 'stable'  # 平稳

    def _calculate_volatility(self, scores: List[float]) -> float:
        """
        计算波动率

        Args:
            scores: 舆情热度分列表

        Returns:
            float: 波动率
        """
        if len(scores) < 2:
            return 0.0

        # 计算标准差
        mean = sum(scores) / len(scores)
        variance = sum((score - mean) ** 2 for score in scores) / len(scores)
        std_dev = variance ** 0.5

        # 波动率 = 标准差 / 平均值
        if mean == 0:
            return 0.0

        return std_dev / mean

    def _identify_inflection_points(self, scores: List[float]) -> List[Dict]:
        """
        识别舆情拐点

        Args:
            scores: 舆情热度分列表

        Returns:
            list: 拐点列表
        """
        if len(scores) < 4:
            return []

        inflection_points = []

        for i in range(1, len(scores) - 2):
            # 计算前后斜率
            before_slope = scores[i] - scores[i - 1]
            after_slope = scores[i + 1] - scores[i]

            # 如果斜率方向改变，则是拐点
            if (before_slope > 0 and after_slope < 0) or \
               (before_slope < 0 and after_slope > 0):
                inflection_points.append({
                    'index': i,
                    'score': scores[i],
                    'type': 'peak' if before_slope > 0 else 'valley'
                })

        return inflection_points

    def get_forecast(self, stock_code: str, days_ahead: int = 3) -> Dict:
        """
        预测舆情热度

        Args:
            stock_code: 股票代码
            days_ahead: 预测天数

        Returns:
            dict: 预测结果
        """
        if stock_code not in self.history:
            return {
                'stock_code': stock_code,
                'stock_name': '未知',
                'current_score': None,
                'trend_direction': 'unknown',
                'days_ahead': days_ahead,
                'forecast_scores': [],
                'forecast_avg': None,
                'error': f'股票 {stock_code} 没有历史舆情数据'
            }

        records = self.history[stock_code]['records']

        if len(records) < 5:
            return {
                'stock_code': stock_code,
                'stock_name': self.history[stock_code]['name'],
                'current_score': records[-1]['sentiment_heat_score'] if records else None,
                'trend_direction': 'unknown',
                'days_ahead': days_ahead,
                'forecast_scores': [],
                'forecast_avg': None,
                'error': f'股票 {stock_code} 历史数据不足，无法预测'
            }

        # 提取最近N天的舆情热度分
        recent_scores = [r['sentiment_heat_score'] for r in records[-7:]]

        # 使用简单移动平均进行预测
        avg_score = sum(recent_scores) / len(recent_scores)

        # 计算趋势
        trend_direction = self._calculate_trend_direction(recent_scores)

        # 根据趋势预测未来
        if trend_direction == 'rising':
            forecast_scores = [avg_score + i * 2 for i in range(1, days_ahead + 1)]
        elif trend_direction == 'falling':
            forecast_scores = [avg_score - i * 2 for i in range(1, days_ahead + 1)]
        else:
            forecast_scores = [avg_score] * days_ahead

        # 确保预测分数在合理范围内
        forecast_scores = [max(0, min(100, score)) for score in forecast_scores]

        return {
            'stock_code': stock_code,
            'stock_name': self.history[stock_code]['name'],
            'current_score': recent_scores[-1],
            'trend_direction': trend_direction,
            'days_ahead': days_ahead,
            'forecast_scores': forecast_scores,
            'forecast_avg': round(sum(forecast_scores) / len(forecast_scores), 2)
        }


# 测试代码
if __name__ == "__main__":
    # 初始化舆情趋势跟踪器
    tracker = SentimentTrendTracker()

    # 测试案例1：记录舆情数据
    print("测试案例1：记录舆情数据")
    tracker.record_sentiment(
        stock_code="002594.SZ",
        stock_name="比亚迪",
        sentiment_data={
            'sentiment_heat_score': 85.0,
            'discussion_score': 100,
            'sentiment_trend_score': 50,
            'leader_attention_score': 100,
            'sentiment_level': '🔥 爆热'
        }
    )

    # 测试案例2：获取舆情趋势
    print("\n" + "="*60)
    print("测试案例2：获取舆情趋势")
    trend = tracker.get_trend("002594.SZ", days=7)
    print(f"股票代码: {trend.get('stock_code')}")
    print(f"股票名称: {trend.get('stock_name')}")
    print(f"统计天数: {trend.get('days')}天")
    print(f"记录数量: {trend.get('record_count')}条")
    print(f"平均舆情热度: {trend.get('avg_sentiment_heat_score')}/100")
    print(f"趋势方向: {trend.get('trend_direction')}")
    print(f"波动率: {trend.get('volatility')}")
    print(f"最新得分: {trend.get('latest_score')}/100")
    print(f"最早得分: {trend.get('earliest_score')}/100")
    print(f"得分变化: {trend.get('score_change')}")
    if trend.get('inflection_points'):
        print(f"拐点数量: {len(trend['inflection_points'])}个")

    # 测试案例3：预测舆情热度
    print("\n" + "="*60)
    print("测试案例3：预测舆情热度")
    forecast = tracker.get_forecast("002594.SZ", days_ahead=3)
    print(f"股票代码: {forecast.get('stock_code')}")
    print(f"股票名称: {forecast.get('stock_name')}")
    print(f"当前得分: {forecast.get('current_score')}/100")
    print(f"趋势方向: {forecast.get('trend_direction')}")
    print(f"预测天数: {forecast.get('days_ahead')}天")
    print(f"预测得分: {forecast.get('forecast_scores')}")
    print(f"预测平均: {forecast.get('forecast_avg')}/100")
