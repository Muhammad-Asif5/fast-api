from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from fastapi import Form, UploadFile, File
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    email: str
    password: str = Field(..., min_length=8, max_length=72)
    full_name: Optional[str] = None  # Add this line
    
    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v):
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password cannot exceed 72 bytes')
        return v


class UserLogin(BaseModel):
    username: str
    password: str = Field(..., max_length=72)


class UserResponse(UserBase):
    id: int
    CreatedBy: Optional[UUID] = None
    IsActive: bool = Field(alias="Isactive")
    CreatedDate: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

