#!/usr/bin/env python3
"""구글 번역 언어 수정"""

from pathlib import Path

html_file = Path(__file__).parent.parent / 'web' / 'index.html'

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 기존 번역 설정 찾기
old_config = "includedLanguages: 'ko,en,ja,zh-CN'"
new_config = "includedLanguages: 'en,ja,zh-CN,zh-TW,ko'"

# 언어 순서 변경 (영어, 일본어, 중국어 간체, 중국어 번체, 한국어)
content = content.replace(old_config, new_config)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 번역 언어 수정 완료!")
