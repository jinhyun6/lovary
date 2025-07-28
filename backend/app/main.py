from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import auth, diary, users, photos, anniversary
from app.core.config import settings
import os

app = FastAPI(title="Couple Diary API")

# CORS 설정 - 로컬과 프로덕션 URL 모두 포함
cors_origins = [
    "http://localhost:5173",  # 로컬 개발용
    "https://lovary.vercel.app"  # 프로덕션 (임시 하드코딩)
]

# 프로덕션 프론트엔드 URL 추가 (환경변수)
frontend_url = os.getenv("FRONTEND_URL", "").strip()
if frontend_url and frontend_url not in cors_origins:
    cors_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(diary.router, prefix="/api/diary", tags=["diary"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(photos.router, prefix="/api/photos", tags=["photos"])
app.include_router(anniversary.router, prefix="/api/anniversary", tags=["anniversary"])

# Mount static files for serving uploaded images
uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

@app.get("/")
def root():
    return {"message": "Couple Diary API"}