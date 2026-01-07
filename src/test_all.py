#!/usr/bin/env python3
"""전체 시스템 테스트 스크립트"""

import yaml
import sys
from pathlib import Path

# 상위 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from database import Database
from content_filter import ContentFilter
from rss_collector import RSSCollector


def main():
    print("=" * 60)
    print("🧪 Military News Aggregator 테스트")
    print("=" * 60)
    
    # 1. 설정 로드
    print("\n📁 [1/5] 설정 로드...")
    config_file = Path(__file__).parent.parent / 'config.yaml'
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print(f"   ✅ RSS 피드: {len(config['rss_feeds'])}개")
    print(f"   ✅ Wikipedia 페이지: {len(config['wikipedia']['pages'])}개")
    print(f"   ✅ 고우선순위 키워드: {len(config['filters']['high_priority'])}개")
    print(f"   ✅ 중간우선순위 키워드: {len(config['filters']['medium_priority'])}개")
    print(f"   ✅ 제외 키워드: {len(config['filters']['exclude'])}개")
    
    # 2. 데이터베이스 초기화
    print("\n💾 [2/5] 데이터베이스 초기화...")
    db_path = Path(__file__).parent.parent / config['database']['path']
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = Database(str(db_path))
    stats = db.get_statistics()
    print(f"   ✅ DB 경로: {db_path}")
    print(f"   ✅ 기존 기사: {stats['total']}개")
    
    # 3. 콘텐츠 필터 테스트
    print("\n🔍 [3/5] 콘텐츠 필터 테스트...")
    content_filter = ContentFilter(config)
    
    test_titles = [
        "F-35 stealth fighter deployed to South Korea",
        "K-beauty products gain popularity in China", 
        "North Korea launches ICBM missile test",
        "Korean drama wins international award",
        "US Navy aircraft carrier arrives in Pacific",
        "Seoul weather forecast for next week",
        "KF-21 Boramae completes new test flight",
        "Pentagon announces defense budget increase",
    ]
    
    print("   테스트 제목 필터링 결과:")
    print("-" * 60)
    for title in test_titles:
        is_military = content_filter.is_military_related(title)
        score = content_filter.calculate_score({'title': title, 'summary': ''})
        status = "✅ 통과" if is_military else "❌ 제외"
        print(f"   {status} (점수:{score:3d}) | {title[:45]}...")
    print("-" * 60)
    
    # 4. RSS 수집 테스트
    print("\n📡 [4/5] RSS 수집 테스트 (실제 수집)...")
    rss_collector = RSSCollector(config, db, content_filter)
    articles = rss_collector.collect_all()
    
    # 5. 결과 출력
    print("\n📊 [5/5] 수집 결과")
    print("=" * 60)
    
    # 소스별 통계
    source_stats = {}
    for article in articles:
        source = article['source']
        source_stats[source] = source_stats.get(source, 0) + 1
    
    print("\n📰 소스별 수집 현황:")
    for source, count in source_stats.items():
        print(f"   • {source}: {count}개")
    
    # 점수별 상위 기사
    if articles:
        sorted_articles = sorted(articles, key=lambda x: x.get('score', 0), reverse=True)
        
        print("\n🔥 점수 상위 10개 기사:")
        print("-" * 60)
        for i, article in enumerate(sorted_articles[:10], 1):
            score = article.get('score', 0)
            title = article['title'][:50]
            source = article['source']
            print(f"   {i:2d}. [{score:3d}점] [{source}]")
            print(f"       {title}...")
        print("-" * 60)
        
        print("\n📉 점수 하위 5개 기사 (필터 통과했지만 점수 낮음):")
        print("-" * 60)
        for i, article in enumerate(sorted_articles[-5:], 1):
            score = article.get('score', 0)
            title = article['title'][:50]
            source = article['source']
            print(f"   {i:2d}. [{score:3d}점] [{source}]")
            print(f"       {title}...")
        print("-" * 60)
    
    # DB 최종 통계
    final_stats = db.get_statistics()
    print(f"\n💾 DB 최종 통계:")
    print(f"   • 총 기사: {final_stats['total']}개")
    print(f"   • 오늘 수집: {final_stats['today']}개")
    
    # 상위 기사 조회 테스트
    print("\n🏆 DB에서 상위 기사 조회 (get_top_articles):")
    top_articles = db.get_top_articles(5)
    for i, (id, title, url, source, score, created) in enumerate(top_articles, 1):
        print(f"   {i}. [{score}점] {title[:45]}...")
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)


if __name__ == '__main__':
    main()
