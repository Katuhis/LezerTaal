from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TextCreate(BaseModel):
    title: Optional[str] = None
    content: str = Field(min_length=1)
    language: str = Field(min_length=1)
    section_id: Optional[str] = None

class TextResponse(BaseModel):
    id: str = Field(alias="_id")
    title: Optional[str] = None
    content: str
    language: str
    user_id: str
    section_id: Optional[str] = None
    created_at: str
    model_config = ConfigDict(populate_by_name=True)