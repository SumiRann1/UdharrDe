from pydantic import BaseModel, Field, computed_field
from typing import Optional, Literal, List
import uuid
from database.user_data import get_friends, get_exp_frnd, get_user_by_id
from router.auth.schemas import UserResponse

def get_friends_data(current_user: UserResponse):
    friends = get_friends(current_user.id)
    exp_frnd = get_exp_frnd(current_user.id)
    friends_data = []
    for friend in friends:
        friend_data = get_user_by_id(friend)
        if friend_data:
            friend_data["amount"] = exp_frnd.get(friend, 0)
            friends_data.append(friend_data)
    return friends_data


class SettleUpRequest(BaseModel):
    payer_id : uuid.UUID
    receiver_id: uuid.UUID
    amount: float
    notes: Optional[str] = "Settlement Payment"
    payment_method: Literal["Cash", "UPI"]

    @computed_field
    def getfrnds(self) -> list:
        if not self.payer_id:
            return []
        return get_friends(str(self.payer_id))
    
    def getexp(self):
        if not self.payer_id:
            return {}
        return get_exp_frnd(str(self.payer_id))
     
class UPILinkRequest(BaseModel):
    payer_name : str
    payee_upi: str = Field(..., description="UPI ID, e.g. example@okaxis")
    payee_name: str = Field(..., description="Recipient Name")
    amount: float = Field(..., gt=0)
    note: Optional[str] = "UdharrDe Settlement"

class UPILinkResponse(BaseModel):
    upi_url: str
    qr_code_url: str
    payee_upi: str
    amount: float
    payer_name: str
    payee_name : str

class SettleUpResponse(BaseModel):
    message: str
    payer_id: uuid.UUID
    receiver_id: uuid.UUID
    amount_settled: float
    net_balance_with_friend: float
    upi_link: Optional[UPILinkResponse] = None
    method : Literal["Cash","UPI"]

    
