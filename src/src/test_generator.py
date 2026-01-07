#!/usr/bin/env python3
"""콘텐츠 생성기 테스트"""

import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import Database
from content_generator import ContentGenerator


def main():
    print("=" * 60)
    print("📝 콘텐츠 생성기 테스트")
    print("=" * 60)
    
    # 설정 로드
    config_file = Path(__file__).parent.parent / 'config.yaml'
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # DB 연결
    db_path = Path(__file__).parent.parent / config['database']['path']
    db = Database(str(db_path))
    
    # 생성기 초기화
    generator = ContentGenerator(config, db)
    
    # 테스트 1: 샘플 뉴스로 테스트
    print("\n🧪 테스트 1: 샘플 뉴스")
    print("-" * 60)
    
    test_articles = [
        {
            'title': 'Poland orders 100 more K2 tanks from Hyundai Rotem',
            'title_ko': '폴란드, 현대로템에 K2 전차 100대 추가 주문',
            'url': 'https://example.com/news1',
            'source': 'Defense News'
        },
        {
            'title': 'KF-21 Boramae completes first supersonic flight test',
            'title_ko': 'KF-21 보라매, 첫 초음속 비행 시험 성공',
            'url': 'https://example.com/news2',
            'source': 'Yonhap News'
        },
        {
            'title': 'Hanwha Aerospace wins $2B artillery contract',
            'title_ko': '한화에어로스페이스, 20억 달러 포병 계약 수주',
            'url': 'https://example.com/news3',
            'source': 'Reuters'
        }
    ]
    
    for article in test_articles:
        content = generator.generate_from_news(article)
        if content:
            print(content)
        else:
            print(f"❌ 매칭 실패: {article['title'][:50]}...")
        print()
    
    # 테스트 2: DB에서 실제 기사로 테스트
    print("\n🧪 테스트 2: DB 상위 기사")
    print("-" * 60)
    
    results = generator.process_top_articles(limit=3)
    
    if results:
        for r in results:
            print(f"\n📰 원본: {r['article']['title'][:50]}...")
            print(r['content'])
    else:
        print("❌ 매칭되는 기사가 없습니다.")
        print("   (DB에 K2, KF-21, Hanwha 등 키워드가 포함된 기사가 필요합니다)")
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)


if __name__ == '__main__':
    main()