from pydantic import BaseModel
from datetime import datetime

class DiaryBase(BaseModel):
    title: str
    content: str

class DiaryCreate(DiaryBase):
    pass

class DiaryUpdate(DiaryBase):
    pass

class Diary(DiaryBase):
    id: int
    author_id: int
    created_at: datetime
    is_read_by_partner: bool

    class Config:
        from_attributes = True

class DiaryInDB(Diary):
    pass