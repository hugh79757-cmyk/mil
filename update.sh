#!/bin/bash
# 뉴스 자동 수집 스크립트

cd ~/Desktop/mil/mil
source venv/bin/activate

echo "$(date): 뉴스 수집 시작" >> output.log

# 수집 실행 (30초 후 자동 종료)
timeout 30 python src/main.py >> output.log 2>&1

echo "$(date): 수집 완료" >> output.log
