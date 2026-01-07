#!/usr/bin/env python3
"""정적 HTML 생성 (Cloudflare Pages용)"""

import json
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import Database

# 설정 로드
config_file = Path(__file__).parent.parent / 'config.yaml'
with open(config_file, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# DB 연결
db_path = Path(__file__).parent.parent / config['database']['path']
db = Database(str(db_path))

# 기사 가져오기
cursor = db.conn.cursor()
cursor.execute('''
    SELECT id, title, title_ko, url, source, score, created_at 
    FROM rss_articles 
    ORDER BY created_at DESC 
    LIMIT 50
''')

articles = []
for row in cursor.fetchall():
    articles.append({
        'id': row[0],
        'title': row[1],
        'title_ko': row[2],
        'url': row[3],
        'source': row[4],
        'score': row[5],
        'created_at': row[6]
    })

# HTML 템플릿 읽기
html_path = Path(__file__).parent.parent / 'web' / 'index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 기사 데이터 삽입
articles_json = json.dumps(articles, ensure_ascii=False)
html = html.replace('ARTICLES_DATA', articles_json)

# 저장
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ 정적 페이지 생성 완료: {len(articles)}개 기사")
