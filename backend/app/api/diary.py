from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import os
from app.db.database import get_db
from app.models.diary import Diary as DiaryModel
from app.models.diary_photo import DiaryPhoto
from app.models.user import User
from app.schemas.diary import DiaryCreate, Diary, DiaryUpdate
from app.api.deps import get_current_user
from app.services.push_notification import send_push_notification

router = APIRouter()

@router.post("/", response_model=Diary)
async def create_diary(
    title: str = Form(...),
    content: str = Form(...),
    photos: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    now = datetime.utcnow()
    today = now.date()
    
    # Check if still within writing time (until 6 AM next day)
    cutoff_time = datetime.combine(today, datetime.min.time()).replace(hour=6)
    if now.hour < 6:
        # If it's before 6 AM, we're writing for yesterday
        today = (now - timedelta(days=1)).date()
        cutoff_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
    else:
        # Next day 6 AM
        cutoff_time = (cutoff_time + timedelta(days=1))
    
    if now > cutoff_time:
        raise HTTPException(
            status_code=400,
            detail="Writing time has expired for this date"
        )
    
    # Check if user already wrote diary for this date
    existing_diary = db.query(DiaryModel).filter(
        DiaryModel.author_id == current_user.id,
        DiaryModel.created_at >= today,
        DiaryModel.created_at < today + timedelta(days=1)
    ).first()
    
    if existing_diary:
        raise HTTPException(
            status_code=400,
            detail="You already wrote a diary for this date"
        )
    
    db_diary = DiaryModel(
        title=title,
        content=content,
        author_id=current_user.id
    )
    db.add(db_diary)
    db.commit()
    db.refresh(db_diary)
    
    # Handle photo uploads if provided
    if photos:
        await _handle_diary_photos(db, db_diary.id, photos, current_user)
    
    # Send push notification to partner if they exist and have push subscription
    if current_user.partner_id:
        partner = db.query(User).filter(User.id == current_user.partner_id).first()
        if partner and partner.push_subscription:
            author_name = current_user.name or current_user.email
            send_push_notification(
                partner.push_subscription,
                "새로운 일기가 도착했어요!",
                f"{author_name}님이 오늘의 일기를 작성했습니다."
            )
    
    return db_diary

@router.get("/my", response_model=List[Diary])
def get_my_diaries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    diaries = db.query(DiaryModel).filter(
        DiaryModel.author_id == current_user.id
    ).order_by(DiaryModel.created_at.desc()).all()
    return diaries

@router.get("/partner", response_model=List[Diary])
def get_partner_diaries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.partner_id:
        return []
    
    # Get partner's diaries that were written today
    today = datetime.utcnow().date()
    partner_diaries = db.query(DiaryModel).filter(
        DiaryModel.author_id == current_user.partner_id,
        DiaryModel.created_at >= today
    ).all()
    
    # Check if current user has written diary today
    my_diary_today = db.query(DiaryModel).filter(
        DiaryModel.author_id == current_user.id,
        DiaryModel.created_at >= today
    ).first()
    
    # Only show partner's diary if user has written their own
    if my_diary_today:
        # Mark partner's diaries as read
        for diary in partner_diaries:
            diary.is_read_by_partner = True
        db.commit()
        return partner_diaries
    
    return []

@router.get("/month/{year}/{month}")
def get_month_diaries(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get diary status for each day in a specific month"""
    from calendar import monthrange
    from collections import defaultdict
    
    # Get number of days in the month
    _, days_in_month = monthrange(year, month)
    
    # Initialize result
    result = {}
    
    # Get all diaries for this month
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, days_in_month, 23, 59, 59)
    
    my_diaries = db.query(DiaryModel).filter(
        DiaryModel.author_id == current_user.id,
        DiaryModel.created_at >= start_date,
        DiaryModel.created_at <= end_date
    ).all()
    
    partner_diaries = []
    if current_user.partner_id:
        partner_diaries = db.query(DiaryModel).filter(
            DiaryModel.author_id == current_user.partner_id,
            DiaryModel.created_at >= start_date,
            DiaryModel.created_at <= end_date
        ).all()
    
    # Create lookup dictionaries
    my_diary_days = {d.created_at.day: d for d in my_diaries}
    partner_diary_days = {d.created_at.day: d for d in partner_diaries}
    
    # Build result for each day
    today = datetime.utcnow().date()
    
    for day in range(1, days_in_month + 1):
        date = datetime(year, month, day).date()
        has_my_diary = day in my_diary_days
        has_partner_diary = day in partner_diary_days
        
        status = "future"
        if date < today:
            status = "past"
        elif date == today:
            status = "today"
        
        result[day] = {
            "date": date.isoformat(),
            "status": status,
            "has_my_diary": has_my_diary,
            "has_partner_diary": has_partner_diary,
            "is_complete": has_my_diary and has_partner_diary
        }
    
    return result

@router.get("/date/{year}/{month}/{day}")
def get_day_diaries(
    year: int,
    month: int,
    day: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get diaries for a specific date"""
    date = datetime(year, month, day).date()
    next_date = date + timedelta(days=1)
    
    # Get my diary
    my_diary = db.query(DiaryModel).filter(
        DiaryModel.author_id == current_user.id,
        DiaryModel.created_at >= date,
        DiaryModel.created_at < next_date
    ).first()
    
    # Get partner's diary
    partner_diary = None
    partner_name = None
    if current_user.partner_id:
        partner = db.query(User).filter(User.id == current_user.partner_id).first()
        partner_name = partner.name if partner else None
        
        partner_diary = db.query(DiaryModel).filter(
            DiaryModel.author_id == current_user.partner_id,
            DiaryModel.created_at >= date,
            DiaryModel.created_at < next_date
        ).first()
    
    return {
        "date": date.isoformat(),
        "my_diary": my_diary,
        "partner_diary": partner_diary,
        "my_name": current_user.name or "나",
        "partner_name": partner_name or "상대방",
        "can_write": _can_write_diary(date)
    }

def _can_write_diary(date: datetime.date) -> bool:
    """Check if user can still write diary for given date"""
    now = datetime.utcnow()
    cutoff = datetime.combine(date + timedelta(days=1), datetime.min.time()).replace(hour=6)
    return now <= cutoff

@router.put("/{diary_id}", response_model=Diary)
def update_diary(
    diary_id: int,
    diary_update: DiaryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update own diary (only allowed until 6 AM next day)"""
    # Get the diary
    diary = db.query(DiaryModel).filter(
        DiaryModel.id == diary_id,
        DiaryModel.author_id == current_user.id
    ).first()
    
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")
    
    # Check if can still edit (until 6 AM next day)
    diary_date = diary.created_at.date()
    if not _can_write_diary(diary_date):
        raise HTTPException(
            status_code=403,
            detail="Cannot edit diary after 6 AM next day"
        )
    
    # Update diary
    diary.title = diary_update.title
    diary.content = diary_update.content
    diary.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(diary)
    
    return diary

async def _handle_diary_photos(
    db: Session,
    diary_id: int,
    photos: List[UploadFile],
    current_user: User
):
    """Handle photo uploads for diary"""
    # Import here to avoid circular dependency
    from app.api.photos import get_supabase_client
    
    # Get couple ID for folder organization
    couple_id = f"{min(current_user.id, current_user.partner_id or current_user.id)}_{max(current_user.id, current_user.partner_id or current_user.id)}"
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    for photo in photos:
        if not photo or photo.filename == "":
            continue
            
        # Generate unique filename
        file_extension = photo.filename.split('.')[-1] if '.' in photo.filename else 'jpg'
        unique_filename = f"{diary_id}_{uuid.uuid4()}.{file_extension}"
        
        # Try Supabase first
        try:
            supabase = get_supabase_client()
            if supabase:
                file_path = f"diaries/{couple_id}/{date_str}/{unique_filename}"
                file_content = await photo.read()
                
                response = supabase.storage.from_("photos").upload(
                    file_path,
                    file_content,
                    file_options={"content-type": photo.content_type or "image/jpeg"}
                )
                
                public_url = supabase.storage.from_("photos").get_public_url(file_path)
                photo_url = public_url
            else:
                raise Exception("Supabase not available")
                
        except Exception as e:
            # Fallback to local storage
            print(f"Supabase upload failed, using local storage: {e}")
            
            # Create local directory
            local_dir = f"uploads/diaries/{couple_id}/{date_str}"
            os.makedirs(local_dir, exist_ok=True)
            
            # Save file locally
            file_path = f"{local_dir}/{unique_filename}"
            file_content = await photo.read() if photo.size > 0 else await photo.read()
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # Generate local URL
            base_url = os.getenv("BASE_URL", "http://localhost:8000")
            photo_url = f"{base_url}/{file_path}"
        
        # Save photo record to database
        db_photo = DiaryPhoto(
            diary_id=diary_id,
            photo_url=photo_url,
            original_filename=photo.filename
        )
        db.add(db_photo)
    
    db.commit()

