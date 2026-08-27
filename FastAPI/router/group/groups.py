from fastapi import FastAPI, APIRouter
from .schemas import (addMember,createGroupSchema, getGroupsSchema)
from database.grp_data import (add_mem , create_grp, grp_info_by_id)
from database.user_data import (get_user_by_name,  get_user_grps)


groups= APIRouter(prefix="/groups", tags=["groups"])

@groups.post("/create_group")
def create_group(groupData: createGroupSchema):
    ''' This function takes the group name and creator's user ID from the request body and creates a new group'''
    if not groupData.groupName:
        return {"error": "Group name is required"}
    if not groupData.creator_uid:
        return {"error": "No such user exists"}
    create_grp(groupData.groupName, str(groupData.creator_uid))
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
        membersUuid.append(dataMembers["id"])
    add_mem(groupData.groupName, membersUuid)
    return {"message": f"Group '{groupData.groupName}' created with members: {groupData.listMembers}"}

@groups.post("/get_groups")
def get_groups(groupData: getGroupsSchema):
    '''this gives all the data of the groups that a user is a part of'''
    grpUuids = get_user_grps(groupData.userUdid)
    allGroupData = []
    for grpUuid in grpUuids:
        grpData = grp_info_by_id(grpUuid)
        allGroupData.append(grpData)
    return allGroupData






    