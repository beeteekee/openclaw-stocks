#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
舆情数据获取器 - 从真实数据源获取舆情信息
符合养家心法第3条"数据求真原则"
"""

import re
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup


class SentimentDataFetcher:
    """
    真实舆情数据获取器

    从以下平台获取舆情数据：
    - 东方财富股吧
    - 雪球
    - 同花顺
    - 微博
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def fetch_from_eastmoney_guba(self, stock_code: str, stock_name: str, limit: int = 50) -> List[Dict]:
        """
        从东方财富股吧获取评论数据

        Args:
            stock_code: 股票代码（格式：600000.SH 或 000001.SZ）
            stock_name: 股票名称
            limit: 获取数量限制

        Returns:
            评论数据列表
        """
        try:
            # 转换股票代码格式（去除.SZ/.SH，转换为纯数字）
            code_num = stock_code.split('.')[0]

            # 东方财富股吧API
            api_url = f"https://guba.eastmoney.com/list,{code_num},1.html"

            response = self.session.get(api_url, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                print(f"⚠️ 东方财富股吧请求失败: HTTP {response.status_code}")
                return []

            # 方法1：尝试从JavaScript变量中提取JSON数据
            json_match = re.search(r'var\s+article_list\s*=\s*(\{.*?\});', response.text, re.DOTALL)
            if json_match:
                try:
                    import json
                    article_json_str = json_match.group(1)
                    article_data = json.loads(article_json_str)

                    if 're' in article_data and isinstance(article_data['re'], list):
                        comments = []
                        for post in article_data['re'][:limit]:
                            try:
                                title = post.get('post_title', '')
                                author = post.get('user_nickname', '匿名')
                                publish_time = post.get('post_publish_time', '')
                                read_count = post.get('post_click_count', 0)
                                comment_count = post.get('post_comment_count', 0)
                                post_url = post.get('Art_Url', '')

                                # 提取时间（格式如"2026-03-11 11:53:02"）
                                time_match = re.search(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', publish_time)
                                time_str = time_match.group()[11:16] if time_match else publish_time[:16]

                                if title:  # 只添加有标题的帖子
                                    comments.append({
                                        'platform': '东方财富股吧',
                                        'content': title,
                                        'author': author,
                                        'time': time_str,
                                        'read_count': read_count,
                                        'comment_count': comment_count,
                                        'url': post_url
                                    })
                            except Exception as e:
                                continue

                        print(f"✅ 从东方财富股吧（JSON）获取到 {len(comments)} 条评论")
                        return comments

                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON解析失败: {e}")
                    # 继续尝试HTML解析

            # 方法2：从HTML表格中解析
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取评论数据
            comments = []
            table = soup.find('table', class_='default_list')
            if not table:
                print(f"⚠️ 未找到表格数据")
                return []

            tbody = table.find('tbody')
            if not tbody:
                print(f"⚠️ 未找到tbody")
                return []

            rows = tbody.find_all('tr', class_='listitem')
            print(f"找到 {len(rows)} 行数据")

            for row in rows[:limit]:
                try:
                    tds = row.find_all('td')
                    if len(tds) < 5:
                        continue

                    # 阅读数
                    read_div = tds[0].find('div', class_='read')
                    read_count = int(read_div.get_text(strip=True)) if read_div else 0

                    # 评论数
                    reply_div = tds[1].find('div', class_='reply')
                    comment_count = int(reply_div.get_text(strip=True)) if reply_div else 0

                    # 标题和链接
                    title_div = tds[2].find('div', class_='title')
                    if not title_div:
                        continue

                    title_a = title_div.find('a')
                    title = title_a.get_text(strip=True) if title_a else ''
                    link = title_a.get('href', '') if title_a else ''

                    # 作者
                    author_div = tds[3].find('div', class_='author')
                    if author_div:
                        author_a = author_div.find('a')
                        author = author_a.get_text(strip=True) if author_a else '匿名'
                    else:
                        author = '匿名'

                    # 时间
                    update_div = tds[4].find('div', class_='update')
                    time_str = update_div.get_text(strip=True) if update_div else '未知'

                    if title:  # 只添加有标题的帖子
                        comments.append({
                            'platform': '东方财富股吧',
                            'content': title,
                            'author': author,
                            'time': time_str,
                            'read_count': read_count,
                            'comment_count': comment_count,
                            'url': f"https://guba.eastmoney.com{link}" if link else ''
                        })

                except Exception as e:
                    continue

            print(f"✅ 从东方财富股吧（HTML）获取到 {len(comments)} 条评论")
            return comments

        except Exception as e:
            print(f"⚠️ 东方财富股吧获取失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def fetch_from_snowball(self, stock_name: str, limit: int = 50) -> List[Dict]:
        """
        从雪球获取评论数据

        Args:
            stock_name: 股票名称
            limit: 获取数量限制

        Returns:
            评论数据列表
        """
        try:
            # 雪球搜索API
            search_url = f"https://xueqiu.com/search?q={stock_name}"
            headers = {
                'Cookie': 'xq_a_token=xxx',  # 需要真实token
                'User-Agent': self.headers['User-Agent']
            }

            # 注意：雪球需要登录token，这里仅作示例
            # 实际使用时需要配置真实的token
            print(f"⚠️ 雪球API需要登录token，暂未配置")

            return []

        except Exception as e:
            print(f"⚠️ 雪球获取失败: {e}")
            return []

    def fetch_from_weibo(self, keyword: str, limit: int = 50) -> List[Dict]:
        """
        从微博获取相关帖子数据

        Args:
            keyword: 搜索关键词（股票名称）
            limit: 获取数量限制

        Returns:
            帖子数据列表
        """
        try:
            # 微博搜索API（需要登录）
            # 注意：微博API需要登录凭证，这里仅作示例
            print(f"⚠️ 微博API需要登录凭证，暂未配置")

            return []

        except Exception as e:
            print(f"⚠️ 微博获取失败: {e}")
            return []

    def fetch_all(self, stock_code: str, stock_name: str, limit_per_source: int = 20) -> List[Dict]:
        """
        从所有可用数据源获取舆情数据

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            limit_per_source: 每个数据源获取的数量限制

        Returns:
            合并后的舆情数据列表
        """
        all_data = []

        # 从东方财富股吧获取
        eastmoney_data = self.fetch_from_eastmoney_guba(stock_code, stock_name, limit_per_source)
        all_data.extend(eastmoney_data)

        # 从雪球获取（暂未配置）
        # snowball_data = self.fetch_from_snowball(stock_name, limit_per_source)
        # all_data.extend(snowball_data)

        # 从微博获取（暂未配置）
        # weibo_data = self.fetch_from_weibo(stock_name, limit_per_source)
        # all_data.extend(weibo_data)

        print(f"\n📊 总共获取到 {len(all_data)} 条舆情数据")

        # 按平台统计
        platform_count = {}
        for item in all_data:
            platform = item.get('platform', '未知')
            platform_count[platform] = platform_count.get(platform, 0) + 1

        print(f"平台分布: {json.dumps(platform_count, ensure_ascii=False, indent=2)}")

        return all_data


def fetch_sentiment_data(stock_code: str, stock_name: str, limit: int = 50) -> List[Dict]:
    """
    便捷函数：获取舆情数据

    Args:
        stock_code: 股票代码
        stock_name: 股票名称
        limit: 总数量限制

    Returns:
        舆情数据列表
    """
    fetcher = SentimentDataFetcher()
    return fetcher.fetch_all(stock_code, stock_name, limit_per_source=limit)


if __name__ == '__main__':
    # 测试：获取比亚迪的舆情数据
    print("测试：获取比亚迪的舆情数据")
    data = fetch_sentiment_data("002594.SZ", "比亚迪", limit=20)

    print(f"\n获取到 {len(data)} 条数据:")
    for i, item in enumerate(data[:5], 1):
        print(f"\n{i}. [{item['platform']}] {item['content'][:50]}...")
        print(f"   作者: {item['author']}, 时间: {item['time']}")
