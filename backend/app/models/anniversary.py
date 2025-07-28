from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Anniversary(Base):
    __tablename__ = "anniversaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    name = Column(String, nullable=False)
    
    user = relationship("User", foreign_keys=[user_id])
    partner = relationship("User", foreign_keys=[partner_id])