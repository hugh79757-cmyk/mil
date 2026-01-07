#!/usr/bin/env python3
"""RSS 피드 수집 모듈"""

import feedparser
import logging
from datetime import datetime
from database import Database

logger = logging.getLogger(__name__)


class RSSCollector:
    """RSS 피드 수집 및 처리"""
    
    def __init__(self, config, db):
        self.config = config
        self.db = db
        self.feeds = config['rss_feeds']
        logger.info(f"RSS 수집기 초기화: {len(self.feeds)}개 피드")
    
    def collect_all(self):
        """모든 RSS 피드 수집"""
        all_articles = []
        
        for feed_config in self.feeds:
            try:
                articles = self.collect_feed(feed_config)
                all_articles.extend(articles)
                logger.info(f"✅ {feed_config['name']}: {len(articles)}개 수집")
            except Exception as e:
                logger.error(f"❌ {feed_config['name']} 오류: {e}")
        
        return all_articles
    
    def collect_feed(self, feed_config):
        """단일 RSS 피드 수집"""
        feed_name = feed_config['name']
        feed_url = feed_config['url']
        
        # RSS 파싱
        feed = feedparser.parse(feed_url)
        articles = []
        
        for entry in feed.entries[:10]:  # 최신 10개만
            article = {
                'title': entry.get('title', 'No title'),
                'url': entry.get('link', ''),
                'source': feed_name,
                'published_date': entry.get('published', ''),
                'summary': entry.get('summary', '')[:500],
                'category': feed_config['category']
            }
            
            # 데이터베이스 저장
            if self.save_article(article):
                articles.append(article)
        
        return articles
    
    def save_article(self, article):
        """기사를 데이터베이스에 저장"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO rss_articles 
                (title, url, source, published_date, content, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                article['title'],
                article['url'],
                article['source'],
                article['published_date'],
                article['summary'],
                article['category']
            ))
            self.db.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"저장 오류: {e}")
            return False
