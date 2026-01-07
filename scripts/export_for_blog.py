#!/usr/bin/env python3
"""블로그 작성용 콘텐츠 추출"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import yaml
from database import Database
from datetime import datetime

# 설정 로드
config_file = Path(__file__).parent.parent / 'config.yaml'
with open(config_file, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

db_path = Path(__file__).parent.parent / config['database']['path']
db = Database(str(db_path))

# 데이터 조회
articles = db.get_latest_articles(limit=50)

# 카테고리별 분류
global_news = []
korea_news = []

cursor = db.conn.cursor()
for article in articles:
    cursor.execute("SELECT category FROM rss_articles WHERE url=?", (article[1],))
    result = cursor.fetchone()
    category = result[0] if result else 'global'
    
    article_dict = {
        'title': article[0],
        'url': article[1],
        'source': article[2],
        'date': article[3]
    }
    
    if category == 'korea':
        korea_news.append(article_dict)
    else:
        global_news.append(article_dict)

# 블로그 포스트 생성
today = datetime.now().strftime('%Y년 %m월 %d일')

blog_post = f'''# 밀리터리 뉴스 브리핑 - {today}

## 🌐 글로벌 국방 뉴스

'''

for i, article in enumerate(global_news[:10], 1):
    blog_post += f'''### {i}. {article['title']}

**출처**: {article['source']}  
**날짜**: {article['date']}  
**링크**: [{article['title']}]({article['url']})

---

'''

blog_post += '''
## 🇰🇷 한국 국방 뉴스

'''

for i, article in enumerate(korea_news[:5], 1):
    blog_post += f'''### {i}. {article['title']}

**출처**: {article['source']}  
**날짜**: {article['date']}  
**링크**: [{article['title']}]({article['url']})

---

'''

blog_post += f'''
## 📊 통계

- 총 수집 기사: {len(articles)}개
- 글로벌 뉴스: {len(global_news)}개
- 한국 뉴스: {len(korea_news)}개

---

*이 브리핑은 자동으로 생성되었습니다.*  
*출처: [Military News Aggregator](https://mil-4a7.pages.dev/)*
'''

# 파일 저장
output_file = Path(__file__).parent.parent / 'blog_posts' / f'briefing_{datetime.now().strftime("%Y%m%d")}.md'
output_file.parent.mkdir(exist_ok=True)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(blog_post)

print(f"✅ 블로그 포스트 생성: {output_file}")
print(f"\n📊 통계:")
print(f"   글로벌 뉴스: {len(global_news)}개")
print(f"   한국 뉴스: {len(korea_news)}개")
print(f"\n📝 파일을 열어서 블로그에 복사하세요:")
print(f"   cat {output_file}")
