#!/usr/bin/env python3
"""HTML에 구글 번역 추가"""

from pathlib import Path

html_file = Path(__file__).parent.parent / 'web' / 'index.html'

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 구글 번역 스크립트 추가
translation_script = '''
    <!-- Google Translate -->
    <div id="google_translate_element" style="position: fixed; top: 20px; right: 20px; z-index: 1000; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);"></div>
    <script type="text/javascript">
        function googleTranslateElementInit() {
            new google.translate.TranslateElement({
                pageLanguage: 'ko',
                includedLanguages: 'ko,en,ja,zh-CN',
                layout: google.translate.TranslateElement.InlineLayout.SIMPLE
            }, 'google_translate_element');
        }
    </script>
    <script type="text/javascript" src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
'''

# </body> 태그 앞에 삽입
content = content.replace('</body>', translation_script + '\n</body>')

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 구글 번역 추가 완료!")
