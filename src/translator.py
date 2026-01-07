#!/usr/bin/env python3
"""DeepL 번역 모듈"""

import deepl
import logging

logger = logging.getLogger(__name__)


class Translator:
    """DeepL API를 사용한 번역"""
    
    def __init__(self, config):
        api_key = config['api_keys'].get('deepl', '')
        if not api_key:
            logger.warning("⚠️ DeepL API 키가 없습니다. 번역 비활성화.")
            self.translator = None
        else:
            self.translator = deepl.Translator(api_key)
            self._check_usage()
    
    def _check_usage(self):
        """API 사용량 확인"""
        try:
            usage = self.translator.get_usage()
            used = usage.character.count
            limit = usage.character.limit
            percent = (used / limit) * 100
            logger.info(f"📊 DeepL 사용량: {used:,} / {limit:,} ({percent:.1f}%)")
        except Exception as e:
            logger.error(f"사용량 확인 실패: {e}")
    
    def translate_title(self, title):
        """제목을 한글로 번역"""
        if not self.translator:
            return title
        
        try:
            result = self.translator.translate_text(
                title,
                source_lang="EN",
                target_lang="KO"
            )
            return result.text
        except Exception as e:
            logger.error(f"번역 실패: {e}")
            return title
    
    def translate_batch(self, titles):
        """여러 제목을 한 번에 번역 (API 호출 최소화)"""
        if not self.translator:
            return titles
        
        if not titles:
            return []
        
        try:
            results = self.translator.translate_text(
                titles,
                source_lang="EN",
                target_lang="KO"
            )
            return [r.text for r in results]
        except Exception as e:
            logger.error(f"배치 번역 실패: {e}")
            return titles
    
    def get_usage(self):
        """현재 사용량 반환"""
        if not self.translator:
            return None
        
        try:
            usage = self.translator.get_usage()
            return {
                'used': usage.character.count,
                'limit': usage.character.limit,
                'remaining': usage.character.limit - usage.character.count
            }
        except:
            return None
