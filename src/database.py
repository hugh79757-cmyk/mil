#!/usr/bin/env python3
"""데이터베이스 관리 모듈"""

import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.init_tables()
        logger.info(f"✅ DB 연결: {db_path}")
    
    def init_tables(self):
        """테이블 초기화"""
        cursor = self.conn.cursor()
        
        # RSS 기사 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rss_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                title_ko TEXT,
                url TEXT UNIQUE,
                source TEXT,
                published_date TEXT,
                content TEXT,
                category TEXT,
                score INTEGER DEFAULT 0,
                is_used INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Wikipedia 변경 내역 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wiki_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_title TEXT,
                revision_id INTEGER,
                timestamp TEXT,
                editor TEXT,
                comment TEXT,
                size_change INTEGER,
                detected_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 기존 테이블에 새 컬럼 추가 (이미 있으면 무시)
        try:
            cursor.execute('ALTER TABLE rss_articles ADD COLUMN score INTEGER DEFAULT 0')
        except:
            pass
        
        try:
            cursor.execute('ALTER TABLE rss_articles ADD COLUMN is_used INTEGER DEFAULT 0')
        except:
            pass
        
        try:
            cursor.execute('ALTER TABLE rss_articles ADD COLUMN title_ko TEXT')
        except:
            pass
        
        self.conn.commit()
        logger.info("✅ 테이블 초기화 완료")
    
    def get_statistics(self):
        """통계 조회"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM rss_articles")
        total_rss = cursor.fetchone()[0]
        
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute(
            "SELECT COUNT(*) FROM rss_articles WHERE DATE(created_at) = ?",
            (today,)
        )
        today_rss = cursor.fetchone()[0]
        
        return {
            'total': total_rss,
            'today': today_rss
        }
    
    def get_latest_articles(self, limit=10):
        """최신 기사 조회"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT title, title_ko, url, source, created_at 
            FROM rss_articles 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()
    
    def get_wiki_changes(self, limit=10):
        """최신 Wikipedia 변경사항 조회"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT page_title, comment, editor, detected_at 
            FROM wiki_changes 
            ORDER BY detected_at DESC 
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()
    
    def get_top_articles(self, limit=20):
        """점수 높은 미사용 기사 조회"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, title, title_ko, url, source, score, created_at 
            FROM rss_articles 
            WHERE is_used = 0
            ORDER BY score DESC, created_at DESC 
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()
    
    def mark_as_used(self, article_id):
        """기사를 '사용됨'으로 표시"""
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE rss_articles SET is_used = 1 WHERE id = ?',
            (article_id,)
        )
        self.conn.commit()
