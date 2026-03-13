#!/usr/bin/env python3
"""养家心法选股服务 - 提供股票分析API
更新：Flask服务端口改为5000"""

from flask import Flask, jsonify, request, send_file
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

app = Flask(__name__)
CORS(app)

# 从环境变量读取配置
TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN')
STATS_FILE = os.getenv('STATS_FILE', '/Users/likan/.openclaw/workspace/query_stats.json')
TOP3_TODAY_FILE = os.getenv('TOP3_RESULT_FILE', '/Users/likan/.openclaw/workspace/top3_today_result.csv')
FEISHU_APP_ID = os.getenv('FEISHU_APP_ID', '')
FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET', '')
FEISHU_REGION = os.getenv('FEISHU_REGION', 'cn')

# Flask服务端口（硬编码为5000）
FLASK_PORT = 5000

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

def get_industry_growth_coefficient(industry, concepts=None):
    """
    根据行业名称和概念板块获取成长系数
    """
    # 优先匹配概念板块中的高成长概念
    if concepts:
        for concept in concepts:
            concept = str(concept)
            for key, value in INDUSTRY_GROWTH.items():
                if key in concept:
                    return value

    # 如果没有匹配概念，使用行业字段
    return INDUSTRY_GROWTH.get(industry, 0.3)

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
QUERY_STATS = load_query_stats()

# 初始化Tushare API
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

def get_stock_basic_info(stock_code):
    """
    获取股票基本信息
    """
    try:
        df = pro.daily(ts_code=stock_code, start_date='20260309', end_date='20260311')
        if len(df) > 0:
            latest = df.iloc[0]
            return {
                'code': stock_code,
                'close': float(latest['close']),
                'pct_chg': float(latest['pct_chg']),
                'volume': int(latest['vol']),
                'date': str(latest['trade_date'])
            }
        return None
    except Exception as e:
        print(f"⚠️ 获取股票基本信息失败 {stock_code}: {e}")
        return None

def get_top_stocks_today(limit=10):
    """
    获取今日TOP股票（从top3_today_result.csv）
    """
    try:
        df = pd.read_csv(TOP3_TODAY_FILE, encoding='utf-8-sig')
        if len(df) > 0:
            # 按赢面率排序
            df_sorted = df.sort_values('win_rate', ascending=False)
            top_stocks = df_sorted.head(limit).to_dict('records')
            return top_stocks
        return []
    except Exception as e:
        print(f"⚠️ 读取TOP3今日结果失败: {e}")
        return []

def calculate_sentiment_score(stock_code, stock_name):
    """
    计算舆情热度得分（占位函数）
    TODO: 集成MiroFish情感分析器
    """
    # 占位实现：基于行业成长系数和查询次数
    industry_growth = 0.3  # 默认中成长
    query_count = QUERY_STATS['stock_queries'].get(stock_code, 0)
    
    # 舆情热度 = 行业成长 * 50 + 查询热度 * 50
    sentiment_heat = industry_growth * 50 + min(query_count * 2, 50)
    
    return {
        'heat_score': round(sentiment_heat, 2),
        'query_count': query_count,
        'data_source': '东方财富股吧'  # 占位
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': '养家心法选股服务',
        'version': '1.0.0',
        'port': FLASK_PORT
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取查询统计信息"""
    return jsonify(QUERY_STATS)

@app.route('/api/analyze', methods=['GET'])
def analyze_stock():
    """分析单只股票 - 调用完整分析逻辑"""
    stock_code = request.args.get('code', '')

    if not stock_code:
        return jsonify({'error': 'Missing stock code parameter'}), 400

    # 记录查询统计
    QUERY_STATS['total_count'] += 1
    QUERY_STATS['stock_queries'][stock_code] = QUERY_STATS['stock_queries'].get(stock_code, 0) + 1
    save_query_stats()

    try:
        # 导入完整分析模块
        import sys
        sys.path.append('/Users/likan/.openclaw/workspace')
        from top3_today import analyze_stock as full_analyze

        # 调用完整分析函数
        result = full_analyze(stock_code, pro)

        if not result:
            return jsonify({'error': 'Stock not found or analysis failed'}), 404

        # 添加查询统计信息
        result['query_count'] = QUERY_STATS['stock_queries'].get(stock_code, 0)

        # 将不可序列化的类型转换为JSON兼容类型
        result['price_above_ma250'] = bool(result.get('price_above_ma250', False))
        if 'ma250' in result and result['ma250'] is not None:
            result['ma250'] = float(result['ma250'])

        return jsonify(result)

    except Exception as e:
        print(f"分析失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/top3', methods=['GET'])
def get_top_stocks():
    """获取TOP3股票"""
    limit = int(request.args.get('limit', 10))
    top_stocks = get_top_stocks_today(limit=limit)
    
    return jsonify({
        'total_count': len(top_stocks),
        'stocks': top_stocks
    })

@app.route('/api/sentiment', methods=['GET'])
def get_sentiment():
    """获取舆情分析（占位）"""
    stock_code = request.args.get('code', '')
    limit = int(request.args.get('limit', 30))
    
    if not stock_code:
        return jsonify({'error': 'Missing stock code parameter'}), 400
    
    # 记录查询统计
    QUERY_STATS['total_count'] += 1
    QUERY_STATS['stock_queries'][stock_code] = QUERY_STATS['stock_queries'].get(stock_code, 0) + 1
    save_query_stats()
    
    # 占位：调用MiroFish情感分析器
    # TODO: from mirofish_sentiment import fetch_sentiment_data, MiroFishSentimentAnalyzer
    
    sentiment = calculate_sentiment_score(stock_code, '')
    
    return jsonify({
        'code': stock_code,
        'limit': limit,
        'sentiment_heat_score': sentiment['heat_score'],
        'query_count': sentiment['query_count'],
        'data_source': sentiment['data_source']
    })

@app.route('/api/industry-growth', methods=['GET'])
def get_industry_growth_coefficients():
    """获取行业成长系数表"""
    return jsonify(INDUSTRY_GROWTH)

# 静态文件服务（前端页面）
FRONTEND_DIR = '/Users/likan/.openclaw/workspace/stockbot-frontend/public'

@app.route('/')
def index():
    """首页：重定向到股票分析页面"""
    return send_file(os.path.join(FRONTEND_DIR, 'stock-analysis-final.html'))

@app.route('/stock-analysis-final.html')
def stock_analysis():
    """股票分析页面"""
    return send_file(os.path.join(FRONTEND_DIR, 'stock-analysis-final.html'))

if __name__ == '__main__':
    print(f"🚀 启动养家心法选股服务...")
    print(f"📊 服务地址：http://localhost:{FLASK_PORT}")
    print(f"🌐 健康检查：http://localhost:{FLASK_PORT}/api/health")
    print(f"📊 查询统计：http://localhost:{FLASK_PORT}/api/stats")
    print(f"📈 TOP3股票：http://localhost:{FLASK_PORT}/api/top3")
    print(f"🎯 股票分析：http://localhost:{FLASK_PORT}/api/analyze?code=<code>")
    print(f"😊 舆情分析：http://localhost:{FLASK_PORT}/api/sentiment?code=<code>")
    print(f"🏭 行业成长系数：http://localhost:{FLASK_PORT}/api/industry-growth")
    print("")
    print(f"⚠️  按 Ctrl+C 停止服务")
    print("")
    
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=False)
