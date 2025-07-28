# Couple Diary App

커플을 위한 일기 공유 애플리케이션

## 기능

- 📅 달력 기반 퍼즐 UI
- 📝 매일 일기 작성 (오전 6시까지 수정 가능)
- 📷 월별 사진 업로드
- 💑 파트너와 일기 공유
- 🎉 기념일 관리
- 🔔 웹 푸시 알림

## 기술 스택

### Frontend
- Vue 3 + TypeScript
- Tailwind CSS
- Vite

### Backend
- FastAPI
- PostgreSQL (Supabase)
- SQLAlchemy

## 배포 가이드

### 1. GitHub Secrets 설정

다음 시크릿을 GitHub 레포지토리에 추가하세요:

- `GCP_PROJECT_ID`: GCP 프로젝트 ID
- `GCP_SA_KEY`: 서비스 계정 JSON 키 (base64 인코딩)
  ```bash
  base64 -i service-account-key.json | tr -d '\n'
  ```
- `GCP_REGION`: 배포 리전 (예: asia-northeast3)
- `DATABASE_URL`: Supabase PostgreSQL 연결 문자열
- `SECRET_KEY`: JWT 비밀키 (32자 이상)
  ```bash
  openssl rand -hex 32
  ```
- `CORS_ORIGINS`: 허용할 프론트엔드 URL (쉼표로 구분)
  ```
  https://your-app.vercel.app,http://localhost:5173
  ```
- `FRONTEND_URL`: Vercel 프론트엔드 URL

### 2. GCP 설정

1. **필요한 API 활성화**:
   - Cloud Run API
   - Cloud Build API
   - Artifact Registry API

2. **Artifact Registry 저장소 생성**:
   ```bash
   gcloud artifacts repositories create couple-diary-images \
     --repository-format=docker \
     --location=asia-northeast3 \
     --description="Docker images for couple diary app"
   ```

3. **서비스 계정 권한**:
   - Cloud Run 관리자
   - 서비스 계정 사용자
   - Cloud Build 편집자
   - Artifact Registry 작성자

### 3. Vercel 환경 변수

Vercel 대시보드에서 다음 환경 변수를 설정하세요:

- `VITE_API_URL`: Cloud Run 백엔드 URL (배포 후 확인)

### 4. 배포

1. **백엔드 배포**: main 브랜치에 푸시하면 GitHub Actions가 자동으로 Cloud Run에 배포
2. **프론트엔드 배포**: Vercel이 자동으로 감지하여 배포

### 5. 배포 후 설정

1. Cloud Run 서비스 URL 확인
2. Vercel 환경 변수에 `VITE_API_URL` 업데이트
3. 필요시 Cloud Run의 CORS_ORIGINS 환경 변수 업데이트

## 로컬 개발

### 사전 요구사항

- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### 실행 방법

1. 환경 변수 설정:
   ```bash
   cp backend/.env.example backend/.env
   # .env 파일 수정
   ```

2. Docker Compose로 실행:
   ```bash
   docker-compose up
   ```

3. 접속:
   - Frontend: http://localhost:5173
   - Backend: http://localhost:8000

## 환경 변수

### Backend
- `DATABASE_URL`: PostgreSQL 연결 문자열
- `SECRET_KEY`: JWT 서명 키
- `ALGORITHM`: JWT 알고리즘 (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 토큰 만료 시간
- `CORS_ORIGINS`: 허용할 프론트엔드 URL
- `PORT`: 서버 포트 (Cloud Run 자동 설정)

### Frontend
- `VITE_API_URL`: 백엔드 API URL