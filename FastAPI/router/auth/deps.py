from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database.client import supabase
from .schemas import UserResponse

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    token = credentials.credentials
    try:
        res = supabase.auth.get_user(token)
        user_data = res.user
        if not user_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or user not found")
        return UserResponse(
            id=str(user_data.id),
            email=user_data.email,
            user_metadata=user_data.user_metadata or {},
            created_at=str(user_data.created_at) if user_data.created_at else None,
        )
    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired access token: {str(err)}"
        )

