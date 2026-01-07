#!/usr/bin/env python3
"""블로그 콘텐츠 생성기 (Wikidata 연동) - 확장판"""

import logging
from datetime import datetime
from wikidata_client import WikidataClient

logger = logging.getLogger(__name__)


class ContentGenerator:
    """전쟁사 + 무기 + 투자 융합 콘텐츠 생성"""
    
    def __init__(self, config, db, translator=None):
        self.config = config
        self.db = db
        self.translator = translator
        self.wikidata = WikidataClient()
        
        # 확장된 키워드 매핑
        self.keyword_map = {
            # 한국 무기
            "k2": {"search": "K2 tank", "type": "tank", "country": "korea"},
            "k9": {"search": "K9 Thunder", "type": "artillery", "country": "korea"},
            "k21": {"search": "K21", "type": "vehicle", "country": "korea"},
            "kf-21": {"search": "KF-21", "type": "aircraft", "country": "korea"},
            "kf21": {"search": "KF-21", "type": "aircraft", "country": "korea"},
            "fa-50": {"search": "FA-50", "type": "aircraft", "country": "korea"},
            "t-50": {"search": "T-50", "type": "aircraft", "country": "korea"},
            "hyunmoo": {"search": "Hyunmoo", "type": "missile", "country": "korea"},
            "천무": {"search": "Chunmoo", "type": "rocket", "country": "korea"},
            "천궁": {"search": "Cheongung", "type": "missile", "country": "korea"},
            
            # 미국 무기
            "f-35": {"search": "F-35", "type": "aircraft", "country": "us"},
            "f-22": {"search": "F-22", "type": "aircraft", "country": "us"},
            "f-16": {"search": "F-16", "type": "aircraft", "country": "us"},
            "f-15": {"search": "F-15", "type": "aircraft", "country": "us"},
            "b-52": {"search": "B-52", "type": "bomber", "country": "us"},
            "b-21": {"search": "B-21", "type": "bomber", "country": "us"},
            "b-2": {"search": "B-2", "type": "bomber", "country": "us"},
            "m1 abrams": {"search": "M1 Abrams", "type": "tank", "country": "us"},
            "abrams": {"search": "M1 Abrams", "type": "tank", "country": "us"},
            "patriot": {"search": "Patriot missile", "type": "missile", "country": "us"},
            "thaad": {"search": "THAAD", "type": "missile", "country": "us"},
            "himars": {"search": "HIMARS", "type": "rocket", "country": "us"},
            "javelin": {"search": "Javelin missile", "type": "missile", "country": "us"},
            "tomahawk": {"search": "Tomahawk missile", "type": "missile", "country": "us"},
            
            # 러시아 무기
            "t-90": {"search": "T-90", "type": "tank", "country": "russia"},
            "t-72": {"search": "T-72", "type": "tank", "country": "russia"},
            "t-14": {"search": "T-14 Armata", "type": "tank", "country": "russia"},
            "su-57": {"search": "Su-57", "type": "aircraft", "country": "russia"},
            "su-35": {"search": "Su-35", "type": "aircraft", "country": "russia"},
            "s-400": {"search": "S-400", "type": "missile", "country": "russia"},
            "iskander": {"search": "Iskander", "type": "missile", "country": "russia"},
            
            # 중국 무기
            "j-20": {"search": "J-20", "type": "aircraft", "country": "china"},
            "df-21": {"search": "DF-21", "type": "missile", "country": "china"},
            "type 99": {"search": "Type 99 tank", "type": "tank", "country": "china"},
            
            # 유럽 무기
            "leopard": {"search": "Leopard 2", "type": "tank", "country": "germany"},
            "eurofighter": {"search": "Eurofighter", "type": "aircraft", "country": "germany"},
            "rafale": {"search": "Rafale", "type": "aircraft", "country": "france"},
            "challenger": {"search": "Challenger 2", "type": "tank", "country": "uk"},
            
            # 일반 카테고리
            "tank": {"search": "tank", "type": "tank", "country": None},
            "drone": {"search": "drone", "type": "drone", "country": None},
            "uav": {"search": "UAV", "type": "drone", "country": None},
            "missile": {"search": "missile", "type": "missile", "country": None},
            "icbm": {"search": "ICBM", "type": "missile", "country": None},
            "slbm": {"search": "SLBM", "type": "missile", "country": None},
            "submarine": {"search": "submarine", "type": "submarine", "country": None},
            "aircraft carrier": {"search": "aircraft carrier", "type": "naval", "country": None},
            "carrier": {"search": "aircraft carrier", "type": "naval", "country": None},
            "destroyer": {"search": "destroyer", "type": "naval", "country": None},
            "frigate": {"search": "frigate", "type": "naval", "country": None},
            "nuclear": {"search": "nuclear", "type": "nuclear", "country": None},
            "stealth": {"search": "stealth", "type": "aircraft", "country": None},
            "hypersonic": {"search": "hypersonic", "type": "missile", "country": None},
            
            # 국가/분쟁
            "ukraine": {"search": "Ukraine", "type": "conflict", "country": "ukraine"},
            "russia": {"search": "Russia", "type": "conflict", "country": "russia"},
            "china": {"search": "China", "type": "conflict", "country": "china"},
            "taiwan": {"search": "Taiwan", "type": "conflict", "country": "taiwan"},
            "north korea": {"search": "North Korea", "type": "conflict", "country": "north korea"},
            "iran": {"search": "Iran", "type": "conflict", "country": "iran"},
            "israel": {"search": "Israel", "type": "conflict", "country": "israel"},
            "gaza": {"search": "Gaza", "type": "conflict", "country": "palestine"},
            "poland": {"search": "Poland", "type": "export", "country": "poland"},
            "nato": {"search": "NATO", "type": "alliance", "country": None},
            "pentagon": {"search": "Pentagon", "type": "military", "country": "us"},
            
            # 방산 기업
            "hanwha": {"search": "Hanwha", "type": "company", "country": "korea"},
            "hyundai rotem": {"search": "Hyundai Rotem", "type": "company", "country": "korea"},
            "kai": {"search": "Korea Aerospace", "type": "company", "country": "korea"},
            "lig nex1": {"search": "LIG Nex1", "type": "company", "country": "korea"},
            "boeing": {"search": "Boeing", "type": "company", "country": "us"},
            "lockheed": {"search": "Lockheed Martin", "type": "company", "country": "us"},
            "raytheon": {"search": "Raytheon", "type": "company", "country": "us"},
            "northrop": {"search": "Northrop Grumman", "type": "company", "country": "us"},
            "general dynamics": {"search": "General Dynamics", "type": "company", "country": "us"},
            "bae": {"search": "BAE Systems", "type": "company", "country": "uk"},
            "rheinmetall": {"search": "Rheinmetall", "type": "company", "country": "germany"},
        }
        
        # 투자 정보
        self.stock_info = {
            # 한국 무기
            "k2": ["현대로템(064350)", "풍산(103140)"],
            "k9": ["한화에어로스페이스(012450)", "풍산(103140)"],
            "k21": ["한화에어로스페이스(012450)"],
            "kf-21": ["한국항공우주(047810)", "한화시스템(272210)", "LIG넥스원(079550)"],
            "kf21": ["한국항공우주(047810)", "한화시스템(272210)", "LIG넥스원(079550)"],
            "fa-50": ["한국항공우주(047810)"],
            "t-50": ["한국항공우주(047810)"],
            "hyunmoo": ["LIG넥스원(079550)", "한화에어로스페이스(012450)"],
            "천무": ["한화에어로스페이스(012450)"],
            "천궁": ["LIG넥스원(079550)"],
            
            # 일반 카테고리
            "tank": ["현대로템(064350)", "한화에어로스페이스(012450)"],
            "drone": ["한화시스템(272210)", "대한항공(003490)"],
            "uav": ["한화시스템(272210)", "대한항공(003490)"],
            "missile": ["LIG넥스원(079550)", "한화에어로스페이스(012450)"],
            "submarine": ["한화오션(042660)", "HD현대중공업(329180)"],
            "aircraft carrier": ["한화오션(042660)", "HD현대중공업(329180)"],
            "carrier": ["한화오션(042660)", "HD현대중공업(329180)"],
            "destroyer": ["한화오션(042660)", "HD현대중공업(329180)"],
            "nuclear": ["두산에너빌리티(034020)"],
            
            # 방산 기업
            "hanwha": ["한화에어로스페이스(012450)", "한화시스템(272210)", "한화오션(042660)"],
            "hyundai rotem": ["현대로템(064350)"],
            "kai": ["한국항공우주(047810)"],
            "lig nex1": ["LIG넥스원(079550)"],
            "boeing": ["보잉(BA)"],
            "lockheed": ["록히드마틴(LMT)"],
            "raytheon": ["레이시온(RTX)"],
            "northrop": ["노스롭그루먼(NOC)"],
            "general dynamics": ["제너럴다이내믹스(GD)"],
            
            # 국가별 수출
            "poland": ["현대로템(064350)", "한화에어로스페이스(012450)", "한국항공우주(047810)"],
            "ukraine": ["현대로템(064350)", "한화에어로스페이스(012450)"],
            
            # 미국 무기
            "f-35": ["록히드마틴(LMT)", "한화시스템(272210)"],
            "f-22": ["록히드마틴(LMT)"],
            "b-52": ["보잉(BA)"],
            "b-21": ["노스롭그루먼(NOC)"],
            "patriot": ["레이시온(RTX)"],
            "thaad": ["록히드마틴(LMT)"],
            "himars": ["록히드마틴(LMT)"],
            "abrams": ["제너럴다이내믹스(GD)"],
        }
        
        logger.info("✅ 콘텐츠 생성기 초기화 (확장 키워드)")
    
    def find_keyword(self, title):
        """뉴스 제목에서 키워드 찾기"""
        title_lower = title.lower()
        
        # 긴 키워드부터 매칭 (더 정확한 매칭)
        sorted_keywords = sorted(self.keyword_map.keys(), key=len, reverse=True)
        
        for keyword in sorted_keywords:
            if keyword in title_lower:
                return keyword
        return None
    
    def get_related_battles(self, keyword):
        """키워드 관련 전투 검색"""
        if keyword not in self.keyword_map:
            return []
        
        info = self.keyword_map[keyword]
        battles = []
        
        if info["type"] == "tank":
            results = self.wikidata.get_tank_battles()
            battles = self.wikidata.format_results(results)[:5]
        elif info["type"] in ["aircraft", "bomber"]:
            results = self.wikidata.get_air_battles()
            battles = self.wikidata.format_results(results)[:5]
        elif info["country"]:
            results = self.wikidata.get_battles_by_country(info["country"])
            battles = self.wikidata.format_results(results)[:5]
        else:
            results = self.wikidata.search_military_history(info["search"])
            battles = self.wikidata.format_results(results)[:5]
        
        return battles
    
    def get_weapon_info(self, keyword):
        """무기 정보 검색"""
        if keyword not in self.keyword_map:
            return []
        
        search_term = self.keyword_map[keyword]["search"]
        results = self.wikidata.get_weapon_info(search_term)
        return self.wikidata.format_results(results)[:3]
    
    def get_stock_info(self, keyword):
        """관련 종목 정보"""
        return self.stock_info.get(keyword, [])
    
    def generate_content(self, article):
        """뉴스에서 블로그 콘텐츠 생성"""
        title = article.get('title', '')
        title_ko = article.get('title_ko', '')
        url = article.get('url', '')
        source = article.get('source', '')
        
        keyword = self.find_keyword(title)
        if not keyword:
            return None
        
        battles = self.get_related_battles(keyword)
        weapons = self.get_weapon_info(keyword)
        stocks = self.get_stock_info(keyword)
        
        content = self._format_content(
            title=title,
            title_ko=title_ko,
            url=url,
            source=source,
            keyword=keyword,
            battles=battles,
            weapons=weapons,
            stocks=stocks
        )
        
        return content
    
    def _format_content(self, title, title_ko, url, source, keyword, battles, weapons, stocks):
        """블로그 포스트 포맷"""
        
        post = f"""
{'='*60}
📰 블로그 콘텐츠 초안
{'='*60}

## 뉴스 소스
- 원문: {title}
- 번역: {title_ko or '(번역 없음)'}
- 출처: {source}
- 링크: {url}
- 키워드: {keyword}

{'─'*60}

## 제목 아이디어
1. "[{keyword.upper()}] 뉴스로 보는 전쟁사와 투자 기회"
2. "{title_ko or title[:30]} - 역사적 맥락과 수혜주 분석"
3. "오늘의 군사 뉴스: {keyword.upper()}가 주목받는 이유"

{'─'*60}

## 1부: 관련 전쟁사 🎖️ (Wikidata)

"""
        if battles:
            for i, b in enumerate(battles, 1):
                battle_name = b.get('battleLabel', 'N/A')
                war_name = b.get('warLabel', '')
                date = b.get('date', '')[:10] if b.get('date') else ''
                post += f"   {i}. {battle_name}"
                if war_name:
                    post += f" - {war_name}"
                if date:
                    post += f" ({date})"
                post += "\n"
        else:
            post += "   (관련 전투 데이터 없음)\n"
        
        post += f"""
{'─'*60}

## 2부: 무기/장비 분석 🔧 (Wikidata)

"""
        if weapons:
            for w in weapons:
                name = w.get('itemLabel', 'N/A')
                desc = w.get('description', '')[:100]
                country = w.get('countryLabel', '')
                post += f"   • {name}"
                if country:
                    post += f" ({country})"
                post += "\n"
                if desc:
                    post += f"     {desc}\n"
        else:
            post += "   (무기 정보 없음)\n"
        
        post += f"""
{'─'*60}

## 3부: 투자 포인트 📈

**관련 종목**
"""
        if stocks:
            for stock in stocks:
                post += f"   • {stock}\n"
        else:
            post += "   (관련 종목 없음)\n"
        
        post += f"""
{'─'*60}

## 작성 가이드

1. 뉴스 요약 (2-3문장)
2. 역사적 배경 (위 전투 참고하여 확장)
3. 무기/기술 분석 (스펙, 성능 비교)
4. 투자 시사점 (수혜주, 전망)
5. 결론 및 향후 전망

{'='*60}
"""
        return post
    
    def generate_from_news(self, article):
        return self.generate_content(article)
    
    def process_top_articles(self, limit=5):
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT id, title, title_ko, url, source, score 
            FROM rss_articles 
            WHERE is_used = 0
            ORDER BY score DESC, created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            article = {
                'id': row[0],
                'title': row[1],
                'title_ko': row[2],
                'url': row[3],
                'source': row[4],
                'score': row[5]
            }
            
            content = self.generate_content(article)
            if content:
                results.append({'article': article, 'content': content})
        
        return results
