#!/usr/bin/env python3
"""Wikipedia 실시간 모니터링 모듈"""

import json
import time
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WikipediaMonitor:
    """Wikipedia EventStreams 실시간 모니터링"""
    
    def __init__(self, config, db):
        self.config = config
        self.db = db
        self.stream_url = config['wikipedia']['stream_url']
        self.target_pages = {
            page['title']: page 
            for page in config['wikipedia']['pages']
        }
        logger.info(f"Wikipedia 모니터 초기화: {len(self.target_pages)}개 페이지")
    
    def start_realtime_monitoring(self):
        """실시간 모니터링 시작 (자동 재연결)"""
        logger.info("🔴 Wikipedia 실시간 모니터링 시작...")
        logger.info(f"📋 대상: {', '.join(self.target_pages.keys())}")
        
        while True:
            try:
                with requests.get(self.stream_url, stream=True, timeout=300) as response:
                    for line in response.iter_lines():
                        if line:
                            self.process_event(line)
            except requests.exceptions.Timeout:
                logger.warning("⏱️ 타임아웃, 재연결 중...")
            except requests.exceptions.ConnectionError:
                logger.warning("🔌 연결 끊김, 5초 후 재연결...")
                time.sleep(5)
            except Exception as e:
                logger.error(f"모니터링 오류: {e}, 10초 후 재연결...")
                time.sleep(10)
    
    def process_event(self, line):
        """이벤트 처리"""
        try:
            line = line.decode('utf-8')
            
            if line.startswith('data:'):
                data = json.loads(line[6:])
                
                # 영문 위키백과만
                if data.get('wiki') == 'enwiki':
                    title = data.get('title', '')
                    
                    # 관심 페이지인지 확인
                    if title in self.target_pages:
                        self.handle_page_change(data)
        except Exception as e:
            logger.debug(f"이벤트 파싱 오류: {e}")
    
    def handle_page_change(self, data):
        """페이지 변경 처리"""
        title = data['title']
        revid = data.get('revision', {}).get('new')
        timestamp = data.get('timestamp')
        user = data.get('user', 'Unknown')
        comment = data.get('comment', '')
        size_change = data.get('length', {}).get('new', 0) - data.get('length', {}).get('old', 0)
        
        page_info = self.target_pages[title]
        
        # 로그 출력
        logger.info(f"\n🚨 [{title}] 업데이트 감지!")
        logger.info(f"   🏷️ 카테고리: {page_info['category']} / {page_info['country']}")
        logger.info(f"   📝 편집: {comment[:80]}")
        logger.info(f"   👤 편집자: {user}")
        logger.info(f"   📊 크기 변화: {size_change:+d} bytes")
        logger.info(f"   🔗 https://en.wikipedia.org/w/index.php?diff={revid}")
        
        # 데이터베이스 저장
        self.save_change(title, revid, timestamp, user, comment, size_change)
    
    def save_change(self, title, revid, timestamp, user, comment, size_change):
        """변경사항 저장"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT INTO wiki_changes 
                (page_title, revision_id, timestamp, editor, comment, size_change)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, revid, timestamp, user, comment, size_change))
            self.db.conn.commit()
            logger.info(f"   💾 DB 저장 완료")
        except Exception as e:
            logger.error(f"저장 오류: {e}")
