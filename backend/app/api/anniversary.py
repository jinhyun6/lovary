from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.db.database import get_db
from app.models.anniversary import Anniversary as AnniversaryModel
from app.models.user import User
from app.schemas.anniversary import Anniversary, AnniversaryCreate, AnniversaryUpdate
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=Anniversary)
def create_or_update_anniversary(
    anniversary: AnniversaryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.partner_id:
        raise HTTPException(status_code=400, detail="No partner connected")
    
    # Check if anniversary already exists for this date
    existing = db.query(AnniversaryModel).filter(
        ((AnniversaryModel.user_id == current_user.id) & (AnniversaryModel.partner_id == current_user.partner_id)) |
        ((AnniversaryModel.user_id == current_user.partner_id) & (AnniversaryModel.partner_id == current_user.id)),
        AnniversaryModel.date == anniversary.date
    ).first()
    
    if existing:
        # Update existing anniversary
        existing.name = anniversary.name
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new anniversary
    db_anniversary = AnniversaryModel(
        user_id=current_user.id,
        partner_id=current_user.partner_id,
        date=anniversary.date,
        name=anniversary.name
    )
    db.add(db_anniversary)
    db.commit()
    db.refresh(db_anniversary)
    
    return db_anniversary

@router.get("/", response_model=List[Anniversary])
def get_anniversaries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.partner_id:
        return []
    
    anniversaries = db.query(AnniversaryModel).filter(
        ((AnniversaryModel.user_id == current_user.id) & (AnniversaryModel.partner_id == current_user.partner_id)) |
        ((AnniversaryModel.user_id == current_user.partner_id) & (AnniversaryModel.partner_id == current_user.id))
    ).all()
    
    return anniversaries

@router.get("/month/{year}/{month}")
def get_month_anniversaries(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get anniversaries for a specific month"""
    if not current_user.partner_id:
        return {}
    
    # Get all anniversaries for this month
    anniversaries = db.query(AnniversaryModel).filter(
        ((AnniversaryModel.user_id == current_user.id) & (AnniversaryModel.partner_id == current_user.partner_id)) |
        ((AnniversaryModel.user_id == current_user.partner_id) & (AnniversaryModel.partner_id == current_user.id))
    ).all()
    
    # Filter by month and create result dict
    result = {}
    for anniversary in anniversaries:
        # Check if anniversary is in this month (considering recurring yearly)
        if anniversary.date.month == month:
            day = anniversary.date.day
            result[day] = {
                "name": anniversary.name,
                "date": anniversary.date.isoformat()
            }
    
    return result

@router.delete("/{anniversary_id}")
def delete_anniversary(
    anniversary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    anniversary = db.query(AnniversaryModel).filter(
        AnniversaryModel.id == anniversary_id,
        ((AnniversaryModel.user_id == current_user.id) | (AnniversaryModel.partner_id == current_user.id))
    ).first()
    
    if not anniversary:
        raise HTTPException(status_code=404, detail="Anniversary not found")
    
    db.delete(anniversary)
    db.commit()
    
    return {"message": "Anniversary deleted"}