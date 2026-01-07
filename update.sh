#!/bin/bash
echo "�� 밀리터리 뉴스 업데이트 시작..."
echo "📅 $(date '+%Y-%m-%d %H:%M:%S')"

cd /Users/twinssn/Desktop/mil/mil
source venv/bin/activate

# HTML 생성
python3 scripts/generate_static.py

# Git 커밋 (변경사항 있을 때만)
if git diff --quiet web/index.html; then
    echo "✅ 변경사항 없음. 푸시 생략."
else
    git add web/index.html
    git commit -m "📊 자동 업데이트 $(date '+%Y-%m-%d %H:%M')"
    git push
    echo "✅ 배포 완료! https://mil-4a7.pages.dev/"
fi

echo "=" >> /Users/twinssn/Desktop/mil/mil/cron.log
