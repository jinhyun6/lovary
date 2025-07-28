from sqlalchemy import Column, Integer, String, DateTime, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    partner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reminder_time = Column(Time, nullable=True)
    push_subscription = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    diaries = relationship("Diary", back_populates="author")
    partner_requests_sent = relationship("PartnerRequest", foreign_keys="PartnerRequest.requester_id", back_populates="requester")
    partner_requests_received = relationship("PartnerRequest", foreign_keys="PartnerRequest.recipient_id", back_populates="recipient")

class PartnerRequest(Base):
    __tablename__ = "partner_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")  # pending, accepted, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    
    requester = relationship("User", foreign_keys=[requester_id], back_populates="partner_requests_sent")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="partner_requests_received")