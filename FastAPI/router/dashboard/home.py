from fastapi import APIRouter, Depends, HTTPException
from database.user_data import get_user_by_id, update_user
from router.auth.deps import get_current_user
from router.auth.schemas import UserResponse
from .schemas import DashboardResponse
import logging
logger = logging.getLogger(__name__)

home = APIRouter(prefix="/dashboard", tags=["dashboard"])

@home.get("/")
def dashboard(current_user: UserResponse = Depends(get_current_user)):
    user = None
    try:
        user = get_user_by_id(current_user.id)
    except Exception as e:
        logger.error("Error fetching dashboard for user_id %s: %s", current_user.id, str(e), exc_info=True)
        raise HTTPException(status_code=404, detail=f"Error fetching user: {str(e)}")
    
    if not user:
        logger.warning("Dashboard requested for non-existent user_id: %s", current_user.id)
        raise HTTPException(status_code=404, detail="User not found")

    logger.info("Successfully retrieved dashboard for user_id: %s", current_user.id)
    return DashboardResponse(**user)

@home.put("/update")
def update_profile(display_name: str, phone:str, current_user: UserResponse = Depends(get_current_user)):
    user = None
    try:
        user = get_user_by_id(current_user.id)
    except Exception as e:
        logger.error("Error fetching dashboard for user_id %s: %s", current_user.id, str(e), exc_info=True)
        raise HTTPException(status_code=404, detail=f"Error fetching user: {str(e)}")
    
    if not user:
        logger.warning("Dashboard requested for non-existent user_id: %s", current_user.id)
        raise HTTPException(status_code=404, detail="User not found")

    try:
        update_user(current_user.id, display_name, phone)
        updated_user = get_user_by_id(current_user.id)
        logger.info("Successfully updated profile for user_id: %s", current_user.id)
        return DashboardResponse(**updated_user)
    except Exception as e:
        logger.error("Error updating profile for user_id %s: %s", current_user.id, str(e), exc_info=True)
        raise HTTPException(status_code=404, detail=f"Error updating user: {str(e)}")
    
