from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone_number: str = Field(..., pattern=r"^\d{10}$")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ForgotPassword(BaseModel):
    email: EmailStr


class ChangePassword(BaseModel):
    verification_code: str
    new_password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone_number: str

    class Config:
        from_attributes = True


class Userdetail(BaseModel):
    id: int
