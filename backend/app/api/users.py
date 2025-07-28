from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user import User, PartnerRequest
from app.schemas.user import User as UserSchema, UserUpdate, PartnerRequest as PartnerRequestSchema, PartnerRequestCreate, PushSubscription
from app.api.deps import get_current_user
import json

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def get_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.partner_id:
        partner = db.query(User).filter(User.id == current_user.partner_id).first()
        current_user.partner = partner
    return current_user

@router.put("/me", response_model=UserSchema)
def update_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.reminder_time is not None:
        current_user.reminder_time = user_update.reminder_time
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/search")
def search_users(
    email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    users = db.query(User).filter(
        User.email.contains(email),
        User.id != current_user.id
    ).limit(10).all()
    
    return [{"id": u.id, "email": u.email, "name": u.name} for u in users]

@router.post("/partner-request", response_model=PartnerRequestSchema)
def send_partner_request(
    request: PartnerRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if already has partner
    if current_user.partner_id:
        raise HTTPException(
            status_code=400,
            detail="You already have a partner"
        )
    
    # Find recipient
    recipient = db.query(User).filter(User.email == request.recipient_email).first()
    if not recipient:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    if recipient.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot send request to yourself"
        )
    
    # Check if request already exists
    existing_request = db.query(PartnerRequest).filter(
        ((PartnerRequest.requester_id == current_user.id) & (PartnerRequest.recipient_id == recipient.id)) |
        ((PartnerRequest.requester_id == recipient.id) & (PartnerRequest.recipient_id == current_user.id)),
        PartnerRequest.status == "pending"
    ).first()
    
    if existing_request:
        raise HTTPException(
            status_code=400,
            detail="Partner request already exists"
        )
    
    # Create request
    partner_request = PartnerRequest(
        requester_id=current_user.id,
        recipient_id=recipient.id
    )
    db.add(partner_request)
    db.commit()
    db.refresh(partner_request)
    
    return partner_request

@router.get("/partner-requests", response_model=List[PartnerRequestSchema])
def get_partner_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    requests = db.query(PartnerRequest).filter(
        (PartnerRequest.recipient_id == current_user.id) | (PartnerRequest.requester_id == current_user.id),
        PartnerRequest.status == "pending"
    ).all()
    
    return requests

@router.put("/partner-request/{request_id}/accept")
def accept_partner_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    partner_request = db.query(PartnerRequest).filter(
        PartnerRequest.id == request_id,
        PartnerRequest.recipient_id == current_user.id,
        PartnerRequest.status == "pending"
    ).first()
    
    if not partner_request:
        raise HTTPException(
            status_code=404,
            detail="Partner request not found"
        )
    
    # Update request status
    partner_request.status = "accepted"
    
    # Connect users
    current_user.partner_id = partner_request.requester_id
    requester = db.query(User).filter(User.id == partner_request.requester_id).first()
    requester.partner_id = current_user.id
    
    # Reject all other pending requests for both users
    db.query(PartnerRequest).filter(
        ((PartnerRequest.requester_id == current_user.id) | (PartnerRequest.recipient_id == current_user.id) |
         (PartnerRequest.requester_id == requester.id) | (PartnerRequest.recipient_id == requester.id)),
        PartnerRequest.status == "pending",
        PartnerRequest.id != request_id
    ).update({"status": "rejected"})
    
    db.commit()
    
    return {"message": "Partner request accepted"}

@router.put("/partner-request/{request_id}/reject")
def reject_partner_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    partner_request = db.query(PartnerRequest).filter(
        PartnerRequest.id == request_id,
        PartnerRequest.recipient_id == current_user.id,
        PartnerRequest.status == "pending"
    ).first()
    
    if not partner_request:
        raise HTTPException(
            status_code=404,
            detail="Partner request not found"
        )
    
    partner_request.status = "rejected"
    db.commit()
    
    return {"message": "Partner request rejected"}

@router.post("/push-subscription")
def save_push_subscription(
    subscription: PushSubscription,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.push_subscription = json.dumps(subscription.dict())
    db.commit()
    
    return {"message": "Push subscription saved"}

@router.delete("/partner/disconnect")
def disconnect_partner(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.partner_id:
        raise HTTPException(status_code=400, detail="No partner connected")
    
    # Get partner
    partner = db.query(User).filter(User.id == current_user.partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Disconnect both users
    current_user.partner_id = None
    partner.partner_id = None
    
    # Delete all partner requests between them
    db.query(PartnerRequest).filter(
        ((PartnerRequest.requester_id == current_user.id) & (PartnerRequest.recipient_id == partner.id)) |
        ((PartnerRequest.requester_id == partner.id) & (PartnerRequest.recipient_id == current_user.id))
    ).delete()
    
    db.commit()
    
    return {"message": "Partner disconnected successfully"}

@router.delete("/account")
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # If user has a partner, disconnect first
    if current_user.partner_id:
        partner = db.query(User).filter(User.id == current_user.partner_id).first()
        if partner:
            partner.partner_id = None
    
    # Delete all user's diaries
    from app.models.diary import Diary
    db.query(Diary).filter(Diary.user_id == current_user.id).delete()
    
    # Delete all user's monthly photos
    from app.models.monthly_photo import MonthlyPhoto
    db.query(MonthlyPhoto).filter(MonthlyPhoto.user_id == current_user.id).delete()
    
    # Delete all user's anniversaries
    from app.models.anniversary import Anniversary
    db.query(Anniversary).filter(
        (Anniversary.user_id == current_user.id) | (Anniversary.partner_id == current_user.id)
    ).delete()
    
    # Delete all partner requests
    db.query(PartnerRequest).filter(
        (PartnerRequest.requester_id == current_user.id) | (PartnerRequest.recipient_id == current_user.id)
    ).delete()
    
    # Delete the user
    db.delete(current_user)
    db.commit()
    
    return {"message": "Account deleted successfully"}