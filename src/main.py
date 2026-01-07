#!/usr/bin/env python3
import yaml
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MilitaryNewsAggregator:
    def __init__(self):
        config_file = Path(__file__).parent.parent / 'config.yaml'
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        logger.info("✅ 설정 로드 완료")
    
    def start(self):
        logger.info("🚀 Military News Aggregator 시작")
        print("\n📡 RSS 피드:")
        for feed in self.config['rss_feeds']:
            print(f"  - {feed['name']}")
        print("\n📚 Wikipedia 모니터링:")
        for page in self.config['wikipedia']['pages']:
            print(f"  - {page['title']}")

if __name__ == '__main__':
    app = MilitaryNewsAggregator()
    app.start()
