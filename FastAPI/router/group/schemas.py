from pydantic import BaseModel
from uuid import UUID

# ---------- GROUP REQUEST SCHEMAS ----------

class createGroupSchema(BaseModel):
    groupName: str
    creator_uid: UUID
    
class addMember(BaseModel):
    groupName: str
    listMembers: list[str]

# ---------- COMMON RESPONSE SCHEMA ----------

class createGroupSchema(BaseModel):
    message: str
    groupName: str


class addMember(BaseModel):
    message: str
    groupName: str
    listMembers: list[str]