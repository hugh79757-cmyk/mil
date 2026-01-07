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
                url TEXT UNIQUE,
                source TEXT,
                published_date TEXT,
                content TEXT,
                category TEXT,
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
        
        self.conn.commit()
        logger.info("✅ 테이블 초기화 완료")
    
    def get_statistics(self):
        """통계 조회"""
        cursor = self.conn.cursor()
        
        # 총 RSS 기사 수
        cursor.execute("SELECT COUNT(*) FROM rss_articles")
        total_rss = cursor.fetchone()[0]
        
        # 오늘 수집된 기사 수
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
            SELECT title, url, source, created_at 
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
