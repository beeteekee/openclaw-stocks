#!/usr/bin/env python3
"""龙头识别优化模块 - 基于封板时间、带动效应、板块地位等维度更精确地识别龙头"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class DragonLeaderIdentifier:
    """龙头识别器（优化版）"""

    def __init__(self, cache_file: str = None):
        """
        初始化龙头识别器

        Args:
            cache_file: 缓存文件路径，用于存储龙头识别历史
        """
        if cache_file is None:
            cache_file = '/Users/likan/.openclaw/workspace/dragon_leader_cache.json'
        self.cache_file = cache_file

        # 加载历史数据
        self.history = self._load_history()

    def _load_history(self) -> Dict:
        """加载历史数据"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载龙头识别历史失败: {e}")
                return {}
        return {}

    def _save_history(self):
        """保存历史数据"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存龙头识别历史失败: {e}")

    def identify_leader(self, stock_code: str, stock_name: str,
                      industry: str, limit_up_count: int,
                      growth_coeff: float, concepts: List[str] = None,
                      market_cap: float = None,
                      limit_up_time: str = None) -> Dict:
        """
        识别龙头股（优化版）

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            industry: 所属行业
            limit_up_count: 近10日涨停次数
            growth_coeff: 行业成长系数
            concepts: 概念板块列表
            market_cap: 总市值（亿元）
            limit_up_time: 封板时间（格式：HH:MM:SS）

        Returns:
            dict: 龙头识别结果
        """
        print("\n" + "="*60)
        print("龙头识别分析（优化版）")
        print("="*60)

        # 1. 封板时间评分（0-100分，权重20%）
        time_score = self._calculate_limit_up_time_score(limit_up_time)

        # 2. 带动效应评分（0-100分，权重30%）
        effect_score = self._calculate_board_effect_score(
            stock_code, industry, limit_up_count, growth_coeff
        )

        # 3. 板块地位评分（0-100分，权重20%）
        status_score = self._calculate_board_status_score(
            stock_code, industry, market_cap, growth_coeff
        )

        # 4. 涨停频率评分（0-100分，权重30%）
        frequency_score = self._calculate_limit_up_frequency_score(limit_up_count)

        # 综合龙头得分
        leader_score = (time_score * 0.2 +
                       effect_score * 0.3 +
                       status_score * 0.2 +
                       frequency_score * 0.3)

        # 龙头类型判定
        leader_type = self._determine_leader_type(leader_score, limit_up_count)

        # 龙头级别
        leader_level = self._determine_leader_level(leader_score)

        result = {
            'leader_score': round(leader_score, 1),
            'leader_type': leader_type,
            'leader_level': leader_level,
            'scores': {
                'time_score': time_score,
                'effect_score': effect_score,
                'status_score': status_score,
                'frequency_score': frequency_score
            }
        }

        print(f"\n🎯 龙头识别得分: {leader_score:.1f}/100")
        print(f"  ├─ 封板时间: {time_score}/100 (权重20%)")
        print(f"  ├─ 带动效应: {effect_score}/100 (权重30%)")
        print(f"  ├─ 板块地位: {status_score}/100 (权重20%)")
        print(f"  └─ 涨停频率: {frequency_score}/100 (权重30%)")
        print(f"  龙头类型: {leader_type}")
        print(f"  龙头级别: {leader_level}")

        # 保存识别结果
        self._save_leader_result(stock_code, stock_name, result)

        return result

    def _calculate_limit_up_time_score(self, limit_up_time: str) -> float:
        """
        计算封板时间评分

        Args:
            limit_up_time: 封板时间（格式：HH:MM:SS）

        Returns:
            封板时间评分（0-100）
        """
        # 数据求真原则：没有封板时间数据时，不使用假设数据
        if limit_up_time is None:
            print("  ⚠️ 缺少封板时间数据（需要从Level-2数据或专业数据源获取）")
            print("  ⚠️ 封板时间评分功能暂时禁用")
            return 0.0  # 没有数据时不评分

        try:
            # 解析封板时间
            time_parts = limit_up_time.split(':')
            hours = int(time_parts[0])
            minutes = int(time_parts[1])

            # 转换为分钟数
            total_minutes = hours * 60 + minutes

            # 评分标准：
            # 早盘封板（9:30-10:30）：100分（最强）
            # 上午封板（10:30-11:30）：80分
            # 下午开盘封板（13:00-14:00）：70分
            # 下午中段封板（14:00-14:30）：50分
            # 收盘前封板（14:30-15:00）：30分

            if total_minutes <= 60:  # 9:30-10:30
                score = 100
                reason = "早盘封板（9:30-10:30）"
            elif total_minutes <= 90:  # 10:30-11:30
                score = 80
                reason = "上午封板（10:30-11:30）"
            elif total_minutes <= 780:  # 13:00-14:00
                score = 70
                reason = "下午开盘封板（13:00-14:00）"
            elif total_minutes <= 870:  # 14:00-14:30
                score = 50
                reason = "下午中段封板（14:00-14:30）"
            else:  # 14:30-15:00
                score = 30
                reason = "收盘前封板（14:30-15:00）"

            print(f"  封板时间: {score}/100")
            print(f"    （{reason}）")

            return score

        except Exception as e:
            print(f"  ⚠️ 解析封板时间失败: {e}")
            return 0.0

    def _calculate_board_effect_score(self, stock_code: str, industry: str,
                                    limit_up_count: int, growth_coeff: float) -> float:
        """
        计算带动效应评分

        ⚠️ 数据求真原则：真正的带动效应应该是"这只股涨停后，同板块有多少只跟风涨停"
       当前实现基于涨停次数和行业成长推断，这是不严谨的
       需要获取板块涨停关系数据才能准确计算

        Args:
            stock_code: 股票代码
            industry: 所属行业
            limit_up_count: 近10日涨停次数
            growth_coeff: 行业成长系数

        Returns:
            带动效应评分（0-100）
        """
        print(f"  ⚠️ 缺少板块涨停关系数据（无法准确计算带动效应）")
        print(f"  ⚠️ 带动效应评分功能暂时禁用")
        print(f"  ⚠️ 真正的带动效应需要：这只股涨停后，同板块有多少只跟风涨停")

        return 0.0

    def _calculate_board_status_score(self, stock_code: str, industry: str,
                                   market_cap: float, growth_coeff: float) -> float:
        """
        计算板块地位评分

        Args:
            stock_code: 股票代码
            industry: 所属行业
            market_cap: 总市值（亿元）
            growth_coeff: 行业成长系数

        Returns:
            板块地位评分（0-100）
        """
        # 数据求真原则：没有市值数据时，不使用假设数据
        if market_cap is None:
            print("  ⚠️ 缺少市值数据")
            print("  ⚠️ 板块地位评分功能暂时禁用")
            return 0.0  # 没有数据时不评分

        if market_cap > 500:
            score = 100
            reason = "超大市值，板块龙头"
        elif market_cap > 200:
            score = 90
            reason = "大市值，板块核心"
        elif market_cap > 100:
            score = 80
            reason = "中市值，板块重要成员"
        elif market_cap > 50:
            score = 70
            reason = "中小市值，板块活跃成员"
        else:
            score = 60
            reason = "小市值，板块潜在龙头"

        # 高成长行业加成
        if growth_coeff >= 0.7:
            score = min(100, score + 10)
            reason += " + 高成长行业加成"

        print(f"  板块地位: {score}/100")
        print(f"    （{reason}）")

        return score

    def _calculate_limit_up_frequency_score(self, limit_up_count: int) -> float:
        """
        计算涨停频率评分

        Args:
            limit_up_count: 近10日涨停次数

        Returns:
            涨停频率评分（0-100）
        """
        if limit_up_count >= 3:
            score = 100
            reason = "连续涨停（≥3次）"
        elif limit_up_count == 2:
            score = 80
            reason = "两次涨停"
        elif limit_up_count == 1:
            score = 60
            reason = "一次涨停"
        else:
            score = 30
            reason = "无涨停"

        print(f"  涨停频率: {score}/100")
        print(f"    （{reason}）")

        return score

    def _determine_leader_type(self, leader_score: float, limit_up_count: int) -> str:
        """
        判定龙头类型

        Args:
            leader_score: 龙头得分
            limit_up_count: 近10日涨停次数

        Returns:
            龙头类型
        """
        if leader_score >= 90 and limit_up_count >= 2:
            return "龙一"  # 市场龙头
        elif leader_score >= 80 and limit_up_count >= 2:
            return "龙二"  # 板块龙头
        elif leader_score >= 70 and limit_up_count >= 1:
            return "潜在龙头"  # 潜在龙头
        elif limit_up_count >= 1:
            return "活跃股"  # 活跃股
        else:
            return "跟风股"  # 跟风股

    def _determine_leader_level(self, leader_score: float) -> str:
        """
        判定龙头级别

        Args:
            leader_score: 龙头得分

        Returns:
            龙头级别
        """
        if leader_score >= 90:
            return "⭐⭐⭐ 顶级龙头"
        elif leader_score >= 80:
            return "⭐⭐ 核心龙头"
        elif leader_score >= 70:
            return "⭐ 重要龙头"
        elif leader_score >= 60:
            return "一般龙头"
        else:
            return "跟风股"

    def _save_leader_result(self, stock_code: str, stock_name: str, result: Dict):
        """
        保存龙头识别结果

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            result: 龙头识别结果
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if stock_code not in self.history:
            self.history[stock_code] = {
                'code': stock_code,
                'name': stock_name,
                'results': []
            }

        # 添加新的识别结果
        self.history[stock_code]['results'].append({
            'timestamp': timestamp,
            'leader_score': result['leader_score'],
            'leader_type': result['leader_type'],
            'leader_level': result['leader_level'],
            'scores': result['scores']
        })

        # 只保留最近10次记录
        self.history[stock_code]['results'] = self.history[stock_code]['results'][-10:]

        # 保存历史数据
        self._save_history()

    def get_leader_history(self, stock_code: str) -> Dict:
        """
        获取龙头识别历史

        Args:
            stock_code: 股票代码

        Returns:
            dict: 龙头识别历史
        """
        if stock_code not in self.history:
            return {
                'error': f'股票 {stock_code} 没有龙头识别历史'
            }

        return self.history[stock_code]


