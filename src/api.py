#!/usr/bin/env python3
"""웹 대시보드 API 서버 (Wikidata 연동)"""

from flask import Flask, jsonify, render_template_string, request
import yaml
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from database import Database
from content_generator import ContentGenerator
from wikidata_client import WikidataClient

app = Flask(__name__)

# 설정 로드
config_file = Path(__file__).parent.parent / 'config.yaml'
with open(config_file, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# DB 연결
db_path = Path(__file__).parent.parent / config['database']['path']
db = Database(str(db_path))

# 모듈 초기화
generator = ContentGenerator(config, db)
wikidata = WikidataClient()

# 블로그 출력 폴더
output_dir = Path(__file__).parent.parent / 'blog_posts'
output_dir.mkdir(exist_ok=True)


@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/articles')
def get_articles():
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
    
    return jsonify(articles)


@app.route('/api/stats')
def get_stats():
    stats = db.get_statistics()
    return jsonify(stats)


@app.route('/api/generate/<int:article_id>')
def generate_content(article_id):
    cursor = db.conn.cursor()
    cursor.execute('''
        SELECT id, title, title_ko, url, source, score 
        FROM rss_articles 
        WHERE id = ?
    ''', (article_id,))
    
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Article not found'}), 404
    
    article = {
        'id': row[0],
        'title': row[1],
        'title_ko': row[2],
        'url': row[3],
        'source': row[4],
        'score': row[5]
    }
    
    content = generator.generate_content(article)
    
    return jsonify({
        'article': article,
        'content': content,
        'has_content': content is not None
    })


@app.route('/api/wikidata/battles/<country>')
def get_battles(country):
    """국가별 전투 검색"""
    results = wikidata.get_battles_by_country(country)
    formatted = wikidata.format_results(results)
    return jsonify(formatted[:10])


@app.route('/api/wikidata/tanks')
def get_tank_battles():
    """전차전 목록"""
    results = wikidata.get_tank_battles()
    formatted = wikidata.format_results(results)
    return jsonify(formatted[:10])


@app.route('/api/wikidata/air')
def get_air_battles():
    """공중전 목록"""
    results = wikidata.get_air_battles()
    formatted = wikidata.format_results(results)
    return jsonify(formatted[:10])


@app.route('/api/wikidata/search/<keyword>')
def search_wikidata(keyword):
    """키워드 검색"""
    results = wikidata.search_military_history(keyword)
    formatted = wikidata.format_results(results)
    return jsonify(formatted[:10])


@app.route('/api/export/<int:article_id>')
def export_markdown(article_id):
    """마크다운 파일로 내보내기"""
    cursor = db.conn.cursor()
    cursor.execute('''
        SELECT id, title, title_ko, url, source, score 
        FROM rss_articles 
        WHERE id = ?
    ''', (article_id,))
    
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Article not found'}), 404
    
    article = {
        'id': row[0],
        'title': row[1],
        'title_ko': row[2],
        'url': row[3],
        'source': row[4],
        'score': row[5]
    }
    
    content = generator.generate_content(article)
    if not content:
        return jsonify({'error': 'No content generated'}), 400
    
    # 파일명 생성
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in article['title'][:50])
    filename = f"{timestamp}_{safe_title}.md"
    filepath = output_dir / filename
    
    # 마크다운 형식으로 변환
    markdown_content = content.replace('═', '=').replace('─', '-')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    # 사용됨 표시
    cursor.execute('UPDATE rss_articles SET is_used = 1 WHERE id = ?', (article_id,))
    db.conn.commit()
    
    return jsonify({
        'success': True,
        'filename': filename,
        'filepath': str(filepath)
    })


DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Military News Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            line-height: 1.6;
        }
        .container { max-width: 1600px; margin: 0 auto; padding: 20px; }
        header {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            border: 1px solid #333;
        }
        h1 {
            font-size: 2em;
            margin-bottom: 8px;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stats { display: flex; gap: 15px; margin-top: 15px; }
        .stat-box {
            background: rgba(255,255,255,0.05);
            padding: 12px 20px;
            border-radius: 10px;
            border: 1px solid #333;
        }
        .stat-number { font-size: 1.8em; font-weight: bold; color: #00d4ff; }
        .stat-label { color: #888; font-size: 0.85em; }
        
        .main-content { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
        .panel {
            background: #111;
            border-radius: 15px;
            padding: 20px;
            border: 1px solid #222;
        }
        .panel h2 {
            color: #fff;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #333;
            font-size: 1.1em;
        }
        
        .article-list { max-height: 500px; overflow-y: auto; }
        .article-item {
            background: #1a1a1a;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.3s;
            border: 1px solid #222;
        }
        .article-item:hover {
            background: #252525;
            border-color: #00d4ff;
        }
        .article-item.selected { border-color: #7b2cbf; background: #1a1a2e; }
        .article-title { font-weight: 600; margin-bottom: 4px; color: #fff; font-size: 0.9em; }
        .article-title-ko { color: #00d4ff; font-size: 0.85em; margin-bottom: 6px; }
        .article-meta { display: flex; gap: 10px; font-size: 0.75em; color: #666; }
        .source { background: #2a2a2a; padding: 2px 6px; border-radius: 4px; color: #888; }
        .score { color: #ffd700; }
        
        .content-output {
            background: #0a0a0a;
            padding: 15px;
            border-radius: 10px;
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 0.8em;
            max-height: 500px;
            overflow-y: auto;
            border: 1px solid #222;
        }
        
        .wikidata-section { margin-top: 15px; }
        .wikidata-item {
            background: #1a1a1a;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 8px;
            border-left: 3px solid #7b2cbf;
        }
        .wikidata-title { color: #fff; font-weight: 600; font-size: 0.9em; }
        .wikidata-meta { color: #888; font-size: 0.8em; margin-top: 4px; }
        
        .btn {
            background: linear-gradient(135deg, #00d4ff, #7b2cbf);
            color: #fff;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
            margin-right: 8px;
            margin-top: 10px;
        }
        .btn:hover { opacity: 0.8; }
        .btn-export { background: linear-gradient(135deg, #00c853, #00bfa5); }
        
        .tabs { display: flex; gap: 10px; margin-bottom: 15px; }
        .tab {
            padding: 8px 16px;
            background: #222;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85em;
        }
        .tab.active { background: #7b2cbf; }
        .tab:hover { background: #333; }
        .tab.active:hover { background: #7b2cbf; }
        
        .no-content { color: #666; text-align: center; padding: 30px; }
        
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #111; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎖️ Military News Dashboard</h1>
            <p>전쟁사 × 무기 분석 × 방산주 투자 콘텐츠 생성기</p>
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-number" id="total-count">-</div>
                    <div class="stat-label">총 기사</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number" id="today-count">-</div>
                    <div class="stat-label">오늘 수집</div>
                </div>
            </div>
        </header>
        
        <div class="main-content">
            <div class="panel">
                <h2>📰 최신 기사</h2>
                <div class="article-list" id="article-list">
                    <div class="no-content">로딩 중...</div>
                </div>
            </div>
            
            <div class="panel">
                <h2>📝 콘텐츠 초안</h2>
                <div id="content-actions"></div>
                <div class="content-output" id="content-output">
                    <div class="no-content">
                        왼쪽에서 기사를 선택하세요
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <h2>🌍 전쟁사 데이터 (Wikidata)</h2>
                <div class="tabs">
                    <div class="tab active" onclick="loadWikidata('korea')">한국</div>
                    <div class="tab" onclick="loadWikidata('us')">미국</div>
                    <div class="tab" onclick="loadWikidata('tanks')">전차전</div>
                    <div class="tab" onclick="loadWikidata('air')">공중전</div>
                </div>
                <div class="wikidata-section" id="wikidata-list">
                    <div class="no-content">로딩 중...</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let selectedArticleId = null;
        
        // 통계 로드
        fetch('/api/stats')
            .then(r => r.json())
            .then(data => {
                document.getElementById('total-count').textContent = data.total;
                document.getElementById('today-count').textContent = data.today;
            });
        
        // 기사 목록 로드
        fetch('/api/articles')
            .then(r => r.json())
            .then(articles => {
                const list = document.getElementById('article-list');
                list.innerHTML = '';
                articles.forEach(article => {
                    const item = document.createElement('div');
                    item.className = 'article-item';
                    item.innerHTML = `
                        <div class="article-title">${article.title.substring(0, 60)}...</div>
                        ${article.title_ko ? `<div class="article-title-ko">${article.title_ko.substring(0, 50)}...</div>` : ''}
                        <div class="article-meta">
                            <span class="source">${article.source}</span>
                            <span class="score">⭐ ${article.score}점</span>
                        </div>
                    `;
                    item.onclick = () => selectArticle(article.id, item);
                    list.appendChild(item);
                });
            });
        
        // 기사 선택
        function selectArticle(articleId, element) {
            selectedArticleId = articleId;
            document.querySelectorAll('.article-item').forEach(i => i.classList.remove('selected'));
            element.classList.add('selected');
            generateContent(articleId);
        }
        
        // 콘텐츠 생성
        function generateContent(articleId) {
            const output = document.getElementById('content-output');
            const actions = document.getElementById('content-actions');
            output.innerHTML = '<div class="no-content">생성 중...</div>';
            actions.innerHTML = '';
            
            fetch('/api/generate/' + articleId)
                .then(r => r.json())
                .then(data => {
                    if (data.content) {
                        output.textContent = data.content;
                        actions.innerHTML = `
                            <button class="btn btn-export" onclick="exportMarkdown(${articleId})">📥 마크다운 저장</button>
                        `;
                    } else {
                        output.innerHTML = '<div class="no-content">❌ 매칭 키워드 없음</div>';
                    }
                });
        }
        
        // 마크다운 내보내기
        function exportMarkdown(articleId) {
            fetch('/api/export/' + articleId)
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        alert('저장 완료!\\n' + data.filename);
                    } else {
                        alert('저장 실패: ' + data.error);
                    }
                });
        }
        
        // Wikidata 로드
        function loadWikidata(type) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            
            const list = document.getElementById('wikidata-list');
            list.innerHTML = '<div class="no-content">로딩 중...</div>';
            
            let url = '';
            if (type === 'tanks') url = '/api/wikidata/tanks';
            else if (type === 'air') url = '/api/wikidata/air';
            else url = '/api/wikidata/battles/' + type;
            
            fetch(url)
                .then(r => r.json())
                .then(battles => {
                    list.innerHTML = '';
                    if (battles.length === 0) {
                        list.innerHTML = '<div class="no-content">데이터 없음</div>';
                        return;
                    }
                    battles.forEach(b => {
                        const item = document.createElement('div');
                        item.className = 'wikidata-item';
                        const date = b.date ? b.date.substring(0, 10) : '';
                        item.innerHTML = `
                            <div class="wikidata-title">${b.battleLabel || b.itemLabel || 'N/A'}</div>
                            <div class="wikidata-meta">
                                ${b.warLabel ? b.warLabel + ' · ' : ''}${date}
                            </div>
                        `;
                        list.appendChild(item);
                    });
                });
        }
        
        // 초기 로드
        loadWikidata('korea');
    </script>
</body>
</html>
'''


if __name__ == '__main__':
    print("=" * 50)
    print("🎖️ Military News Dashboard")
    print("http://127.0.0.1:8080")
    print("종료: Ctrl+C")
    print("=" * 50)
    app.run(host='127.0.0.1', port=8080, debug=False)
