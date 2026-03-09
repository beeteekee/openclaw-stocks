#!/usr/bin/env python3
"""养家心法选股服务 - 提供股票分析API"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from technical_analysis import calculate_technical_score
import json
import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 从环境变量读取配置
TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN')
STATS_FILE = os.getenv('STATS_FILE', '/Users/likan/.openclaw/workspace/query_stats.json')
TOP3_TODAY_FILE = os.getenv('TOP3_TODAY_FILE', '/Users/likan/.openclaw/workspace/top3_today_result.csv')
FEISHU_APP_ID = os.getenv('FEISHU_APP_ID', '')
FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET', '')
FEISHU_REGION = os.getenv('FEISHU_REGION', 'cn')

# Flask 服务端口（默认5000）
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))

# 行业成长系数表
INDUSTRY_GROWTH = {
    # 高成长 (1.0)
    'AI算力': 1.0, '半导体': 1.0, '集成电路': 1.0,
    '新能源车': 1.0, '光伏': 1.0, '储能': 1.0, '未来能源': 1.0,
    '机器人': 1.0, '具身智能': 1.0,
    '航空航天': 1.0, '低空经济': 1.0,
    '生物医药': 1.0,
    '量子计算': 1.0, '脑机接口': 1.0, '6G': 1.0,
    '锂电': 1.0, '锂电池': 1.0, '磷酸铁锂': 1.0, '新能源': 1.0,
    '特斯拉': 1.0, '比亚迪': 1.0, '蔚来': 1.0, '小鹏': 1.0, '理想': 1.0,
    # 中成长 (0.7)
    '医药生物': 0.7, '5G': 0.7, '新材料': 0.7, '高端制造': 0.7, '汽车电子': 0.7,
    '通信设备': 0.7, '通信': 0.7, '元器件': 0.7, '电子': 0.7, '专用设备': 0.7,
    '汽车整车': 0.7, '汽车制造': 0.7,
    # 低成长 (0.3)
    '农业': 0.3, '银行': 0.3, '钢铁': 0.3, '煤炭': 0.3, '白酒': 0.3, '公用事业': 0.3, '食品': 0.3,
    # 无成长 (0.1)
    '综合类': 0.1, '建筑装饰': 0.1, '商业贸易': 0.1, '纺织服装': 0.1, '机械基件': 0.1
}

def load_query_stats():
    """从文件加载统计数据"""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载统计数据失败: {e}")
    return {
        'total_count': 0,
        'stock_queries': {}
    }

def save_query_stats():
    """保存统计数据到文件"""
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(QUERY_STATS, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ 保存统计数据失败: {e}")

# 查询统计
# 从文件加载统计数据（持久化）
QUERY_STATS = load_query_stats()

# 初始化Tushare API
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

def get_industry_growth_coefficient(industry, concepts=None):
    """
    根据行业名称和概念板块获取成长系数

    优先匹配概念板块中的高成长概念，如果没有匹配则使用行业字段

    Args:
        industry: 行业名称（来自Tushare的industry字段）
        concepts: 概念板块列表（来自Tushare的concept_detail接口）

    Returns:
        成长系数（1.0, 0.7, 0.3, 0.1）
    """
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
    """市值扣分逻辑（根据V8.0标准）"""
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

def get_ma250_score(price, ma250):
    """250日均线评分"""
    if price <= 0 or ma250 <= 0:
        return 0

    ratio = price / ma250

    if price > ma250 and ratio > 1.05:
        return 100
    elif price > ma250 and ratio > 1.02:
        return 80
    elif price > ma250:
        return 60
    elif price < ma250 and ratio > 0.98:
        return 40
    elif price < ma250 and ratio > 0.95:
        return 20
    else:
        return 0

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

def identify_dragon(stock_code, industry):
    """
    识别龙头属性

    龙头识别标准：
    - 板块内第一个涨停
    - 封板最坚决（开盘即涨停或早盘快速封板）
    - 对板块带动效应最强

    龙头属性评分：
    - 板块龙一：100分
    - 板块龙二：80分
    - 市场龙头：90分（多个板块的核心龙头）
    - 潜在龙头：60分
    - 跟风股：0分（坚决回避）

    注意：由于Tushare数据限制和性能考虑，这里使用简化逻辑
    后续可通过缓存或批量查询优化
    """
    try:
        # 获取当日市场数据
        today = datetime.now().strftime('%Y%m%d')

        # 首先检查目标股票是否涨停（避免大量查询）
        stock_daily = pro.daily(ts_code=stock_code, trade_date=today)
        if len(stock_daily) == 0:
            return 60, '潜在龙头', '无法获取当日数据'

        stock_pct_chg = stock_daily.iloc[0]['pct_chg']

        # 如果目标股票没有涨停（涨幅<9.5%），直接判断为跟风股
        if stock_pct_chg < 9.5:
            return 0, '跟风股', '未涨停，不是龙头'

        # 如果目标股票涨停了，需要判断是否是龙头
        # 但由于查询板块内所有股票的性能问题，暂时简化处理

        # 获取近10日涨停次数
        end_date = today
        start_date = (datetime.now() - timedelta(days=15)).strftime('%Y%m%d')

        recent_df = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)

        if len(recent_df) == 0:
            return 60, '潜在龙头', '无法获取历史数据'

        limit_up_count = len(recent_df[recent_df['pct_chg'] >= 9.5])

        # 根据涨停次数判断龙头属性
        if limit_up_count >= 3:
            return 100, '板块龙一', f'近10日涨停{limit_up_count}次，可能是板块龙一'
        elif limit_up_count == 2:
            return 80, '板块龙二', f'近10日涨停{limit_up_count}次，可能是板块龙二'
        elif limit_up_count == 1:
            return 60, '潜在龙头', f'近10日涨停{limit_up_count}次，带动效应未确认'
        else:
            return 60, '潜在龙头', '当日首次涨停，带动效应未确认'

    except Exception as e:
        print(f"识别龙头失败: {e}")
        return 60, '潜在龙头', '识别失败，使用默认值'

@app.route('/')
def index():
    """主页 - 返回前端页面"""
    return app.send_static_file('stock-analysis.html')

def get_market_emotion_data():
    """
    获取市场情绪相关数据

    基于多维度数据：
    - 涨停板数量（衡量市场热度）
    - 跌停板数量（衡量恐慌程度）
    - 核按钮数量（跌幅>5%，衡量亏钱效应）
    - 市场成交额（衡量资金活跃度）
    - 换手率（衡量市场活跃度）
    - 指数涨跌幅（衡量趋势）
    - 涨停股票列表（用于连板高度和板块效应计算）

    Returns:
        dict: 包含市场情绪数据
    """
    try:
        today = datetime.now().strftime('%Y%m%d')

        # 1. 获取指数数据（上证指数）
        index_data = pro.index_daily(
            ts_code='000001.SH',
            start_date=(datetime.now() - timedelta(days=5)).strftime('%Y%m%d'),
            end_date=today
        )

        if len(index_data) == 0:
            return None

        # 2. 获取全市场数据（筛选当日）
        # 注意：这个操作可能会较慢，需要性能优化
        all_stocks = pro.daily(
            trade_date=today,
            fields='ts_code,pct_chg,close,vol,amount'
        )

        if len(all_stocks) == 0:
            return None

        # 3. 计算涨停跌停统计
        limit_up_stocks = all_stocks[all_stocks['pct_chg'] >= 9.5]
        limit_up = len(limit_up_stocks)
        limit_down = len(all_stocks[all_stocks['pct_chg'] <= -9.5])
        nuclear = len(all_stocks[all_stocks['pct_chg'] <= -5])

        # 4. 计算市场成交额（转换为亿元）
        total_amount = all_stocks['amount'].sum() / 100000000

        # 5. 计算指数数据
        latest_index = index_data.iloc[-1]
        index_pct_chg = latest_index['pct_chg']

        # 计算近3日累计涨跌
        recent_3 = index_data.tail(3)
        total_chg_3 = recent_3['pct_chg'].sum()

        # 6. 获取换手率（需要daily_basic数据）
        try:
            basic_data = pro.daily_basic(
                trade_date=today,
                fields='ts_code,turnover_rate'
            )
            avg_turnover = basic_data['turnover_rate'].mean() if len(basic_data) > 0 else 0
        except:
            avg_turnover = 0

        # 7. 节假日效应处理（第二阶段功能）
        holiday_effect = calculate_holiday_effect()

        return {
            'limit_up_count': limit_up,
            'limit_down_count': limit_down,
            'nuclear_count': nuclear,
            'total_amount': total_amount,
            'avg_turnover': avg_turnover,
            'index_pct_chg': index_pct_chg,
            'total_chg_3': total_chg_3,
            'limit_up_stocks': limit_up_stocks,
            'holiday_effect': holiday_effect
        }

    except Exception as e:
        print(f"获取市场情绪数据失败: {e}")
        return None


def calculate_holiday_effect():
    """
    计算节假日效应（第二阶段功能）

    节假日前后市场行为可能不同：
    - 节假日前：成交额通常降低，资金趋于谨慎
    - 节假日后：成交额可能恢复，资金重新活跃

    Returns:
        float: 节假日影响系数（0.5-1.0）
    """
    try:
        # 简化处理：判断是否接近常见节假日
        # 这里可以扩展为更精确的节假日检测
        from datetime import date

        today = datetime.now().date()

        # 春节前后（农历正月初一前后7天）
        # 中秋、国庆等节日可以类似处理
        # 这里简化为判断是否是周末或接近月末

        # 判断是否是周五或节假日前最后一个交易日
        weekday = today.weekday()  # 0=周一, 4=周五

        if weekday == 4:  # 周五
            return 0.8  # 节假日前，成交额可能降低
        elif weekday == 0:  # 周一
            return 1.0  # 节假日后，成交额可能恢复
        else:
            return 1.0  # 正常交易日

    except Exception as e:
        print(f"计算节假日效应失败: {e}")
        return 1.0


def calculate_limit_up_score(data, limit_up_stocks):
    """
    计算涨停热度得分（30分）

    包括：
    - 涨停板数量（15分）
    - 连板高度（10分）
    - 板块效应（5分）

    Args:
        data: 市场情绪数据字典
        limit_up_stocks: 涨停股票列表，包含详细信息
    """
    score = 0

    # 涨停板数量（15分）
    limit_up = data.get('limit_up_count', 0)
    if limit_up > 100:
        score += 15
    elif limit_up > 50:
        score += 12
    elif limit_up > 20:
        score += 8
    elif limit_up > 10:
        score += 4
    else:
        score += 0

    # 连板高度（10分） - 第二阶段功能
    max_limit_up_days = calculate_max_limit_up_days()
    if max_limit_up_days >= 7:
        score += 10
    elif max_limit_up_days >= 5:
        score += 8
    elif max_limit_up_days >= 3:
        score += 5
    elif max_limit_up_days >= 2:
        score += 3
    else:
        score += 0

    # 板块效应（5分） - 第二阶段功能
    board_effect_score = calculate_board_effect(limit_up_stocks)
    score += board_effect_score

    return score


def calculate_max_limit_up_days():
    """
    计算市场最高连板高度（第二阶段功能）

    通过获取所有股票的历史数据，统计连续涨停的最大天数
    """
    try:
        today = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')

        # 获取近30天的市场数据（性能考虑，只获取涨停股票）
        all_limit_up = pro.daily(
            start_date=start_date,
            end_date=today,
            fields='ts_code,trade_date,pct_chg'
        )

        if len(all_limit_up) == 0:
            return 0

        # 筛选涨停股票
        limit_up_stocks = all_limit_up[all_limit_up['pct_chg'] >= 9.5]

        if len(limit_up_stocks) == 0:
            return 0

        # 按股票分组，计算每只股票的连板高度
        max_days = 0
        stock_groups = limit_up_stocks.groupby('ts_code')

        for stock_code, group in stock_groups:
            # 按日期排序
            group = group.sort_values('trade_date')

            # 计算连续涨停天数
            consecutive_days = 0
            max_consecutive = 0

            for idx, row in group.iterrows():
                if row['pct_chg'] >= 9.5:
                    consecutive_days += 1
                    max_consecutive = max(max_consecutive, consecutive_days)
                else:
                    consecutive_days = 0

            max_days = max(max_days, max_consecutive)

        return max_days

    except Exception as e:
        print(f"计算连板高度失败: {e}")
        return 0


def calculate_board_effect(limit_up_stocks):
    """
    计算板块效应得分（5分）（第二阶段功能）

    通过统计每个板块的涨停股票数量，判断是否有明显的领涨板块
    """
    try:
        if len(limit_up_stocks) == 0:
            return 0

        # 获取涨停股票的行业信息
        stock_codes = limit_up_stocks['ts_code'].tolist()

        # 分批查询，避免一次性请求过多
        batch_size = 100
        all_stocks_info = []

        for i in range(0, len(stock_codes), batch_size):
            batch = stock_codes[i:i+batch_size]
            stocks = pro.stock_basic(ts_code=batch, fields='ts_code,industry')
            all_stocks_info.append(stocks)

        if not all_stocks_info:
            return 0

        # 合并所有股票信息
        all_stocks_df = pd.concat(all_stocks_info, ignore_index=True)

        # 统计每个板块的涨停数量
        industry_count = all_stocks_df.groupby('industry').size().sort_values(ascending=False)

        if len(industry_count) == 0:
            return 0

        # 判断板块效应
        max_count = industry_count.iloc[0]
        total_count = len(limit_up_stocks)

        # 如果最大板块占比超过30%，说明有明显的领涨板块
        if max_count / total_count >= 0.3:
            return 5
        elif max_count / total_count >= 0.2:
            return 3
        elif max_count / total_count >= 0.1:
            return 1
        else:
            return 0

    except Exception as e:
        print(f"计算板块效应失败: {e}")
        return 0


def calculate_loss_effect_score(data):
    """
    计算亏钱效应得分（30分）

    包括：
    - 跌停板数量（15分）
    - 核按钮数量（10分）
    - 炸板率（5分） - 第二阶段功能
    """
    score = 0

    # 跌停板数量（15分）
    limit_down = data.get('limit_down_count', 0)
    if limit_down < 5:
        score += 15
    elif limit_down < 20:
        score += 10
    elif limit_down < 50:
        score += 5
    elif limit_down < 100:
        score += 2
    else:
        score += 0

    # 核按钮数量（10分）
    nuclear = data.get('nuclear_count', 0)
    if nuclear < 20:
        score += 10
    elif nuclear < 50:
        score += 7
    elif nuclear < 100:
        score += 3
    else:
        score += 0

    # 炸板率（5分） - 第二阶段功能
    explosion_rate = calculate_explosion_rate(data)
    score += explosion_rate

    return score


def calculate_explosion_rate(data):
    """
    计算炸板率得分（5分）（第二阶段功能）

    炸板率 = 曾经涨停但最终未涨停的股票 / 曾经涨停的股票总数

    由于Tushare限制，这里使用简化逻辑：
    通过计算接近涨停（涨幅>8%但<9.5%）的股票数量与涨停板数量的比例
    """
    try:
        today = datetime.now().strftime('%Y%m%d')

        # 获取全市场数据
        all_stocks = pro.daily(
            trade_date=today,
            fields='ts_code,pct_chg'
        )

        if len(all_stocks) == 0:
            return 0

        # 计算涨停板数量
        limit_up_count = len(all_stocks[all_stocks['pct_chg'] >= 9.5])

        # 计算接近涨停的股票数量（8% < 涨幅 < 9.5%）
        near_limit_count = len(all_stocks[(all_stocks['pct_chg'] >= 8) & (all_stocks['pct_chg'] < 9.5)])

        # 炸板率 = 接近涨停 / (涨停 + 接近涨停）
        if limit_up_count + near_limit_count == 0:
            return 0

        explosion_rate = near_limit_count / (limit_up_count + near_limit_count)

        # 根据炸板率评分（炸板率越高，得分越低）
        if explosion_rate < 0.1:
            return 5  # 炸板率低
        elif explosion_rate < 0.2:
            return 3  # 炸板率一般
        else:
            return 1  # 炸板率高

    except Exception as e:
        print(f"计算炸板率失败: {e}")
        return 0


def calculate_capital_activity_score(data):
    """
    计算资金活跃度得分（20分）

    包括：
    - 市场成交额（10分）
    - 换手率（10分）
    """
    score = 0

    # 市场成交额（10分）
    amount = data.get('total_amount', 0)
    if amount > 1.5:
        score += 10
    elif amount > 1:
        score += 8
    elif amount > 0.8:
        score += 5
    elif amount > 0.5:
        score += 3
    else:
        score += 0

    # 换手率（10分）
    turnover = data.get('avg_turnover', 0)
    if turnover > 2:
        score += 10
    elif turnover > 1.5:
        score += 8
    elif turnover > 1:
        score += 5
    elif turnover > 0.8:
        score += 3
    else:
        score += 0

    return score


def calculate_trend_score(data):
    """
    计算趋势指标得分（20分）

    包括：
    - 指数表现（10分）
    - 近3日趋势（10分）
    """
    score = 0

    # 指数表现（10分）
    index_chg = data.get('index_pct_chg', 0)
    if index_chg > 2:
        score += 10
    elif index_chg > 1:
        score += 8
    elif index_chg > 0:
        score += 5
    elif index_chg > -1:
        score += 3
    else:
        score += 0

    # 近3日趋势（10分）
    total_chg_3 = data.get('total_chg_3', 0)
    if total_chg_3 > 5:
        score += 10
    elif total_chg_3 > 2:
        score += 8
    elif total_chg_3 > 0:
        score += 5
    elif total_chg_3 > -2:
        score += 3
    else:
        score += 0

    return score


def get_market_emotion():
    """
    获取当前市场情绪周期

    基于多维度数据综合判断：
    - 涨停热度（30分）
    - 亏钱效应（30分）
    - 资金活跃度（20分）
    - 趋势指标（20分）

    第二阶段功能：
    - 情绪突变检测
    - 节假日效应处理
    """
    try:
        # 获取市场情绪数据
        emotion_data = get_market_emotion_data()

        if not emotion_data:
            print("无法获取市场情绪数据，无法判断情绪周期")
            return 'unknown', None

        # 维度1：涨停热度（30分） - 包含连板高度和板块效应
        limit_up_stocks = emotion_data.get('limit_up_stocks', pd.DataFrame())
        limit_up_score = calculate_limit_up_score(emotion_data, limit_up_stocks)

        # 维度2：亏钱效应（30分） - 包含炸板率
        loss_effect_score = calculate_loss_effect_score(emotion_data)

        # 维度3：资金活跃度（20分） - 应用节假日效应
        capital_activity_score = calculate_capital_activity_score(emotion_data)
        holiday_effect = emotion_data.get('holiday_effect', 1.0)
        capital_activity_score = int(capital_activity_score * holiday_effect)

        # 维度4：趋势指标（20分）
        trend_score = calculate_trend_score(emotion_data)

        # 计算总分
        total_score = (limit_up_score + loss_effect_score +
                      capital_activity_score + trend_score)

        # 第二阶段功能：情绪突变检测
        emotion_changed, prev_emotion = detect_emotion_mutation(emotion_data)

        if emotion_changed:
            print(f"⚠️ 情绪突变检测：情绪从 '{prev_emotion}' 发生变化")
            # 情绪突变时，适当调整评分
            total_score = adjust_score_for_mutation(total_score, prev_emotion)

        # 特殊情况：跌停板远多于涨停板
        limit_up = emotion_data.get('limit_up_count', 0)
        limit_down = emotion_data.get('limit_down_count', 0)

        if limit_down > limit_up * 2:
            print(f"特殊情况：跌停板({limit_down})远多于涨停板({limit_up})，判断为绝望期")
            return 'despair', 0

        # 特殊情况：涨停板极少
        if limit_up < 10:
            print(f"特殊情况：涨停板极少({limit_up})，判断为冰点期")
            return 'freeze', 100

        # 根据总分判断情绪周期
        if total_score >= 85:
            emotion = 'climax'
            emotion_score = 40
        elif total_score >= 75:
            emotion = 'ferment'
            emotion_score = 60
        elif total_score >= 60:
            emotion = 'start'
            emotion_score = 80
        elif total_score >= 40:
            emotion = 'freeze'
            emotion_score = 100
        elif total_score >= 20:
            emotion = 'recede'
            emotion_score = 20
        else:
            emotion = 'despair'
            emotion_score = 0

        print(f"市场情绪判断：")
        print(f"  涨停热度: {limit_up_score}/30")
        print(f"  亏钱效应: {loss_effect_score}/30")
        print(f"  资金活跃度: {capital_activity_score}/20 (节假日系数: {holiday_effect})")
        print(f"  趋势指标: {trend_score}/20")
        print(f"  总分: {total_score}/100")
        print(f"  情绪周期: {emotion}, 评分: {emotion_score}")
        if emotion_changed:
            print(f"  ⚠️ 情绪突变: {prev_emotion} -> {emotion}")

        return emotion, emotion_score

    except Exception as e:
        print(f"获取市场情绪失败: {e}")
        return 'unknown', None  # 无法判断


def detect_emotion_mutation(emotion_data):
    """
    检测情绪突变（第二阶段功能）

    通过对比昨日和今日的市场数据，判断情绪是否发生突变

    Returns:
        tuple: (是否突变, 昨日情绪)
    """
    try:
        today = datetime.now().strftime('%Y%m%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

        # 获取昨日市场数据
        yesterday_index = pro.index_daily(
            ts_code='000001.SH',
            start_date=yesterday,
            end_date=yesterday
        )

        if len(yesterday_index) == 0:
            return False, None

        yesterday_data = pro.daily(
            trade_date=yesterday,
            fields='ts_code,pct_chg'
        )

        if len(yesterday_data) == 0:
            return False, None

        # 计算昨日数据
        ytd_limit_up = len(yesterday_data[yesterday_data['pct_chg'] >= 9.5])
        ytd_limit_down = len(yesterday_data[yesterday_data['pct_chg'] <= -9.5])
        ytd_index_chg = yesterday_index.iloc[-1]['pct_chg']

        # 判断昨日情绪
        ytd_total_score = 0
        # 简化判断：只根据涨停跌停比例
        if ytd_limit_up > ytd_limit_down * 2:
            ytd_emotion = 'climax'  # 高潮
        elif ytd_limit_down > ytd_limit_up * 2:
            ytd_emotion = 'despair'  # 绝望
        elif ytd_index_chg > 1:
            ytd_emotion = 'start'  # 启动
        elif ytd_index_chg < -1:
            ytd_emotion = 'recede'  # 退潮
        else:
            ytd_emotion = 'ferment'  # 发酵

        # 对比今日和昨日
        today_index_chg = emotion_data.get('index_pct_chg', 0)
        today_limit_up = emotion_data.get('limit_up_count', 0)
        today_limit_down = emotion_data.get('limit_down_count', 0)

        # 判断是否突变
        # 突变定义：情绪评分变化超过20分
        emotion_score_map = {
            'despair': 0,
            'recede': 20,
            'freeze': 100,
            'start': 80,
            'ferment': 60,
            'climax': 40
        }

        ytd_score = emotion_score_map.get(ytd_emotion, 50)

        # 快速判断今日情绪
        if today_limit_up > today_limit_down * 2:
            today_emotion = 'climax'
        elif today_limit_down > today_limit_up * 2:
            today_emotion = 'despair'
        elif today_index_chg > 1:
            today_emotion = 'start'
        elif today_index_chg < -1:
            today_emotion = 'recede'
        else:
            today_emotion = 'ferment'

        today_score = emotion_score_map.get(today_emotion, 50)

        # 判断是否突变
        if abs(today_score - ytd_score) >= 20:
            return True, ytd_emotion
        else:
            return False, ytd_emotion

    except Exception as e:
        print(f"检测情绪突变失败: {e}")
        return False, None


def adjust_score_for_mutation(total_score, prev_emotion):
    """
    根据情绪突变调整评分（第二阶段功能）

    如果情绪从高潮突然转向退潮/绝望，降低评分
    如果情绪从绝望突然转向启动/冰点，提高评分

    Returns:
        int: 调整后的总分
    """
    emotion_weight = {
        'climax': 0.8,    # 高潮时，如果转向，降低权重
        'ferment': 0.9,   # 发酵时，正常权重
        'start': 1.0,      # 启动时，正常权重
        'freeze': 1.0,      # 冰点时，正常权重
        'recede': 0.9,     # 退潮时，正常权重
        'despair': 1.2      # 绝望时，如果转向，提高权重
    }

    weight = emotion_weight.get(prev_emotion, 1.0)
    return int(total_score * weight)


@app.route('/api/stats', methods=['GET'])
def get_query_stats():
    """获取查询统计数据API"""
    # 获取热门股票（查询次数最多的8个）
    sorted_stocks = sorted(
        QUERY_STATS['stock_queries'].values(),
        key=lambda x: x['count'],
        reverse=True
    )
    top_stocks = sorted_stocks[:8]

    return jsonify({
        'total_count': QUERY_STATS['total_count'],
        'top_stocks': top_stocks
    })

@app.route('/api/top3-today', methods=['GET'])
def get_top3_today():
    """获取今日精选股票API"""
    try:
        csv_path = TOP3_TODAY_FILE

        if not os.path.exists(csv_path):
            return jsonify({
                'error': '今日精选数据文件不存在，请先运行选股脚本'
            }), 404

        # 读取CSV文件
        df = pd.read_csv(csv_path)

        if len(df) == 0:
            return jsonify({
                'error': '今日精选数据为空'
            }), 404

        # 只取前8名
        df_top3 = df.head(8)

        # 转换为JSON格式
        top3_list = []
        for idx, row in df_top3.iterrows():
            top3_list.append({
                'rank': idx + 1,
                'code': row['ts_code'],
                'name': row['name'],
                'industry': row['industry'],
                'price': float(row['price']),
                'pct_chg': float(row['pct_chg']),
                'trade_date': str(row['trade_date']),
                'total_mv': float(row['total_mv']),
                'overall_score': float(row['overall_score']),
                'win_rate': float(row['win_rate']),
                'position_advice': row['position_advice'],
                'buy_point_type': row['buy_point_type'],
                'buy_point_score': int(row['buy_point_score']),
                'ma250': float(row['ma250']),
                'price_above_ma250': bool(row['price_above_ma250']),
                'long_term_score': float(row['long_term_score']),
                'mid_term_score': float(row['mid_term_score']),
                'short_term_score': float(row['short_term_score']),
                'growth_coeff': float(row['growth_coeff']),
                'limit_up_count': int(row['limit_up_count'])
            })

        return jsonify({
            'status': 'ok',
            'count': len(top3_list),
            'stocks': top3_list,
            'update_time': os.path.getmtime(csv_path)
        })

    except Exception as e:
        print(f"读取Top3数据失败: {e}")
        return jsonify({
            'error': f'读取Top3数据失败: {str(e)}'
        }), 500


@app.route('/api/recognize', methods=['GET'])
def recognize_stock():
    """股票识别API - 将股票名称或模糊代码转换为标准股票代码"""
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({'error': '请提供查询内容'}), 400

    try:
        # === 步骤1：规范化输入（6位数字自动补全后缀）===
        if query.isdigit() and len(query) == 6:
            # 根据股票代码首位判断市场
            first_digit = query[0]
            if first_digit in ['6', '9']:
                query_full = f'{query}.SH'  # 沪市/科创板
            else:
                query_full = f'{query}.SZ'  # 深市/创业板
            
            # 精确匹配
            stock_info = pro.stock_basic(ts_code=query_full,
                                          fields='ts_code,symbol,name,area,industry,list_date')
            
            if len(stock_info) > 0:
                stock_info = stock_info.iloc[0]
                return jsonify({
                    'query': query_full,
                    'code': stock_info['ts_code'],
                    'symbol': stock_info['symbol'],
                    'name': stock_info['name'],
                    'industry': stock_info['industry'],
                    'list_date': stock_info['list_date'],
                    'multiple': False
                })

        # === 步骤2：获取所有股票数据（用于模糊搜索）===
        try:
            all_stocks = pro.stock_basic(fields='ts_code,symbol,name,area,industry,list_date')
        except Exception as e:
            # 如果获取失败，返回错误
            return jsonify({'error': f'获取股票数据失败：{str(e)}'}), 500

        # === 步骤3：精确匹配 ===
        # 尝试精确匹配股票代码
        exact_code_match = all_stocks[all_stocks['ts_code'] == query]
        if len(exact_code_match) > 0:
            stock_info = exact_code_match.iloc[0]
            return jsonify({
                'query': query,
                'code': stock_info['ts_code'],
                'symbol': stock_info['symbol'],
                'name': stock_info['name'],
                'industry': stock_info['industry'],
                'list_date': stock_info['list_date'],
                'multiple': False
            })

        # 尝试精确匹配symbol
        exact_symbol_match = all_stocks[all_stocks['symbol'] == query]
        if len(exact_symbol_match) > 0:
            stock_info = exact_symbol_match.iloc[0]
            return jsonify({
                'query': query,
                'code': stock_info['ts_code'],
                'symbol': stock_info['symbol'],
                'name': stock_info['name'],
                'industry': stock_info['industry'],
                'list_date': stock_info['list_date'],
                'multiple': False
            })

        # === 步骤4：模糊匹配 ===
        matched = None

        # 4.1 模糊匹配股票名称（包含查询字符串）
        try:
            name_match = all_stocks[all_stocks['name'].str.contains(query, case=False, na=False)]
            if len(name_match) > 0:
                matched = name_match
        except Exception as e:
            print(f"名称匹配失败: {e}")

        # 4.2 如果名称匹配失败，尝试模糊匹配代码
        if matched is None or len(matched) == 0:
            try:
                # 包含ts_code
                code_match = all_stocks[all_stocks['ts_code'].str.contains(query, case=False, na=False)]
                if len(code_match) > 0:
                    matched = code_match
                else:
                    # 包含symbol
                    symbol_match = all_stocks[all_stocks['symbol'].str.contains(query, case=False, na=False)]
                    if len(symbol_match) > 0:
                        matched = symbol_match
            except Exception as e:
                print(f"代码匹配失败: {e}")

        # === 步骤5：处理匹配结果 ===
        if matched is None or len(matched) == 0:
            return jsonify({'error': f'未找到匹配的股票：{query}'}), 404

        # 限制返回数量，最多10个
        if len(matched) > 10:
            matched = matched.head(10)

        # 整理结果
        results = []
        for idx, row in matched.iterrows():
            results.append({
                'code': row['ts_code'],
                'symbol': row['symbol'],
                'name': row['name'],
                'industry': row['industry'],
                'list_date': row['list_date']
            })

        return jsonify({
            'query': query,
            'count': len(results),
            'results': results,
            'multiple': len(results) > 1
        })

    except Exception as e:
        print(f"识别错误: {str(e)}")
        return jsonify({'error': f'查询失败：{str(e)}'}), 500
@app.route('/api/analyze', methods=['GET'])
def analyze_stock():
    """股票分析API"""
    stock_code = request.args.get('code')

    if not stock_code:
        return jsonify({'error': '请提供股票代码'}), 400

    try:
        # 获取股票基本信息
        stock_info = pro.stock_basic(ts_code=stock_code,
                                      fields='ts_code,symbol,name,area,industry,list_date')
        if len(stock_info) == 0:
            return jsonify({'error': f'未找到股票 {stock_code}'}), 404

        stock_info = stock_info.iloc[0]

        # 更新查询统计
        QUERY_STATS['total_count'] += 1
        stock_code_key = stock_info['ts_code']
        if stock_code_key in QUERY_STATS['stock_queries']:
            QUERY_STATS['stock_queries'][stock_code_key]['count'] += 1
        else:
            QUERY_STATS['stock_queries'][stock_code_key] = {
                'code': stock_code_key,
                'symbol': stock_info['symbol'],
                'name': stock_info['name'],
                'count': 1
            }

        # 保存统计数据到文件
        save_query_stats()

        # 基础筛选
        is_st = 'ST' in stock_info['name'] or '*ST' in stock_info['name']

        # 行业成长系数
        # 获取概念板块信息
        concepts = []
        try:
            concept_df = pro.concept_detail(ts_code=stock_code)
            if len(concept_df) > 0:
                concepts = concept_df['concept_name'].tolist()
        except Exception as e:
            print(f"  ⚠ 获取概念板块失败: {e}")

        # 行业成长系数
        growth_coeff = get_industry_growth_coefficient(stock_info['industry'], concepts)
        growth_score = growth_coeff * 100

        # 获取最新财务指标
        end_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        start_date = '20240101'

        financial = pro.fina_indicator(ts_code=stock_code,
                                      start_date=start_date,
                                      end_date=end_date)

        financial_score, financial_data = calculate_financial_score_v2(financial, stock_info['industry'])

        # 获取技术数据
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=400)).strftime('%Y%m%d')  # 获取至少400天数据，确保有250天均线

        # 获取K线数据
        df = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)

        if len(df) == 0:
            return jsonify({'error': f'无法获取股票 {stock_code} 的K线数据'}), 404

        # tushare返回的数据是按日期倒序的（最新的在最前面），需要排序为正序（最早的在最前面）
        df = df.sort_values('trade_date').reset_index(drop=True)

        # 确保数据足够计算250日均线
        if len(df) < 250:
            print(f"⚠️ 警告：股票 {stock_code} 只有 {len(df)} 天数据，无法计算250日均线")

        # 获取市值数据
        basic_df = pro.daily_basic(ts_code=stock_code, trade_date=end_date,
                                   fields='ts_code,total_mv,circ_mv,total_share,float_share')

        total_mv = 0
        circ_mv = 0
        if len(basic_df) > 0:
            total_mv = basic_df.iloc[0]['total_mv'] / 10000  # 万元转亿元
            circ_mv = basic_df.iloc[0]['circ_mv'] / 10000
        else:
            basic_df = pro.daily_basic(ts_code=stock_code,
                                       fields='ts_code,total_share,float_share')
            if len(basic_df) > 0:
                total_share = basic_df.iloc[0]['total_share']
                total_mv = 0  # 需要股价计算
                circ_mv = 0  # 需要股价计算

        # 技术面数据
        tech_data = {}
        ma250_score = 0
        chanlun_score = 0
        chanlun_type = 0
        chanlun_desc = ""
        limit_up_count = 0
        limit_up_score = 0
        close_price = 0

        # 使用技术分析工具计算
        tech_result = calculate_technical_score(df)

        ma250_score = tech_result['ma250_score']
        ma250 = tech_result['ma250']
        chanlun_result = tech_result['chanlun']
        chanlun_score = chanlun_result['score']
        chanlun_type = chanlun_result['type']
        chanlun_desc = chanlun_result['desc']

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

        # 获取最新数据
        latest = df.iloc[-1]
        close_price = latest['close']

        tech_data = {
            'close': round(close_price, 2),
            'pre_close': round(latest['pre_close'], 2),
            'pct_chg': round(latest['pct_chg'], 2),
            'vol': round(latest['vol'], 2),
            'amount': round(latest['amount'], 2),
            'trade_date': latest['trade_date'],
            'ma250_score': ma250_score,
            'ma250': round(ma250, 2) if ma250 else None,
            'chanlun_score': chanlun_score,
            'chanlun_type': chanlun_type,
            'chanlun_desc': chanlun_desc,
            'limit_up_count': limit_up_count,
            'limit_up_score': limit_up_score
        }

        # 添加历史数据（近60天）
        history_df = df.tail(60).copy()
        history_data = []

        # 计算250日均线历史数据
        for i, (_, row) in enumerate(history_df.iterrows()):
            # 计算当前日期的250日均线
            if i >= 250:
                ma250_history = history_df.iloc[i-250:i]['close'].mean()
            elif len(df) >= 250:
                # 如果数据不够，使用完整df计算
                current_idx = len(df) - 60 + i
                if current_idx >= 250:
                    ma250_history = df.iloc[current_idx-250:current_idx]['close'].mean()
                else:
                    ma250_history = None
            else:
                ma250_history = None

            history_data.append({
                'date': row['trade_date'],
                'close': round(row['close'], 2),
                'high': round(row['high'], 2),
                'low': round(row['low'], 2),
                'open': round(row['open'], 2),
                'vol': round(row['vol'], 2),
                'amount': round(row['amount'], 2),
                'pct_chg': round(row['pct_chg'], 2),
                'ma250': round(ma250_history, 2) if ma250_history else None
            })

        # 如果市值数据为0，使用股价*总股本计算
        if total_mv == 0 and close_price > 0 and len(basic_df) > 0:
            try:
                total_share = basic_df.iloc[0]['total_share']
                # 股价（元）* 总股本（万股）= 市值（万元）
                # 转换为亿元：市值（万元）/ 10000 = 市值（亿元）
                total_mv = (close_price * total_share) / 10000

                # 尝试计算流通市值
                if 'float_share' in basic_df.columns and pd.notna(basic_df.iloc[0]['float_share']):
                    float_share = basic_df.iloc[0]['float_share']
                    circ_mv = (close_price * float_share) / 10000
                else:
                    circ_mv = total_mv  # 没有流通股本数据，使用总市值
            except Exception as e:
                print(f"计算市值失败: {e}")
                total_mv = 0
                circ_mv = 0

        # 市值扣分
        market_cap_penalty = get_market_cap_penalty(total_mv)

        # 技术面综合得分（使用技术分析工具计算的结果）
        tech_score = tech_result['tech_score']

        # 催化逻辑评分
        if limit_up_count >= 3:
            catalyst_score = 100
            catalyst_reason = "国家级战略/技术革命（连续涨停验证）"
        elif growth_coeff >= 0.7:
            catalyst_score = 80
            catalyst_reason = "行业周期反转/高成长赛道"
        else:
            catalyst_score = 30
            catalyst_reason = "纯情绪炒作"

        # 题材热度指数
        theme_heat_index = (limit_up_score * 0.3) + (catalyst_score * 0.3) + (growth_score * 0.4)

        # 龙头属性评分
        dragon_score, dragon_type, dragon_desc = identify_dragon(stock_code, stock_info['industry'])

        # 获取真实的市场情绪周期
        current_emotion, emotion_score = get_market_emotion()

        # 综合评分
        long_term_score = growth_score  # V8.0: 长期只看行业成长系数
        medium_term_score = (theme_heat_index * 0.5) + (financial_score * 0.3) + (tech_score * 0.2)

        # 如果情绪周期无法判断，使用中性情绪评分（50分）
        if current_emotion == 'unknown' or emotion_score is None:
            emotion_score = 50  # 中性情绪，50分
            if current_emotion == 'unknown':
                print("⚠️ 市场情绪周期无法判断，使用中性情绪评分（50分）")
                current_emotion = 'neutral'  # 设置为中性情绪

        # 计算短期评分（V9.0：技术面80% + 情绪周期20% - 市值扣分）
        if emotion_score is not None:
            short_term_score = (tech_score * 0.8) + (emotion_score * 0.2) - market_cap_penalty
        else:
            short_term_score = (tech_score * 0.8) - market_cap_penalty

        # 确保评分在合理范围内
        short_term_score = max(0, min(100, short_term_score))

        # V9.5: 综合得分优化（直接综合得分，市值扣分已在短期评分中体现）
        # 核心原则：短线决定买点，中线决定趋势，长线决定赛道
        # 权重分配：短期60% + 中期30% + 长期10%
        overall_score = (short_term_score * 0.6) + (medium_term_score * 0.3) + (long_term_score * 0.1)

        # V9.5: 赢面评估优化（基于综合得分和市值）
        # 赢面 = (综合得分 / 100) × 市值系数 × 情绪周期系数

        # 1. 市值系数（市值越大，赢面越低）
        if total_mv < 50:
            mv_coeff = 1.0      # <50亿：超小盘，灵活
        elif total_mv < 100:
            mv_coeff = 0.98    # 50-100亿：小盘，相对灵活
        elif total_mv < 200:
            mv_coeff = 0.95    # 100-200亿：中小盘
        elif total_mv < 300:
            mv_coeff = 0.92    # 200-300亿：中盘
        elif total_mv < 500:
            mv_coeff = 0.88    # 300-500亿：中大盘
        elif total_mv < 1000:
            mv_coeff = 0.82    # 500-1000亿：大盘
        elif total_mv < 3000:
            mv_coeff = 0.75    # 1000-3000亿：超大盘
        elif total_mv < 5000:
            mv_coeff = 0.68    # 3000-5000亿：巨型市值
        else:
            mv_coeff = 0.60    # >5000亿：巨无霸

        # 2. 情绪周期系数
        emotion_coeff = {
            'despair': 0.5,    # 绝望：极高风险
            'recede': 0.7,     # 退潮：高风险
            'climax': 0.6,     # 高潮：中等风险
            'ferment': 0.8,    # 发酵：中低风险
            'start': 1.0,      # 启动：低风险（黄金期）
            'freeze': 0.9,     # 冰点：低风险（拐点期）
            'neutral': 0.75,   # 中性情绪
            'unknown': 0.75    # 未知时使用中性系数
        }

        # 3. 如果情绪周期无法判断，调整短期评分
        if current_emotion == 'unknown':
            short_term_score = tech_score * 0.8  # 仅使用技术面评分
            print("⚠️ 市场情绪周期无法判断，短期评分仅基于技术面")

        # 4. 计算赢面（综合得分 × 市值系数 × 情绪周期系数）
        win_rate = (overall_score / 100) * mv_coeff * emotion_coeff[current_emotion]
        win_rate = max(0, min(1, win_rate))  # 确保在0-1之间

        # 5. 赢面得分（0-100分，用于展示）
        win_score = int(win_rate * 100)

        # V9.5: 仓位建议优化（基于赢面和市值）
        # 综合考虑赢面和市值，给出更科学的仓位建议

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
            position_advice = "空仓"
        elif final_position <= 0.05:
            position_advice = "极小仓试错（≤5%）"
        elif final_position <= 0.2:
            position_advice = f"小仓（约{int(final_position*100)}%）"
        elif final_position <= 0.5:
            position_advice = f"中仓（约{int(final_position*100)}%）"
        elif final_position <= 0.8:
            position_advice = f"中高仓（约{int(final_position*100)}%）"
        else:
            position_advice = "重仓（约80%-100%）"

        # 综合评级（基于综合得分）
        # 优秀：综合得分 >= 75（三周期共振或短线突出）
        # 良好：综合得分 >= 60（单周期突出）
        # 一般：综合得分 < 60（不符合标准）
        if overall_score >= 75:
            overall_rating = "优秀"
        elif overall_score >= 60:
            overall_rating = "良好"
        else:
            overall_rating = "一般"

        return jsonify({
            'code': stock_code,
            'name': stock_info['name'],
            'industry': stock_info['industry'],
            'is_st': is_st,
            'list_date': stock_info['list_date'],
            'basic': {
                'industry': stock_info['industry'],
                'is_st': is_st,
                'list_date': stock_info['list_date']
            },
            'industry_growth': {
                'coefficient': growth_coeff,
                'score': growth_score
            },
            'financial': {
                'score': financial_score,
                'data': financial_data
            },
            'technical': {
                'score': round(tech_score, 1),
                'ma250_score': ma250_score,
                'chanlun_score': chanlun_score,
                'chanlun_type': chanlun_type,
                'chanlun_desc': chanlun_desc,
                'limit_up_count': limit_up_count,
                'limit_up_score': limit_up_score,
                'data': tech_data,
                'history': history_data  # 添加历史数据
            },
            'market_cap': {
                'total_mv': round(total_mv, 2),
                'circ_mv': round(circ_mv, 2),
                'penalty': market_cap_penalty
            },
            'theme_heat': {
                'index': round(theme_heat_index, 1),
                'limit_up_score': limit_up_score,  # 近期涨停热度分
                'catalyst_score': catalyst_score,  # 催化逻辑分
                'catalyst_reason': catalyst_reason,
                'growth_score': growth_score  # 行业成长得分
            },
            'dragon': {
                'score': dragon_score,
                'type': dragon_type,
                'desc': dragon_desc
            },
            'emotion': {
                'score': emotion_score,
                'current': current_emotion
            },
            'scores': {
                'long_term': long_term_score,
                'medium_term': round(medium_term_score, 1),
                'short_term': round(short_term_score, 1),
                'overall': round(overall_score, 1)  # V9.0: 综合得分（短线权重60% + 中期30% + 长期10%）
            },
            'win_rate': round(win_rate * 100, 1),
            'mv_coeff': round(mv_coeff, 3),  # V9.5: 市值系数
            'emotion_coeff': round(emotion_coeff.get(current_emotion, 0.75), 3),  # V9.5: 情绪系数
            'position_advice': position_advice,
            'overall_rating': overall_rating
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# 第三阶段：高级功能（框架实现）
# ========================================

def analyze_dragon_stocks():
    """
    龙头股监测（第三阶段功能）

    监测当前市场的龙头股：
    - 板块龙头
    - 市场龙头
    - 连板龙头

    Returns:
        list: 龙头股列表
    """
    try:
        # TODO: 实现龙头股监测逻辑
        # 1. 获取所有涨停股票
        # 2. 按板块统计涨停数量
        # 3. 识别每个板块的龙头（涨停最早、成交额最大）
        # 4. 识别市场龙头（多个板块涨停、连板高度最高）

        return []

    except Exception as e:
        print(f"龙头股监测失败: {e}")
        return []


def analyze_sector_rotation():
    """
    板块轮动分析（第三阶段功能）

    分析板块的轮动情况：
    - 领涨板块
    - 跟涨板块
    - 滞后板块
    - 板块切换趋势

    Returns:
        dict: 板块轮动分析结果
    """
    try:
        # TODO: 实现板块轮动分析逻辑
        # 1. 获取近10天板块涨幅排名
        # 2. 识别领涨板块（持续涨幅领先）
        # 3. 识别板块切换信号（领涨板块变化）
        # 4. 预测下一个轮动板块

        return {}

    except Exception as e:
        print(f"板块轮动分析失败: {e}")
        return {}


def analyze_capital_flow():
    """
    主力资金流向（第三阶段功能）

    分析主力资金的流向：
    - 净流入板块
    - 净流出板块
    - 资金切换趋势
    - 机构 vs 散户资金流向

    Returns:
        dict: 资金流向分析结果
    """
    try:
        # TODO: 实现主力资金流向分析逻辑
        # 注意：Tushare可能需要高级接口获取资金流向数据
        # 1. 获取板块资金流向
        # 2. 获取个股主力资金流向
        # 3. 识别资金切换趋势
        # 4. 分析机构 vs 散户资金行为

        return {}

    except Exception as e:
        print(f"主力资金流向分析失败: {e}")
        return {}


def predict_emotion_cycle():
    """
    情绪周期预测（第三阶段功能）

    基于历史数据和当前指标，预测未来情绪周期：
    - 短期预测（1-3天）
    - 中期预测（1-2周）
    - 情绪转换信号

    Returns:
        dict: 情绪周期预测结果
    """
    try:
        # TODO: 实现情绪周期预测逻辑
        # 1. 获取历史情绪周期数据
        # 2. 识别情绪转换规律
        # 3. 基于当前指标预测短期趋势
        # 4. 输出预测置信度

        return {}

    except Exception as e:
        print(f"情绪周期预测失败: {e}")
        return {}


def compare_historical_emotion():
    """
    历史情绪对比（第三阶段功能）

    将当前情绪与历史同期进行对比：
    - 与去年同期对比
    - 与历史平均对比
    - 与关键事件时期对比

    Returns:
        dict: 历史对比结果
    """
    try:
        # TODO: 实现历史情绪对比逻辑
        # 1. 获取历史同期情绪数据
        # 2. 计算当前情绪偏离度
        # 3. 识别相似历史时期
        # 4. 推断可能的后续走势

        return {}

    except Exception as e:
        print(f"历史情绪对比失败: {e}")
        return {}


@app.route('/api/advanced-emotion', methods=['GET'])
def advanced_emotion_analysis():
    """
    高级情绪分析API（第三阶段功能）

    提供高级情绪分析功能：
    - 龙头股监测
    - 板块轮动分析
    - 主力资金流向
    - 情绪周期预测
    - 历史情绪对比

    Returns:
        dict: 高级情绪分析结果
    """
    try:
        # 调用第三阶段的所有功能
        dragon_stocks = analyze_dragon_stocks()
        sector_rotation = analyze_sector_rotation()
        capital_flow = analyze_capital_flow()
        emotion_prediction = predict_emotion_cycle()
        historical_comparison = compare_historical_emotion()

        return jsonify({
            'dragon_stocks': dragon_stocks,
            'sector_rotation': sector_rotation,
            'capital_flow': capital_flow,
            'emotion_prediction': emotion_prediction,
            'historical_comparison': historical_comparison,
            'status': 'ok',
            'message': '高级情绪分析功能已启用（部分功能待完善）'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def format_analysis_report(data):
    """
    将分析数据格式化为报告样式

    Args:
        data: analyze_stock返回的完整数据

    Returns:
        str: 格式化的报告文本
    """
    # 提取关键数据
    name = data['name']
    code = data['code']
    industry = data['industry']
    total_mv = data['market_cap']['total_mv']

    long_term_score = data['scores']['long_term']
    medium_term_score = data['scores']['medium_term']
    short_term_score = data['scores']['short_term']
    overall_score = data['scores']['overall']

    win_rate = data['win_rate']
    position_advice = data['position_advice']
    overall_rating = data['overall_rating']

    # 技术面数据
    ma250_score = data['technical']['ma250_score']
    chanlun_score = data['technical']['chanlun_score']
    chanlun_type = data['technical']['chanlun_type']
    chanlun_desc = data['technical']['chanlun_desc']
    price_above_ma250 = chanlun_score > 0 and ma250_score > 60

    # 涨停数据
    limit_up_count = data['technical']['limit_up_count']

    # 财务数据
    financial_score = data['financial']['score']
    financial_data = data['financial']['data']

    # 行业成长系数
    growth_coeff = data['industry_growth']['coefficient']

    # 情绪周期
    current_emotion = data['emotion']['current']
    emotion_score = data['emotion']['score']

    # 生成报告
    report_lines = []

    # 标题
    report_lines.append(f"## {name}（{code}）分析报告")
    report_lines.append(f"**行业**：{industry} | **总市值**：{total_mv:.0f}亿元")
    report_lines.append(f"**综合得分**：{overall_score:.1f}分（{overall_rating}）| **赢面**：{win_rate:.1f}%")
    report_lines.append("")

    # === 长期投资（3年以上）===
    report_lines.append("### ✅ 长期投资（3年以上）")

    # 长期建议和理由
    if long_term_score >= 80:
        report_lines.append("**建议**：积极关注")
        report_lines.append("**理由**：")
        if growth_coeff >= 1.0:
            report_lines.append(f"赛道天花板高：{industry}是国家级战略或高成长行业")
        if financial_score >= 70:
            report_lines.append(f"财务质量强：ROE、营收、利润增长优秀")
        if growth_coeff >= 0.7:
            report_lines.append("行业前景好：中高成长赛道，长期空间大")
    elif long_term_score >= 60:
        report_lines.append("**建议**：适度关注")
        report_lines.append("**理由**：")
        report_lines.append(f"行业中等成长：{industry}有一定成长空间")
        if financial_score >= 60:
            report_lines.append("财务质量尚可：基本面支撑较强")
    else:
        report_lines.append("**建议**：谨慎观望")
        report_lines.append("**理由**：")
        report_lines.append(f"赛道天花板低：{industry}属于低成长或无成长行业")
        if financial_score < 50:
            report_lines.append("财务质量一般：ROE、营收、利润增长乏力")

    report_lines.append("")

    # === 中期投资（6-12个月）===
    report_lines.append("### ⚠️ 中期投资（6-12个月）")

    # 中期建议和理由
    if medium_term_score >= 70:
        report_lines.append("**建议**：积极关注")
        report_lines.append("**理由**：")
        if limit_up_count >= 2:
            report_lines.append(f"资金流入：近10日有{limit_up_count}次涨停，资金关注度强")
        if limit_up_count >= 1:
            report_lines.append(f"有涨停信号：近10日有涨停，资金开始关注")
        if financial_score >= 70:
            report_lines.append("财务质量优秀：基本面支撑强")
        if tech_score := data['technical']['score'] >= 60:
            report_lines.append("技术面企稳：股价站上250日均线或接近")
    elif medium_term_score >= 60:
        report_lines.append("**建议**：适度关注")
        report_lines.append("**理由**：")
        if financial_score >= 60:
            report_lines.append("财务质量尚可：基本面有一定支撑")
        if growth_coeff >= 0.7:
            report_lines.append("行业中等成长：有一定成长空间")
    else:
        report_lines.append("**建议**：谨慎观望")
        report_lines.append("**理由**：")
        if limit_up_count == 0:
            report_lines.append("无资金流入：近10日无涨停，资金关注度低")
        if not price_above_ma250:
            report_lines.append("技术面空头：股价低于250日均线")
        if financial_score < 50:
            report_lines.append("财务质量一般：基本面支撑不足")

    report_lines.append("")

    # === 短期交易（1-3个月）===
    report_lines.append("### ❌ 短期交易（1-3个月）")

    # 短期建议和理由
    if short_term_score >= 70:
        report_lines.append("**建议**：积极关注")
        report_lines.append("**理由**：")
        if chanlun_type >= 1:
            report_lines.append(f"有买点信号：{chanlun_desc}")
        if price_above_ma250:
            report_lines.append("技术面多头：股价高于250日均线")
        if total_mv < 200:
            report_lines.append("市值适中：短期操作相对灵活")
    elif short_term_score >= 50:
        report_lines.append("**建议**：谨慎观望")
        report_lines.append("**理由**：")
        if chanlun_type == 0:
            report_lines.append("无买点信号：无缠论买点确认")
        if ma250_score < 60:
            report_lines.append("技术面中性：股价接近250日均线")
        if total_mv >= 500:
            report_lines.append(f"市值偏大：{total_mv:.0f}亿元，短期操作难度大")
    else:
        report_lines.append("**建议**：回避")
        report_lines.append("**理由**：")
        if ma250_score < 40:
            report_lines.append("技术面空头：股价远低于250日均线")
        if chanlun_type == 0:
            report_lines.append("无买点信号：无缠论买点确认")
        if limit_up_count == 0:
            report_lines.append("无资金关注：近10日无涨停")
        if total_mv >= 500:
            report_lines.append(f"市值过大：{total_mv:.0f}亿元，短期操作极难")

    report_lines.append("")

    # === 关键观察点 ===
    report_lines.append("### 📊 关键观察点")

    # 积极信号（等待确认）
    report_lines.append("#### 🟢 积极信号（等待确认）")
    positive_signals = []

    if not price_above_ma250:
        positive_signals.append("股价站上250日均线")

    if limit_up_count == 0:
        positive_signals.append("出现涨停（资金回流）")

    if chanlun_type == 0 and short_term_score < 50:
        positive_signals.append("底部形态确立")
        positive_signals.append("缠论一类买点确认")

    if positive_signals:
        for signal in positive_signals:
            report_lines.append(f"- {signal}")
    else:
        report_lines.append("- 暂无积极信号")

    # 负面信号（当前状态）
    report_lines.append("")
    report_lines.append("#### 🔴 负面信号（当前状态）")
    negative_signals = []

    if not price_above_ma250:
        if ma250_score < 40:
            negative_signals.append("深度空头趋势（股价远低于250日均线）")
        else:
            negative_signals.append("技术面空头（股价低于250日均线）")

    if limit_up_count == 0:
        negative_signals.append("无涨停资金流入")

    if total_mv >= 500:
        negative_signals.append(f"市值过大（{total_mv:.0f}亿元）")

    if chanlun_type == 0:
        negative_signals.append("无缠论买点确认")

    if negative_signals:
        for signal in negative_signals:
            report_lines.append(f"- {signal}")
    else:
        report_lines.append("- 暂无负面信号")

    report_lines.append("")

    # === 风险提示 ===
    report_lines.append("### ⚠️ 风险提示")

    risk_warnings = []

    if ma250_score < 40:
        risk_warnings.append("技术面深度空头，短期风险大")

    if total_mv >= 500:
        risk_warnings.append(f"市值过大（{total_mv:.0f}亿元），弹性有限")

    if short_term_score < 30:
        risk_warnings.append("无技术买点，短期操作风险极高")

    if limit_up_count == 0 and growth_coeff < 0.7:
        risk_warnings.append("无资金关注，行业成长性一般")

    if financial_score < 40:
        risk_warnings.append("财务质量较差，基本面支撑不足")

    # 行业特定风险
    if growth_coeff >= 0.7 and financial_score < 60:
        risk_warnings.append("行业高成长但财务质量一般，需关注业绩兑现")

    if risk_warnings:
        for warning in risk_warnings:
            report_lines.append(f"- {warning}")
    else:
        report_lines.append("- 当前风险可控")

    report_lines.append("")

    # === 核心结论 ===
    report_lines.append("### 🎯 核心结论")

    # 养家心法三周期视角
    report_lines.append("**养家心法三周期视角：**")
    report_lines.append("")

    # 长期
    long_stars = "⭐" * int(long_term_score / 20)
    report_lines.append(f"**长期（赛道）**：{long_stars} ({int(long_term_score)}分)")
    if growth_coeff >= 1.0:
        report_lines.append(f"- {industry}是国家级战略或高成长赛道")
    elif growth_coeff >= 0.7:
        report_lines.append(f"- {industry}是中等成长赛道")
    else:
        report_lines.append(f"- {industry}成长性一般")
    if financial_score >= 70:
        report_lines.append("- 财务质量优秀，长期价值凸显")
    elif financial_score >= 50:
        report_lines.append("- 财务质量尚可，有一定支撑")
    else:
        report_lines.append("- 财务质量一般，需关注业绩")
    report_lines.append("")

    # 中期
    mid_stars = "⭐" * int(medium_term_score / 20)
    report_lines.append(f"**中期（资金）**：{mid_stars} ({int(medium_term_score)}分)")
    if limit_up_count >= 2:
        report_lines.append(f"- 近10日有{limit_up_count}次涨停，资金关注度高")
    elif limit_up_count == 1:
        report_lines.append("- 近10日有1次涨停，资金开始关注")
    else:
        report_lines.append("- 近10日无涨停，无资金流入迹象")
    if price_above_ma250:
        report_lines.append("- 技术面多头，趋势向上")
    else:
        report_lines.append("- 技术面空头，趋势向下")
    report_lines.append("")

    # 短期
    short_stars = "⭐" * int(short_term_score / 20)
    report_lines.append(f"**短期（技术）**：{short_stars} ({int(short_term_score)}分)")
    if chanlun_type >= 1:
        report_lines.append(f"- {chanlun_desc}")
    else:
        report_lines.append("- 无缠论买点确认")
    if price_above_ma250:
        report_lines.append("- 股价高于250日均线")
    else:
        report_lines.append("- 股价低于250日均线")
    if total_mv >= 500:
        report_lines.append(f"- 市值过大（{total_mv:.0f}亿元），短期操作困难")
    else:
        report_lines.append("- 市值适中，短期操作相对灵活")
    report_lines.append("")

    # 一句话总结
    report_lines.append("**一句话总结：**")
    summary_parts = []

    # 长期描述
    if long_term_score >= 80:
        summary_parts.append(f"长期赛道优秀（{industry}）")
    elif long_term_score >= 60:
        summary_parts.append(f"长期赛道尚可（{industry}）")
    else:
        summary_parts.append(f"长期赛道一般（{industry}）")

    # 中期描述
    if medium_term_score >= 70:
        summary_parts.append("中期资金关注度高")
    elif medium_term_score >= 50:
        summary_parts.append("中期资金关注度一般")
    else:
        summary_parts.append("中期无资金关注")

    # 短期描述
    if short_term_score >= 70:
        summary_parts.append("短期有买点")
    elif short_term_score >= 50:
        summary_parts.append("短期观望")
    else:
        summary_parts.append("短期回避")

    # 综合建议
    if overall_score >= 75:
        summary_parts.append(f"综合评级优秀（{overall_score:.1f}分），建议积极关注")
    elif overall_score >= 60:
        summary_parts.append(f"综合评级良好（{overall_score:.1f}分），建议适度关注")
    else:
        summary_parts.append(f"综合评级一般（{overall_score:.1f}分），建议谨慎观望")

    report_lines.append("，".join(summary_parts) + "。")
    report_lines.append("")

    # 仓位建议
    report_lines.append(f"**仓位建议**：{position_advice}（赢面{win_rate:.1f}%）")

    return "\n".join(report_lines)


@app.route('/api/report', methods=['GET'])
def get_analysis_report():
    """
    获取格式化的分析报告

    Query参数:
        code: 股票代码（如：600000.SH）

    Returns:
        dict: 包含格式化报告和原始数据
    """
    stock_code = request.args.get('code')

    if not stock_code:
        return jsonify({'error': '请提供股票代码'}), 400

    try:
        # 调用analyze_stock获取完整数据
        stock_result = analyze_stock_internal(stock_code)

        if isinstance(stock_result, tuple) and stock_result[1] != 200:
            # 如果是错误响应
            return stock_result

        # 格式化报告
        formatted_report = format_analysis_report(stock_result[0])

        return jsonify({
            'code': stock_code,
            'name': stock_result[0]['name'],
            'report': formatted_report,
            'data': stock_result[0]  # 包含原始数据供前端使用
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/api/sentiment', methods=['GET'])
def analyze_sentiment():
    """舆情分析API"""
    stock_code = request.args.get('code')

    if not stock_code:
        return jsonify({'error': '请提供股票代码'}), 400

    try:
        # 获取股票基本信息
        stock_info = pro.stock_basic(ts_code=stock_code, fields='ts_code,name')
        if len(stock_info) == 0:
            return jsonify({'error': f'未找到股票 {stock_code}'}), 404

        stock_name = stock_info.iloc[0]['name']

        # 模拟舆情分析数据（实际应接入真实舆情API）
        sentiment_score = random.randint(60, 100)
        sentiment_trend = '积极' if sentiment_score >= 80 else '中性' if sentiment_score >= 60 else '消极'

        # 生成趋势数据（近7天）
        trend_data = []
        base_value = random.randint(40, 60)
        for i in range(7):
            value = base_value + random.randint(-10, 30)
            value = max(0, min(100, value))
            trend_data.append({
                'date': f'3月{9-i}日',
                'value': value
            })
        trend_data = trend_data[::-1]

        # 生成热门评论
        comments = generate_mock_comments(stock_name)

        return jsonify({
            'status': 'ok',
            'stock_code': stock_code,
            'stock_name': stock_name,
            'sentiment_score': sentiment_score,
            'sentiment_trend': sentiment_trend,
            'trend_data': trend_data,
            'comments': comments,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': f'舆情分析失败：{str(e)}'}), 500


def generate_mock_comments(stock_name):
    """生成模拟热门评论"""
    positive_comments = [
        {'content': f'{stock_name}表现不错，值得长期持有！', 'author': '投资者A', 'time': '2小时前', 'like': 128},
        {'content': '财报数据超出预期，未来可期', 'author': '股神B', 'time': '3小时前', 'like': 95},
        {'content': '技术面走势良好，支撑位稳固', 'author': '分析师C', 'time': '5小时前', 'like': 76},
        {'content': '公司基本面扎实，持续看好', 'author': '价值投资D', 'time': '6小时前', 'like': 64}
    ]

    neutral_comments = [
        {'content': '短期震荡，建议观望', 'author': '理性投资者F', 'time': '1小时前', 'like': 89},
        {'content': '走势平稳，等待进一步信号', 'author': '技术分析G', 'time': '4小时前', 'like': 72}
    ]

    negative_comments = [
        {'content': '今日调整，注意风险', 'author': '风险意识I', 'time': '30分钟前', 'like': 145},
        {'content': '短期承压，建议减仓', 'author': '保守派J', 'time': '2小时前', 'like': 98}
    ]

    # 随机选择评论组合
    all_comments = positive_comments + neutral_comments + negative_comments
    random.shuffle(all_comments)
    return all_comments[:8]

@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("="*60)
    print("养家心法选股服务启动中...")
    print("="*60)
    print("API端点:")
    print("  - GET /api/analyze?code=股票代码")
    print("  - GET /api/health")
    print("="*60)
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=True)
