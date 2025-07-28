from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import auth, diary, users, photos, anniversary
from app.core.config import settings
import os

app = FastAPI(title="Couple Diary API")

# CORS 설정 - 환경변수에서 가져오기
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
# 빈 문자열 제거
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

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