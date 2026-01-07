#!/usr/bin/env python3
"""Wikidata 전쟁/전투 데이터 클라이언트"""

import requests
import logging

logger = logging.getLogger(__name__)

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"


class WikidataClient:
    """Wikidata SPARQL 쿼리 클라이언트"""
    
    def __init__(self):
        self.endpoint = WIKIDATA_ENDPOINT
        self.headers = {
            "User-Agent": "MilitaryNewsBlog/1.0",
            "Accept": "application/json"
        }
        logger.info("✅ Wikidata 클라이언트 초기화")
    
    def query(self, sparql):
        """SPARQL 쿼리 실행"""
        try:
            response = requests.get(
                self.endpoint,
                params={"query": sparql, "format": "json"},
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["results"]["bindings"]
        except Exception as e:
            logger.error(f"Wikidata 쿼리 실패: {e}")
            return []
    
    def get_battles_by_weapon(self, weapon_name):
        """무기가 사용된 전투 검색"""
        sparql = f'''
        SELECT ?battle ?battleLabel ?date ?locationLabel ?war ?warLabel WHERE {{
          ?battle wdt:P31 wd:Q178561.
          ?battle rdfs:label ?label.
          FILTER(LANG(?label) = "en")
          FILTER(CONTAINS(LCASE(?label), "{weapon_name.lower()}"))
          OPTIONAL {{ ?battle wdt:P585 ?date. }}
          OPTIONAL {{ ?battle wdt:P276 ?location. }}
          OPTIONAL {{ ?battle wdt:P361 ?war. }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,ko". }}
        }}
        LIMIT 20
        '''
        return self.query(sparql)
    
    def get_battles_by_country(self, country_code):
        """국가가 참전한 전투 검색"""
        # 국가 코드 매핑
        country_map = {
            "korea": "Q884",      # 대한민국
            "us": "Q30",          # 미국
            "russia": "Q159",     # 러시아
            "china": "Q148",      # 중국
            "japan": "Q17",       # 일본
            "germany": "Q183",    # 독일
            "poland": "Q36"       # 폴란드
        }
        
        qid = country_map.get(country_code.lower(), "Q884")
        
        sparql = f'''
        SELECT ?battle ?battleLabel ?date ?warLabel WHERE {{
          ?battle wdt:P31 wd:Q178561.
          ?battle wdt:P710 wd:{qid}.
          OPTIONAL {{ ?battle wdt:P585 ?date. }}
          OPTIONAL {{ ?battle wdt:P361 ?war. }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,ko". }}
        }}
        ORDER BY DESC(?date)
        LIMIT 30
        '''
        return self.query(sparql)
    
    def get_wars_by_period(self, start_year, end_year):
        """특정 기간의 전쟁 검색"""
        sparql = f'''
        SELECT ?war ?warLabel ?startDate ?endDate ?casualties WHERE {{
          ?war wdt:P31 wd:Q198.
          ?war wdt:P580 ?startDate.
          FILTER(YEAR(?startDate) >= {start_year} && YEAR(?startDate) <= {end_year})
          OPTIONAL {{ ?war wdt:P582 ?endDate. }}
          OPTIONAL {{ ?war wdt:P1120 ?casualties. }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,ko". }}
        }}
        ORDER BY ?startDate
        LIMIT 50
        '''
        return self.query(sparql)
    
    def get_weapon_info(self, weapon_name):
        """무기 정보 검색"""
        sparql = f'''
        SELECT ?item ?itemLabel ?countryLabel ?serviceDate ?description WHERE {{
          ?item rdfs:label ?label.
          FILTER(LANG(?label) = "en")
          FILTER(CONTAINS(LCASE(?label), "{weapon_name.lower()}"))
          ?item wdt:P31/wdt:P279* wd:Q728.
          OPTIONAL {{ ?item wdt:P495 ?country. }}
          OPTIONAL {{ ?item wdt:P729 ?serviceDate. }}
          OPTIONAL {{ ?item schema:description ?description. FILTER(LANG(?description) = "en") }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,ko". }}
        }}
        LIMIT 10
        '''
        return self.query(sparql)
    
    def get_tank_battles(self):
        """전차전 목록"""
        sparql = '''
        SELECT ?battle ?battleLabel ?date ?warLabel ?locationLabel WHERE {
          ?battle wdt:P31 wd:Q178561.
          ?battle rdfs:label ?label.
          FILTER(LANG(?label) = "en")
          FILTER(CONTAINS(LCASE(?label), "tank") || CONTAINS(LCASE(?label), "armour") || CONTAINS(LCASE(?label), "armor"))
          OPTIONAL { ?battle wdt:P585 ?date. }
          OPTIONAL { ?battle wdt:P361 ?war. }
          OPTIONAL { ?battle wdt:P276 ?location. }
          SERVICE wikibase:label { bd:serviceParam wikibase:language "en,ko". }
        }
        ORDER BY DESC(?date)
        LIMIT 30
        '''
        return self.query(sparql)
    
    def get_air_battles(self):
        """공중전 목록"""
        sparql = '''
        SELECT ?battle ?battleLabel ?date ?warLabel WHERE {
          ?battle wdt:P31 wd:Q178561.
          ?battle rdfs:label ?label.
          FILTER(LANG(?label) = "en")
          FILTER(CONTAINS(LCASE(?label), "air") || CONTAINS(LCASE(?label), "aerial"))
          OPTIONAL { ?battle wdt:P585 ?date. }
          OPTIONAL { ?battle wdt:P361 ?war. }
          SERVICE wikibase:label { bd:serviceParam wikibase:language "en,ko". }
        }
        ORDER BY DESC(?date)
        LIMIT 30
        '''
        return self.query(sparql)
    
    def search_military_history(self, keyword):
        """군사 역사 통합 검색"""
        sparql = f'''
        SELECT ?item ?itemLabel ?typeLabel ?date ?description WHERE {{
          ?item rdfs:label ?label.
          FILTER(LANG(?label) = "en")
          FILTER(CONTAINS(LCASE(?label), "{keyword.lower()}"))
          ?item wdt:P31 ?type.
          FILTER(?type IN (wd:Q178561, wd:Q198, wd:Q728, wd:Q4421))
          OPTIONAL {{ ?item wdt:P585 ?date. }}
          OPTIONAL {{ ?item schema:description ?description. FILTER(LANG(?description) = "en") }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,ko". }}
        }}
        LIMIT 20
        '''
        return self.query(sparql)
    
    def format_results(self, results):
        """결과를 보기 좋게 포맷"""
        formatted = []
        for r in results:
            item = {}
            for key, value in r.items():
                item[key] = value.get("value", "")
            formatted.append(item)
        return formatted
