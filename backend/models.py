from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class Language(str, Enum):
    NL = "nl"
    EN = "en"
    RU = "ru"

class TextCreate(BaseModel):
    title: Optional[str] = None
    content: str = Field(min_length=1)
    language: Language
    section_id: Optional[str] = None

class TextResponse(BaseModel):
    id: str = Field(alias="_id")
    title: Optional[str] = None
    content: str
    language: Language
    section_id: Optional[str] = None
    created_at: str
    model_config = ConfigDict(populate_by_name=True)

class SectionCreate(BaseModel):
    title: str
    parent_id: Optional[str] = None

class SectionResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    parent_id: Optional[str] = None
    created_at: str
    model_config = ConfigDict(populate_by_name=True)

class UserCreate(BaseModel):
    email: str
    password: str
    language: Language

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    email: str
    language: Language
    created_at: str
