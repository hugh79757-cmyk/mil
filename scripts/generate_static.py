#!/usr/bin/env python3
"""정적 HTML 생성"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import yaml
from database import Database

# 설정 로드
config_file = Path(__file__).parent.parent / 'config.yaml'
with open(config_file, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

db_path = Path(__file__).parent.parent / config['database']['path']
db = Database(str(db_path))

# 데이터 조회
stats = db.get_statistics()
articles = db.get_latest_articles(limit=30)

# HTML 생성
html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="300">
    <title>Military News Aggregator - 밀리터리 뉴스</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{ 
            color: #2d3748; 
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #718096;
            font-size: 1.1em;
            margin-bottom: 30px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 15px;
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}
        .stat-card h3 {{ 
            font-size: 0.9em; 
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        .stat-card p {{ 
            font-size: 2.5em; 
            font-weight: bold;
        }}
        .articles {{
            margin-top: 40px;
        }}
        .articles h2 {{
            color: #2d3748;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        .article {{
            background: #f7fafc;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 12px;
            border-left: 4px solid #667eea;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .article:hover {{
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .article h3 {{ 
            color: #2d3748; 
            font-size: 1.15em; 
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        .article a {{ 
            color: #2d3748;
            text-decoration: none;
        }}
        .article a:hover {{
            color: #667eea;
        }}
        .meta {{ 
            color: #718096; 
            font-size: 0.85em;
            display: flex;
            gap: 15px;
            margin-top: 8px;
        }}
        .meta span {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .source-badge {{
            display: inline-block;
            padding: 4px 12px;
            background: #667eea;
            color: white;
            border-radius: 20px;
            font-size: 0.75em;
            font-weight: 600;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            color: #718096;
        }}
        .last-update {{
            background: #edf2f7;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            color: #4a5568;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
        .export-btn {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #667eea;
            color: white;
            padding: 15px 25px;
            border-radius: 50px;
            text-decoration: none;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: transform 0.2s;
            z-index: 999;
        }}
        .export-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }}
        #google_translate_element {{
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🪖 Military News Aggregator</h1>
        <p class="subtitle">실시간 밀리터리 뉴스 및 무기체계 정보 자동 수집 시스템</p>
        
        <div class="last-update">
            ⏰ 최종 업데이트: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>📰 총 수집 기사</h3>
                <p>{stats['total']}</p>
            </div>
            <div class="stat-card">
                <h3>🆕 오늘 수집</h3>
                <p>{stats['today']}</p>
            </div>
            <div class="stat-card">
                <h3>📡 RSS 소스</h3>
                <p>3개</p>
            </div>
            <div class="stat-card">
                <h3>📚 Wikipedia 모니터링</h3>
                <p>3개</p>
            </div>
        </div>
        
        <div class="articles">
            <h2>📰 최신 밀리터리 뉴스</h2>
'''

# 기사 목록
for i, article in enumerate(articles, 1):
    title = article[0]
    url = article[1]
    source = article[2]
    date = article[3]
    
    html += f'''
            <div class="article">
                <h3><a href="{url}" target="_blank">{title}</a></h3>
                <div class="meta">
                    <span class="source-badge">{source}</span>
                    <span>📅 {date}</span>
                </div>
            </div>
'''

html += '''
        </div>
        
        <div class="footer">
            <p>🔗 <a href="https://github.com/hugh79757-cmyk/mil" style="color: #667eea; text-decoration: none;">GitHub Repository</a></p>
            <p style="margin-top: 10px; font-size: 0.85em;">Powered by RSS Feeds + Wikipedia EventStreams</p>
        </div>
    </div>
    
    <!-- Export Button -->
    <a href="javascript:void(0)" class="export-btn" onclick="alert('터미널에서 실행: python3 scripts/export_for_blog.py')">📝 블로그용 내보내기</a>
    
    <!-- Google Translate -->
    <div id="google_translate_element"></div>
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
</body>
</html>
'''

# 파일 저장
output_file = Path(__file__).parent.parent / 'web' / 'index.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ HTML 생성 완료: {output_file}")
print(f"📊 통계: 총 {stats['total']}개 | 오늘 {stats['today']}개")
print(f"📰 기사: {len(articles)}개 표시")
