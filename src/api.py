#!/usr/bin/env python3
"""Flask API 서버"""

from flask import Flask, jsonify, render_template_string
from pathlib import Path
import yaml
from database import Database

app = Flask(__name__)

# 설정 로드
config_file = Path(__file__).parent.parent / 'config.yaml'
with open(config_file, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

db_path = Path(__file__).parent.parent / config['database']['path']
db = Database(str(db_path))


@app.route('/api/articles')
def get_articles():
    """최신 기사 API"""
    articles = db.get_latest_articles(limit=30)
    return jsonify([{
        'title': a[0],
        'url': a[1],
        'source': a[2],
        'created_at': a[3]
    } for a in articles])


@app.route('/api/stats')
def get_stats():
    """통계 API"""
    stats = db.get_statistics()
    return jsonify(stats)


@app.route('/')
def index():
    """메인 페이지"""
    stats = db.get_statistics()
    articles = db.get_latest_articles(limit=20)
    
    html = '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Military News Aggregator</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 { color: #2d3748; margin-bottom: 10px; }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .stat-card {
                background: #f7fafc;
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            .stat-card h3 { color: #4a5568; font-size: 0.9em; margin-bottom: 10px; }
            .stat-card p { color: #2d3748; font-size: 2em; font-weight: bold; }
            .articles {
                margin-top: 40px;
            }
            .article {
                background: #edf2f7;
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 8px;
                border-left: 3px solid #667eea;
            }
            .article h3 { color: #2d3748; font-size: 1.1em; margin-bottom: 5px; }
            .article .meta { color: #718096; font-size: 0.85em; }
            .article a { color: #667eea; text-decoration: none; }
            .article a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🪖 Military News Aggregator</h1>
            <p style="color: #718096; margin-bottom: 20px;">실시간 밀리터리 뉴스 수집 시스템</p>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>📰 총 수집</h3>
                    <p>{{ stats['total'] }}</p>
                </div>
                <div class="stat-card">
                    <h3>🆕 오늘 수집</h3>
                    <p>{{ stats['today'] }}</p>
                </div>
                <div class="stat-card">
                    <h3>📡 RSS 소스</h3>
                    <p>3개</p>
                </div>
                <div class="stat-card">
                    <h3>📚 Wikipedia</h3>
                    <p>3개</p>
                </div>
            </div>
            
            <div class="articles">
                <h2 style="color: #2d3748; margin-bottom: 20px;">최신 기사</h2>
                {% for article in articles %}
                <div class="article">
                    <h3><a href="{{ article[1] }}" target="_blank">{{ article[0] }}</a></h3>
                    <div class="meta">
                        <span>{{ article[2] }}</span> • 
                        <span>{{ article[3] }}</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    '''
    
    from jinja2 import Template
    template = Template(html)
    return template.render(stats=stats, articles=articles)


if __name__ == '__main__':
    print("🌐 Flask 서버 시작: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
