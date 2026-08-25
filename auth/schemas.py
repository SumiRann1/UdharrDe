from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from typing import Optional, Dict, Any, Union
from datetime import datetime


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    confirm_password: str = Field(..., min_length=8, description="Confirm password must be at least 8 characters")
    
    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Password and Confirm Password do not match")
        return self
    
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class VerifyOTPRequest(BaseModel):
    email: EmailStr
    token: str = Field(..., description="6-digit OTP code")
    type: Optional[str] = Field("signup", description="OTP type")

class CompleteProfileRequest(BaseModel):
    display_name: str = Field(..., min_length=3, description="Display name must be at least 3 characters")
    phone: Optional[str] = Field(None, min_length=10, description="Phone number")

    @field_validator('phone')
    def validate_phone(cls, value):
        if value and not value.isdigit():
            raise ValueError("Phone number must contain only digits")
        if value and len(value) != 10:
            raise ValueError("Phone number must be 10 digits long")
        return value

    @field_validator('display_name')
    def validate_display_name(cls, value):
        if value and len(value) < 3:
            raise ValueError("User Name must be at least 3 characters long")
        if value and not value[0].isalpha():
            raise ValueError("User Name must start with an alphabet letter")
        if value and value.endswith(" "):
            raise ValueError("User Name can not end with a space")
        return value
    

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class UserResponse(BaseModel):
    id: str
    email: Optional[str] = None
    user_metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[Union[str, datetime, Any]] = None

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class MessageResponse(BaseModel):
    message: str
    