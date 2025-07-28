from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.monthly_photo import MonthlyPhoto
from app.api.deps import get_current_user
import os
import uuid
from datetime import datetime
import aiofiles

router = APIRouter()

@router.post("/upload/{year}/{month}")
async def upload_monthly_photo(
    year: int,
    month: int,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a photo for a specific month"""
    if not current_user.partner_id:
        raise HTTPException(
            status_code=400,
            detail="You need a partner to upload monthly photos"
        )
    
    # Create couple_id (always smaller ID first for consistency)
    couple_id = f"{min(current_user.id, current_user.partner_id)}_{max(current_user.id, current_user.partner_id)}"
    
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Check if photo already exists for this month
    existing_photo = db.query(MonthlyPhoto).filter(
        MonthlyPhoto.couple_id == couple_id,
        MonthlyPhoto.year == year,
        MonthlyPhoto.month == month
    ).first()
    
    # If photo exists, delete the old file
    if existing_photo:
        # Delete the old file from disk
        old_file_name = existing_photo.photo_url.split("/")[-1]
        old_file_path = os.path.join(uploads_dir, old_file_name)
        if os.path.exists(old_file_path):
            os.remove(old_file_path)
        
        # Delete the database entry
        db.delete(existing_photo)
        db.commit()
    
    # Save file (in production, use cloud storage)
    file_extension = file.filename.split(".")[-1]
    file_name = f"{couple_id}_{year}_{month}_{uuid.uuid4()}.{file_extension}"
    
    # Save file to disk
    file_path = os.path.join(uploads_dir, file_name)
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Create URL path for database storage
    url_path = f"/uploads/{file_name}"
    
    # Create database entry
    monthly_photo = MonthlyPhoto(
        year=year,
        month=month,
        couple_id=couple_id,
        photo_url=url_path,
        created_by=current_user.id
    )
    
    db.add(monthly_photo)
    db.commit()
    db.refresh(monthly_photo)
    
    # Return with full URL
    base_url = str(request.base_url).rstrip('/')
    return {
        "id": monthly_photo.id,
        "year": monthly_photo.year,
        "month": monthly_photo.month,
        "couple_id": monthly_photo.couple_id,
        "photo_url": f"{base_url}{monthly_photo.photo_url}",
        "created_at": monthly_photo.created_at,
        "created_by": monthly_photo.created_by
    }

@router.get("/{year}/{month}")
def get_monthly_photo(
    year: int,
    month: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get photo for a specific month"""
    if not current_user.partner_id:
        return None
    
    couple_id = f"{min(current_user.id, current_user.partner_id)}_{max(current_user.id, current_user.partner_id)}"
    
    photo = db.query(MonthlyPhoto).filter(
        MonthlyPhoto.couple_id == couple_id,
        MonthlyPhoto.year == year,
        MonthlyPhoto.month == month
    ).first()
    
    if photo:
        # Convert relative URL to absolute URL
        base_url = str(request.base_url).rstrip('/')
        photo_dict = {
            "id": photo.id,
            "year": photo.year,
            "month": photo.month,
            "couple_id": photo.couple_id,
            "photo_url": f"{base_url}{photo.photo_url}",
            "created_at": photo.created_at,
            "created_by": photo.created_by
        }
        return photo_dict
    
    return photo