from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, example="John Doe")
    phone: Optional[str] = Field(None, example="+1234567890")
    notification_pref: Optional[str] = Field("email", example="email")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100, example="strongpassword")
    confirm_password: str = Field(..., example="strongpassword")

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError("passwords do not match")
        return v

class UserUpdate(UserBase):
    current_password: Optional[str] = Field(None, min_length=8, max_length=100)
    new_password: Optional[str] = Field(None, min_length=8, max_length=100)
    confirm_new_password: Optional[str] = Field(None, min_length=8, max_length=100)

    @validator('confirm_new_password')
    def new_passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError("new passwords do not match")
        return v

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class User(UserInDBBase):
    last_login: Optional[datetime] = None

class UserInDB(UserInDBBase):
    hashed_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    jti: Optional[str] = None