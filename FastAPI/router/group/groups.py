from fastapi import FastAPI, APIRouter
from .schemas import (addMember,createGroupSchema, getGroupsSchema)
from database.grp_data import (add_mem , create_grp, grp_info_by_id)
from database.user_data import (get_user_by_name,  get_user_grps)
from fastapi import HTTPException


groups= APIRouter(prefix="/groups", tags=["groups"])

@groups.post("/create_group")
def create_group(groupData: createGroupSchema):
    ''' This function takes the group name and creator's user ID from the request body and creates a new group'''
    if not groupData.groupName:
        raise HTTPException(status_code=400, detail="Group name is required")
    if not groupData.creator_uid:
        raise HTTPException(status_code=400, detail="Creator user ID is required")
    create_grp(groupData.groupName, str(groupData.creator_uid))
    raise HTTPException(status_code=200, detail=f"Group '{groupData.groupName}' created successfully")

@groups.post("/add_member")
def add_member(groupData: addMember):
    ''' This function takes the group name and list of members from the request body and creates a new group.'''
    if not groupData.groupName:
        raise HTTPException(status_code=400, detail="Group name is required")
    if not groupData.listMembers:
        raise HTTPException(status_code=400, detail="List of members is required")
    membersUuid=[]
    for member in groupData.listMembers:
        try:
            dataMembers = get_user_by_name(member)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error retrieving user '{member}': {str(e)}")
        membersUuid.append(dataMembers["id"])
    add_mem(groupData.groupName, membersUuid)
    raise HTTPException(status_code=200, detail=f"Group '{groupData.groupName}' created with members: {groupData.listMembers}")

@groups.post("/get_groups")
def get_groups(groupData: getGroupsSchema):
    '''this gives all the data of the groups that a user is a part of'''
    grpUuids = get_user_grps(groupData.userUdid)
    allGroupData = []
    for grpUuid in grpUuids:
        grpData = grp_info_by_id(grpUuid)
        allGroupData.append(grpData)
    return {
    "message": f"Groups for user '{groupData.userUdid}'",
    "groups": allGroupData
    }




    