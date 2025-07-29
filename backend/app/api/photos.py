from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.monthly_photo import MonthlyPhoto
from app.api.deps import get_current_user
from app.core.config import settings
import os
import uuid
from datetime import datetime
from supabase import create_client, Client
import base64
from typing import Optional

router = APIRouter()

def get_supabase_client() -> Optional[Client]:
    """Create Supabase client if credentials are available"""
    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return None

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
    
    # Check if photo already exists for this month
    existing_photo = db.query(MonthlyPhoto).filter(
        MonthlyPhoto.couple_id == couple_id,
        MonthlyPhoto.year == year,
        MonthlyPhoto.month == month
    ).first()
    
    # Read file content
    content = await file.read()
    
    # Try to use Supabase Storage first
    supabase = get_supabase_client()
    if supabase:
        try:
            # If photo exists, delete the old file
            if existing_photo:
                # Extract file name from URL
                old_file_name = existing_photo.photo_url.split("/")[-1]
                if existing_photo.photo_url.startswith("https://"):
                    # It's a Supabase URL, delete from storage
                    try:
                        supabase.storage.from_("photos").remove([f"monthly/{old_file_name}"])
                    except:
                        pass  # Ignore deletion errors
                
                # Delete the database entry
                db.delete(existing_photo)
                db.commit()
            
            # Generate file name
            file_extension = file.filename.split(".")[-1]
            file_name = f"{couple_id}_{year}_{month}_{uuid.uuid4()}.{file_extension}"
            file_path = f"monthly/{file_name}"
            
            # Upload to Supabase Storage
            response = supabase.storage.from_("photos").upload(
                file_path,
                content,
                file_options={"content-type": file.content_type}
            )
            
            # Get public URL
            photo_url = supabase.storage.from_("photos").get_public_url(file_path)
            
        except Exception as e:
            print(f"Supabase storage error: {str(e)}")
            # Fall back to local storage
            photo_url = await save_to_local_storage(couple_id, year, month, file, content, existing_photo, db)
    else:
        # Use local storage
        photo_url = await save_to_local_storage(couple_id, year, month, file, content, existing_photo, db)
    
    # Create database entry
    monthly_photo = MonthlyPhoto(
        year=year,
        month=month,
        couple_id=couple_id,
        photo_url=photo_url,
        created_by=current_user.id
    )
    
    db.add(monthly_photo)
    db.commit()
    db.refresh(monthly_photo)
    
    # Return with proper URL
    return {
        "id": monthly_photo.id,
        "year": monthly_photo.year,
        "month": monthly_photo.month,
        "couple_id": monthly_photo.couple_id,
        "photo_url": monthly_photo.photo_url,
        "created_at": monthly_photo.created_at,
        "created_by": monthly_photo.created_by
    }

async def save_to_local_storage(couple_id: str, year: int, month: int, file: UploadFile, content: bytes, existing_photo, db: Session) -> str:
    """Fallback to local storage"""
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    
    # If photo exists, delete the old file
    if existing_photo and not existing_photo.photo_url.startswith("https://"):
        old_file_name = existing_photo.photo_url.split("/")[-1]
        old_file_path = os.path.join(uploads_dir, old_file_name)
        if os.path.exists(old_file_path):
            os.remove(old_file_path)
    
    # Save file
    file_extension = file.filename.split(".")[-1]
    file_name = f"{couple_id}_{year}_{month}_{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(uploads_dir, file_name)
    
    with open(file_path, 'wb') as f:
        f.write(content)
    
    return f"/uploads/{file_name}"

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
        # Handle URL based on type
        if photo.photo_url.startswith("https://"):
            # It's already a full URL (Supabase)
            photo_url = photo.photo_url
        else:
            # It's a local path, convert to full URL
            base_url = str(request.base_url).rstrip('/')
            photo_url = f"{base_url}{photo.photo_url}"
        
        photo_dict = {
            "id": photo.id,
            "year": photo.year,
            "month": photo.month,
            "couple_id": photo.couple_id,
            "photo_url": photo_url,
            "created_at": photo.created_at,
            "created_by": photo.created_by
        }
        return photo_dict
    
    return photo