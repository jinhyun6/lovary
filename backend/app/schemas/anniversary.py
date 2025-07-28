from pydantic import BaseModel
from datetime import date

class AnniversaryBase(BaseModel):
    date: date
    name: str

class AnniversaryCreate(AnniversaryBase):
    pass

class AnniversaryUpdate(BaseModel):
    name: str

class Anniversary(AnniversaryBase):
    id: int
    user_id: int
    partner_id: int

    class Config:
        from_attributes = True