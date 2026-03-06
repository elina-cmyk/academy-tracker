# 📚 학원 알림장 — 배포 가이드

## 구조

```
academy-tracker/
├── backend/          ← FastAPI (Python)  → Railway 배포
│   ├── main.py
│   ├── requirements.txt
│   └── Procfile
└── frontend/         ← React             → Vercel 배포
    ├── src/
    ├── public/
    └── package.json
```

---

## 1단계 — GitHub에 코드 올리기

1. [github.com](https://github.com) 에서 새 레포지토리 만들기 (예: `academy-tracker`)
2. 터미널에서:
```bash
cd academy-tracker
git init
git add .
git commit -m "첫 커밋"
git remote add origin https://github.com/YOUR_ID/academy-tracker.git
git push -u origin main
```

---

## 2단계 — 백엔드 Railway 배포

1. [railway.app](https://railway.app) 접속 → GitHub 계정으로 로그인
2. **New Project** → **Deploy from GitHub repo** 선택
3. `academy-tracker` 레포 선택 → **backend** 폴더 선택
4. 배포 완료 후 **Settings → Domains** 에서 URL 복사
   - 예: `https://academy-tracker-backend.railway.app`

> Railway 무료 플랜: 월 500시간 무료

---

## 3단계 — 프론트엔드 Vercel 배포

1. [vercel.com](https://vercel.com) 접속 → GitHub 계정으로 로그인
2. **Add New Project** → `academy-tracker` 레포 선택
3. **Root Directory** 를 `frontend` 로 변경
4. **Environment Variables** 추가:
   - Key: `REACT_APP_API_URL`
   - Value: Railway에서 복사한 URL (예: `https://academy-tracker-backend.railway.app`)
5. **Deploy** 클릭

> 배포 완료 후 Vercel이 URL을 줍니다 (예: `https://academy-tracker.vercel.app`)

---

## 4단계 — CORS 설정 (중요!)

백엔드 `main.py` 에서 프론트엔드 URL로 변경:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://academy-tracker.vercel.app"],  # ← Vercel URL로 변경
    ...
)
```

변경 후 GitHub push → Railway 자동 재배포

---

## 로컬 개발 실행

### 백엔드
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# → http://localhost:8000
# → API 문서: http://localhost:8000/docs
```

### 프론트엔드
```bash
cd frontend
cp .env.example .env
# .env 에서 REACT_APP_API_URL=http://localhost:8000 으로 설정
npm install
npm start
# → http://localhost:3000
```

---

## 기능 요약

| 기능 | 설명 |
|------|------|
| 과목별 사이드바 | 수학/영어/과학/국어 + 직접 추가/수정/색상 변경 |
| 날짜별 그룹핑 | 최신순 정렬, 가장 최근 문자 자동 스크롤 |
| 문자 붙여넣기 | 학원 문자 복사 후 그대로 붙여넣기 |
| 숙제 체크박스 | 완료/미완료 토글 (서버 저장) |
| 성적 표시 | 점수/등급 입력 시 배지로 표시 |
| 학원명 태그 | 같은 과목 내에서 학원 구분 |

---

## 나중에 추가하기 좋은 기능

- **로그인**: FastAPI + JWT or Supabase Auth
- **이미지 업로드**: 문자 캡처 이미지 → AI 텍스트 추출 (Anthropic API)
- **푸시 알림**: 숙제 미완료 알림
- **통계**: 과목별 성적 그래프
