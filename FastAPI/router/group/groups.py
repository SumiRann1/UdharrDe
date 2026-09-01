from fastapi import FastAPI, APIRouter
from .schemas import (addMember,createGroupSchema, getGroupsSchema, removeMember, getGroupsResponse)
from database.grp_data import (add_mem , create_grp, grp_info_by_id,rm_member)
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

@groups.post("/get_groups", response_model=getGroupsResponse)
def get_groups(groupData: getGroupsSchema):
    '''this gives all the data of the groups that a user is a part of'''
    grpUuids = get_user_grps(groupData.userUdid)
    allGroupData = []
    for grpUuid in grpUuids:
        grpData = grp_info_by_id(grpUuid)
        allGroupData.append(grpData)
    return getGroupsResponse(groups=allGroupData)

@groups.post("/add_member")
def add_member(groupData: addMember):
    ''' This function takes the group name and list of members by name from the request body and creates a new group.'''
    if not groupData.groupName:
        raise HTTPException(status_code=400, detail="Group name is required")
    if not groupData.listMembers:
        raise HTTPException(status_code=400, detail="List of members is required")
    membersUuid=[]
    for member in groupData.listMembers:
        try:
            dataMembers = get_user_by_name(member)
            membersUuid.append(dataMembers["id"])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error retrieving user '{member}': {str(e)}")
    add_mem(groupData.groupName, membersUuid)
    raise HTTPException(status_code=200, detail=f"Group '{groupData.groupName}' created with members: {groupData.listMembers}")

@groups.post("/rm_member")
def remove_member(groupData:removeMember):
    '''This functions is used to remove a member for this it will need the name of the group and a list of members by name '''
    if not groupData.groupName:
            raise HTTPException(status_code=400, detail="Group name is required")
    if not groupData.listMembers:
        raise HTTPException(status_code=400, detail="List of members is required")
    membersUuid=[]
    for member in groupData.listMembers:
        try:
            dataMembers = get_user_by_name(member)
            membersUuid.append(dataMembers["id"])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error retrieving user '{member}': {str(e)}")
    rm_member(groupData.groupName, membersUuid)
    raise HTTPException(status_code=200, detail=f"Group '{groupData.groupName}' created with members: {groupData.listMembers}")
    



    