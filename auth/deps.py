from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.client import supabase
from auth.schemas import UserResponse

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    token = credentials.credentials
    res = supabase.auth.get_user(token)
    user_data = res.user
    return UserResponse(
        id=str(user_data.id),
        email=user_data.email,
        user_metadata=user_data.user_metadata or {},
        created_at=str(user_data.created_at) if user_data.created_at else None,
    )