# 测试代码
if __name__ == "__main__":
    # 初始化龙头识别器
    identifier = DragonLeaderIdentifier()

    # 测试案例1：顶级龙头
    print("测试案例1：顶级龙头（比亚迪）")
    result = identifier.identify_leader(
        stock_code="002594.SZ",
        stock_name="比亚迪",
        industry="汽车整车",
        limit_up_count=3,
        growth_coeff=1.0,
        concepts=["新能源车", "特斯拉"],
        market_cap=8311,
        limit_up_time="09:35:20"
    )

    # 测试案例2：板块龙头
    print("\n" + "="*60)
    print("测试案例2：板块龙头")
    result = identifier.identify_leader(
        stock_code="300750.SZ",
        stock_name="宁德时代",
        industry="电气设备",
        limit_up_count=2,
        growth_coeff=1.0,
        concepts=["锂电池", "储能"],
        market_cap=15000,
        limit_up_time="10:15:30"
    )

    # 测试案例3：跟风股
    print("\n" + "="*60)
    print("测试案例3：跟风股")
    result = identifier.identify_leader(
        stock_code="600000.SH",
        stock_name="浦发银行",
        industry="银行",
        limit_up_count=0,
        growth_coeff=0.3,
        concepts=["银行"],
        market_cap=2000,
        limit_up_time=None
    )
