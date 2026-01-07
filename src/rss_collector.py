#!/usr/bin/env python3
"""RSS 피드 수집 모듈"""

import feedparser
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RSSCollector:
    """RSS 피드 수집 및 처리"""
    
    def __init__(self, config, db, content_filter=None, translator=None):
        self.config = config
        self.db = db
        self.feeds = config['rss_feeds']
        self.content_filter = content_filter
        self.translator = translator
        logger.info(f"RSS 수집기 초기화: {len(self.feeds)}개 피드")
    
    def collect_all(self):
        """모든 RSS 피드 수집"""
        all_articles = []
        total_filtered = 0
        
        for feed_config in self.feeds:
            try:
                articles, filtered = self.collect_feed(feed_config)
                all_articles.extend(articles)
                total_filtered += filtered
                logger.info(f"✅ {feed_config['name']}: {len(articles)}개 저장 ({filtered}개 필터링됨)")
            except Exception as e:
                logger.error(f"❌ {feed_config['name']} 오류: {e}")
        
        # 번역 처리 (배치로 한 번에)
        if self.translator and all_articles:
            all_articles = self._translate_articles(all_articles)
        
        logger.info(f"📊 총계: {len(all_articles)}개 저장, {total_filtered}개 필터링됨")
        return all_articles
    
    def _translate_articles(self, articles):
        """기사 제목 번역"""
        # 번역 안 된 기사만 필터링
        to_translate = [a for a in articles if not a.get('title_ko')]
        
        if not to_translate:
            return articles
        
        logger.info(f"🌐 {len(to_translate)}개 제목 번역 중...")
        
        titles = [a['title'] for a in to_translate]
        translated = self.translator.translate_batch(titles)
        
        # 번역 결과 적용
        for article, title_ko in zip(to_translate, translated):
            article['title_ko'] = title_ko
            self._update_translation(article['url'], title_ko)
        
        logger.info(f"✅ 번역 완료")
        return articles
    
    def _update_translation(self, url, title_ko):
        """DB에 번역 저장"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                'UPDATE rss_articles SET title_ko = ? WHERE url = ?',
                (title_ko, url)
            )
            self.db.conn.commit()
        except Exception as e:
            logger.error(f"번역 저장 오류: {e}")
    
    def collect_feed(self, feed_config):
        """단일 RSS 피드 수집"""
        feed_name = feed_config['name']
        feed_url = feed_config['url']
        skip_filter = feed_config.get('skip_filter', False)
        
        feed = feedparser.parse(feed_url)
        articles = []
        filtered_count = 0
        
        for entry in feed.entries[:20]:
            article = {
                'title': entry.get('title', 'No title'),
                'url': entry.get('link', ''),
                'source': feed_name,
                'published_date': entry.get('published', ''),
                'summary': entry.get('summary', '')[:500],
                'category': feed_config['category'],
                'score': 0,
                'title_ko': None
            }
            
            # 필터링 적용
            if self.content_filter and not skip_filter:
                text = f"{article['title']} {article['summary']}"
                if not self.content_filter.is_military_related(text):
                    filtered_count += 1
                    logger.debug(f"🚫 필터링: {article['title'][:50]}...")
                    continue
                article['score'] = self.content_filter.calculate_score(article)
            elif self.content_filter and skip_filter:
                article['score'] = self.content_filter.calculate_score(article)
            
            if self.save_article(article):
                articles.append(article)
        
        return articles, filtered_count
    
    def save_article(self, article):
        """기사를 데이터베이스에 저장"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO rss_articles 
                (title, title_ko, url, source, published_date, content, category, score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article['title'],
                article.get('title_ko'),
                article['url'],
                article['source'],
                article['published_date'],
                article['summary'],
                article['category'],
                article.get('score', 0)
            ))
            self.db.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"저장 오류: {e}")
            return False
