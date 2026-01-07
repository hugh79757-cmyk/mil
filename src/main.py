#!/usr/bin/env python3
"""Military News Aggregator - Main Entry Point"""

import yaml
import logging
import threading
import time
from pathlib import Path
from database import Database
from rss_collector import RSSCollector
from wiki_monitor import WikipediaMonitor
from content_filter import ContentFilter
from translator import Translator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MilitaryNewsAggregator:
    def __init__(self):
        logger.info("🚀 Military News Aggregator 시작...")
        
        # 설정 로드
        config_file = Path(__file__).parent.parent / 'config.yaml'
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 데이터베이스 초기화
        db_path = Path(__file__).parent.parent / self.config['database']['path']
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = Database(str(db_path))
        
        # 모듈 초기화
        self.content_filter = ContentFilter(self.config)
        self.translator = Translator(self.config)
        self.rss_collector = RSSCollector(
            self.config, 
            self.db, 
            self.content_filter,
            self.translator
        )
        self.wiki_monitor = WikipediaMonitor(self.config, self.db)
        
        logger.info("✅ 초기화 완료")
    
    def start(self):
        """모든 수집 모듈 시작"""
        threads = []
        
        # 1. RSS 수집 스레드
        logger.info("📡 RSS 수집 시작...")
        rss_thread = threading.Thread(
            target=self._run_rss_collector,
            daemon=True
        )
        threads.append(rss_thread)
        rss_thread.start()
        
        # 2. Wikipedia 실시간 모니터링 스레드
        if self.config['wikipedia']['enabled']:
            logger.info("📚 Wikipedia 실시간 모니터링 시작...")
            wiki_thread = threading.Thread(
                target=self.wiki_monitor.start_realtime_monitoring,
                daemon=True
            )
            threads.append(wiki_thread)
            wiki_thread.start()
        
        logger.info("=" * 60)
        logger.info("✅ 모든 모듈 실행 중 (Ctrl+C로 종료)")
        logger.info("=" * 60)
        
        # 메인 스레드 유지
        try:
            while True:
                time.sleep(60)
                self._print_status()
        except KeyboardInterrupt:
            logger.info("\n⏹️  종료 중...")
    
    def _run_rss_collector(self):
        """RSS 수집기 주기 실행"""
        interval = self.config['schedule']['rss_collection_interval']
        
        while True:
            try:
                articles = self.rss_collector.collect_all()
                
                if articles:
                    sorted_articles = sorted(articles, key=lambda x: x.get('score', 0), reverse=True)
                    logger.info("\n🔥 주요 기사:")
                    for i, article in enumerate(sorted_articles[:3], 1):
                        title_display = article.get('title_ko') or article['title']
                        logger.info(f"   {i}. [{article['source']}] {title_display[:50]}... (점수: {article.get('score', 0)})")
            except Exception as e:
                logger.error(f"RSS 수집 오류: {e}")
            
            time.sleep(interval)
    
    def _print_status(self):
        """시스템 상태 출력"""
        stats = self.db.get_statistics()
        logger.info(f"📊 통계: 총 {stats['total']}개 | 오늘 {stats['today']}개")
        
        # DeepL 사용량 출력
        usage = self.translator.get_usage()
        if usage:
            percent = (usage['used'] / usage['limit']) * 100
            logger.info(f"🌐 DeepL: {usage['used']:,} / {usage['limit']:,} ({percent:.1f}%)")


if __name__ == '__main__':
    app = MilitaryNewsAggregator()
    app.start()
