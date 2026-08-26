from pydantic import BaseModel, Field, computed_field
from typing import List, Dict
import uuid

class DashboardResponse(BaseModel):
    id : uuid.UUID
    name : str
    phone : str
    email : str
    friends : List[uuid.UUID]
    in_grp : List[uuid.UUID]
    exp_frnd : Dict[uuid.UUID, int]
    tot_owe : int
    tot_lend : int
    # split_transactions : List[uuid.UUID]
    # group_transactions : List[uuid.UUID]
    created_at : str

    @computed_field
    def net_balance(self) -> int:
        return self.tot_lend - self.tot_owe

