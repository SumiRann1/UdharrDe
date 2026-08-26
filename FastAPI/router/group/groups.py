from fastapi import FastAPI, APIRouter
from .schemas import (addMember,createGroupSchema)
from database.grp_data import (add_mem , create_grp)
from database.user_data import (get_user_by_name)


groups= APIRouter(prefix="/groups", tags=["groups"])

@groups.post("/create_group")
def create_group(groupData: createGroupSchema):
    ''' This function takes the group name and creator's user ID from the request body and creates a new group'''
    if not groupData.groupName:
        return {"error": "Group name is required"}
    if not groupData.creator_uid:
        return {"error": "No such user exists"}
    create_grp(groupData.groupName, groupData.creator_uid)
    return {"message": f"Group '{groupData.groupName}' created by user"}

@groups.post("/add_member")
def add_member(groupData: addMember):
    ''' This function takes the group name and list of members from the request body and creates a new group.'''
    if not groupData.groupName:
        return {"error": "Group name is required"}
    if not groupData.listMembers:
        return {"error": "List of members is required"}
    membersUuid=[]
    for member in groupData.listMembers:
        try:
            dataMembers = get_user_by_name(member)
        except Exception as e:
            return {"error": f"Error retrieving user '{member}': {str(e)}"}
        membersUuid.append(dataMembers[id])
    add_mem(groupData.groupName, membersUuid)
    return {"message": f"Group '{groupData.groupName}' created with members: {groupData.listMembers}"}







    