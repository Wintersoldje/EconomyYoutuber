# 경제/부동산 뉴스 영상 제작기 (쇼츠 + 롱폼)

## 실행 (Docker 권장)
1) backend/.env.example 을 backend/.env 로 복사 후 필요한 키 입력
2) 실행
```bash
docker compose up --build
```

접속

프론트: http://localhost:5173

백: http://localhost:8000/api/health

로컬 실행 (Docker 없이)
Backend
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate  # Windows는 .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

Frontend
cd frontend
npm install
npm run dev

기능

숏폼/롱폼 대본 생성: RSS 수집 → (OpenAI 키 있으면) 고품질 대본 생성

숏폼/롱폼 영상 생성: 커버 이미지 + 자막(srt) + 오디오(기본 무음) 합성하여 mp4 생성

다음 단계(확장)

TTS 붙이기(한국어 자연스러운 남성 음성)

뉴스별로 여러 장 이미지 슬라이드 구성

기사 원문 이미지 사용 시 라이선스/출처표기 설계

배포 (Vercel + API 서버/컨테이너)


---

## 6) “Codex로 Git에 저장 + 테스트” 바로 실행 절차

너는 아래만 하면 돼.

### 1) 새 리포 만들기
GitHub에서 `news-video-maker` 같은 이름으로 새 repo 생성

### 2) Codex(또는 터미널)에서 초기화 & 푸시
(터미널 기준)
```bash
git clone <너의_repo_url>
cd news-video-maker
# 위 파일/폴더 그대로 생성(복붙)
git add .
git commit -m "Initial MVP: scripts + video generator web"
git push origin main
```

3) 실행

Docker 있으면:

docker compose up --build


브라우저에서 http://localhost:5173
 접속 → 버튼 4개 동작 확인.
