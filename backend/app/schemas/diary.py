from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class DiaryPhotoBase(BaseModel):
    photo_url: str
    original_filename: Optional[str] = None

class DiaryPhotoCreate(DiaryPhotoBase):
    diary_id: int

class DiaryPhoto(DiaryPhotoBase):
    id: int
    diary_id: int
    created_at: datetime

    class Config:
        from_attributes = True

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
    photos: List[DiaryPhoto] = []

    class Config:
        from_attributes = True

class DiaryInDB(Diary):
    pass