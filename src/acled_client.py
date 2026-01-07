#!/usr/bin/env python3
"""ACLED 분쟁 데이터 클라이언트"""

import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ACLEDClient:
    """ACLED API 클라이언트 (실시간 분쟁 데이터)"""
    
    def __init__(self, config=None):
        # ACLED API는 무료 등록 후 키/이메일 필요
        # 없으면 제한된 데이터만 접근 가능
        self.base_url = "https://api.acleddata.com/acled/read"
        self.api_key = ""
        self.email = ""
        
        if config and 'api_keys' in config:
            self.api_key = config['api_keys'].get('acled_key', '')
            self.email = config['api_keys'].get('acled_email', '')
        
        logger.info("✅ ACLED 클라이언트 초기화")
    
    def get_recent_conflicts(self, days=7, limit=100):
        """최근 분쟁 이벤트 조회"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "event_date": f"{start_date.strftime('%Y-%m-%d')}|{end_date.strftime('%Y-%m-%d')}",
            "event_date_where": "BETWEEN",
            "limit": limit
        }
        
        if self.api_key and self.email:
            params["key"] = self.api_key
            params["email"] = self.email
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.error(f"ACLED API 오류: {e}")
            return []
    
    def get_conflicts_by_country(self, country, days=30, limit=50):
        """국가별 분쟁 이벤트"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "country": country,
            "event_date": f"{start_date.strftime('%Y-%m-%d')}|{end_date.strftime('%Y-%m-%d')}",
            "event_date_where": "BETWEEN",
            "limit": limit
        }
        
        if self.api_key and self.email:
            params["key"] = self.api_key
            params["email"] = self.email
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.error(f"ACLED API 오류: {e}")
            return []
    
    def get_conflicts_by_region(self, region, days=30, limit=50):
        """지역별 분쟁 이벤트"""
        # 지역: Middle East, Europe, Asia, Africa 등
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "region": region,
            "event_date": f"{start_date.strftime('%Y-%m-%d')}|{end_date.strftime('%Y-%m-%d')}",
            "event_date_where": "BETWEEN",
            "limit": limit
        }
        
        if self.api_key and self.email:
            params["key"] = self.api_key
            params["email"] = self.email
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.error(f"ACLED API 오류: {e}")
            return []
    
    def get_ukraine_conflicts(self, days=7):
        """우크라이나 분쟁 현황"""
        return self.get_conflicts_by_country("Ukraine", days=days, limit=100)
    
    def get_middle_east_conflicts(self, days=7):
        """중동 분쟁 현황"""
        return self.get_conflicts_by_region("Middle East", days=days, limit=100)
    
    def summarize_conflicts(self, conflicts):
        """분쟁 데이터 요약"""
        if not conflicts:
            return None
        
        summary = {
            "total_events": len(conflicts),
            "by_type": {},
            "by_country": {},
            "fatalities": 0,
            "recent_events": []
        }
        
        for event in conflicts:
            # 이벤트 타입별
            event_type = event.get("event_type", "Unknown")
            summary["by_type"][event_type] = summary["by_type"].get(event_type, 0) + 1
            
            # 국가별
            country = event.get("country", "Unknown")
            summary["by_country"][country] = summary["by_country"].get(country, 0) + 1
            
            # 사망자 수
            fatalities = event.get("fatalities", 0)
            if fatalities:
                summary["fatalities"] += int(fatalities)
        
        # 최근 5개 이벤트
        summary["recent_events"] = conflicts[:5]
        
        return summary
    
    def format_for_blog(self, conflicts):
        """블로그용 포맷"""
        if not conflicts:
            return "분쟁 데이터를 가져올 수 없습니다."
        
        output = []
        for event in conflicts[:10]:
            date = event.get("event_date", "")
            country = event.get("country", "")
            location = event.get("location", "")
            event_type = event.get("event_type", "")
            fatalities = event.get("fatalities", 0)
            notes = event.get("notes", "")[:200]
            
            output.append(f"""
📍 {country} - {location}
   날짜: {date}
   유형: {event_type}
   사망자: {fatalities}명
   내용: {notes}...
""")
        
        return "\n".join(output)
