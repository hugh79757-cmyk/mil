#!/usr/bin/env python3
"""외부 API 테스트"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from wikidata_client import WikidataClient
from acled_client import ACLEDClient


def main():
    print("=" * 60)
    print("🌍 외부 API 테스트")
    print("=" * 60)
    
    # Wikidata 테스트
    print("\n📚 [1] Wikidata 테스트")
    print("-" * 60)
    
    wiki = WikidataClient()
    
    # 한국 관련 전투
    print("\n🇰🇷 한국이 참전한 전투:")
    battles = wiki.get_battles_by_country("korea")
    results = wiki.format_results(battles)
    for i, b in enumerate(results[:5], 1):
        print(f"   {i}. {b.get('battleLabel', 'N/A')} - {b.get('warLabel', 'N/A')}")
    
    # 전차전 목록
    print("\n🛡️ 역사 속 전차전:")
    tank_battles = wiki.get_tank_battles()
    results = wiki.format_results(tank_battles)
    for i, b in enumerate(results[:5], 1):
        date = b.get('date', 'N/A')[:10] if b.get('date') else 'N/A'
        print(f"   {i}. {b.get('battleLabel', 'N/A')} ({date})")
    
    # 공중전 목록
    print("\n✈️ 역사 속 공중전:")
    air_battles = wiki.get_air_battles()
    results = wiki.format_results(air_battles)
    for i, b in enumerate(results[:5], 1):
        print(f"   {i}. {b.get('battleLabel', 'N/A')} - {b.get('warLabel', 'N/A')}")
    
    # 무기 검색
    print("\n🔫 'F-35' 관련 정보:")
    weapons = wiki.get_weapon_info("F-35")
    results = wiki.format_results(weapons)
    for i, w in enumerate(results[:3], 1):
        print(f"   {i}. {w.get('itemLabel', 'N/A')}")
        print(f"      {w.get('description', 'N/A')[:80]}")
    
    # ACLED 테스트
    print("\n" + "=" * 60)
    print("⚔️ [2] ACLED 테스트 (실시간 분쟁)")
    print("-" * 60)
    
    acled = ACLEDClient()
    
    # 최근 분쟁
    print("\n🔥 최근 7일 분쟁 이벤트:")
    conflicts = acled.get_recent_conflicts(days=7, limit=20)
    
    if conflicts:
        summary = acled.summarize_conflicts(conflicts)
        print(f"   총 이벤트: {summary['total_events']}건")
        print(f"   총 사망자: {summary['fatalities']}명")
        print(f"\n   국가별:")
        for country, count in list(summary['by_country'].items())[:5]:
            print(f"      - {country}: {count}건")
        print(f"\n   유형별:")
        for etype, count in list(summary['by_type'].items())[:5]:
            print(f"      - {etype}: {count}건")
    else:
        print("   ⚠️ ACLED API 키 없이는 제한된 데이터만 접근 가능")
        print("   https://acleddata.com 에서 무료 등록 후 API 키 발급")
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)


if __name__ == '__main__':
    main()
