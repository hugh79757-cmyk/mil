#!/usr/bin/env python3
"""콘텐츠 필터링 모듈"""

import logging

logger = logging.getLogger(__name__)


class ContentFilter:
    """밀리터리 키워드 기반 필터링"""
    
    def __init__(self, config):
        self.config = config
        self.high_priority = config['filters']['high_priority']
        self.medium_priority = config['filters']['medium_priority']
        self.exclude = config['filters'].get('exclude', [])
        logger.info("콘텐츠 필터 초기화")
    
    def is_military_related(self, text):
        """밀리터리 관련 여부 판단"""
        text_lower = text.lower()
        
        # 제외 키워드 체크
        for keyword in self.exclude:
            if keyword.lower() in text_lower:
                return False
        
        # 고우선순위 키워드
        for keyword in self.high_priority:
            if keyword.lower() in text_lower:
                return True
        
        # 중간우선순위 키워드
        for keyword in self.medium_priority:
            if keyword.lower() in text_lower:
                return True
        
        return False
    
    def calculate_score(self, article):
        """기사 중요도 점수 계산"""
        text = f"{article['title']} {article.get('summary', '')}"
        text_lower = text.lower()
        
        score = 0
        
        # 고우선순위 키워드: +10점
        for keyword in self.high_priority:
            if keyword.lower() in text_lower:
                score += 10
        
        # 중간우선순위 키워드: +5점
        for keyword in self.medium_priority:
            if keyword.lower() in text_lower:
                score += 5
        
        return score
    
    def filter_articles(self, articles):
        """기사 필터링 및 점수 부여"""
        filtered = []
        
        for article in articles:
            text = f"{article['title']} {article.get('summary', '')}"
            
            if self.is_military_related(text):
                article['score'] = self.calculate_score(article)
                filtered.append(article)
        
        # 점수 순으로 정렬
        filtered.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"필터링 결과: {len(articles)}개 → {len(filtered)}개")
        return filtered
