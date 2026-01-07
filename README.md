# 🪖 Military News Aggregator

실시간 밀리터리 뉴스 및 무기체계 정보 자동 수집 시스템

## 🎯 주요 기능

- **실시간 RSS 수집**: Defense One, Military Times, 연합뉴스 등
- **Wikipedia 실시간 모니터링**: EventStreams를 통한 무기체계 업데이트 감지
- **뉴스 API 통합**: NewsData.io로 글로벌 밀리터리 뉴스 수집
- **스마트 필터링**: 밀리터리/국방 키워드 기반 자동 분류
- **자동 알림**: Slack/이메일로 중요 뉴스 실시간 알림

## 📊 데이터 소스

### RSS 피드
- Defense One: https://www.defenseone.com/rss/all/
- Military Times: https://www.militarytimes.com/arc/outboundfeeds/rss/
- 연합뉴스 (영문): https://en.yna.co.kr/RSS/national.xml
- Breaking Defense: https://breakingdefense.com/feed/

### API
- Wikipedia EventStreams (실시간)
- NewsData.io API
- 국방부 공공데이터 Open API

## 🚀 빠른 시작

### 1. 설치

```bash
git clone https://github.com/hugh79757-cmyk/mil.git
cd mil
pip install -r requirements.txt

