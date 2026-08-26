from fastapi import FastAPI, APIRouter
from .schemas import (addMember,createGroupSchema)
from database.grp_data import (add_mem , create_grp)
from database.user_data import (get_user_by_name)


groups= APIRouter(prefix="/dashboard", tags=["dashboard"])

@groups.post("/create_group")
def create_group(groupData: createGroupSchema):
    # This function takes the group name and creator's user ID from the request body and creates a new group.
    if not groupData.groupName:
        return {"error": "Group name is required"}
    if not groupData.creator_uid:
        return {"error": "No such user exists"}
    create_grp(groupData.groupName, groupData.creator_uid)







    