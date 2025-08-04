from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import auth, diary, users, photos, anniversary
from app.core.config import settings
import os

app = FastAPI(title="Lovary API")

# CORS 설정 - 로컬과 프로덕션 URL 모두 포함
cors_origins = ["http://localhost:5173", "https://lovary.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    """Log 422 errors for debugging"""
    print(f"422 Error - Path: {request.url.path}")
    print(f"422 Error - Method: {request.method}")
    print(f"422 Error - Headers: {dict(request.headers)}")
    if request.method == "POST":
        try:
            body = await request.body()
            print(f"422 Error - Body: {body[:500] if body else 'No body'}")  # First 500 chars
        except:
            pass
    print(f"422 Error - Exception: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(diary.router, prefix="/api/diary", tags=["diary"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(photos.router, prefix="/api/photos", tags=["photos"])
app.include_router(anniversary.router, prefix="/api/anniversary", tags=["anniversary"])

@app.get("/")
def root():
    return {"message": "Lovary API"}

@app.get("/health")
def health_check():
    from app.db.database import SessionLocal
    from app.models.user import User
    from sqlalchemy import text
    try:
        # Test database connection
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        
        # Count users
        user_count = db.query(User).count()
        
        # Get first user email for debugging (masked)
        first_user = db.query(User).first()
        first_user_email = first_user.email[:3] + "***" if first_user else "No users"
        
        db.close()
        return {
            "status": "healthy", 
            "database": "connected",
            "user_count": user_count,
            "first_user_email": first_user_email,
            "database_url": os.getenv("DATABASE_URL", "").split("@")[-1] if "@" in os.getenv("DATABASE_URL", "") else "not set",
            "supabase_configured": bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"))
        }
    except Exception as e:
        return {"status": "unhealthy", "database": "error", "detail": str(e)}