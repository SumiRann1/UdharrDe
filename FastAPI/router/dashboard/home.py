from fastapi import APIRouter, Depends, HTTPException
from database.user_data import get_user_by_id, update_user, get_user_by_id_list, is_friend
from database.grp_data import get_grp_by_id_list, grp_info_by_id
from database.exp_data import get_user_exp, get_grp_exp
from router.auth.deps import get_current_user
from router.auth.schemas import UserResponse
from .schemas import DashboardResponse, UpdateProfileRequest, GroupResponse, FriendDashboardResponse, GroupDashboardResponse
import uuid

home = APIRouter(prefix="/dashboard", tags=["dashboard"])

def format_user_dashboard(user: dict) -> dict:
    friends_list = user.get("friends") or []
    groups_list = user.get("in_grp") or []
    exp_dict = user.get("exp_frnd") or {}

    user_map = {user["id"]: user["name"] for user in get_user_by_id_list(friends_list + list(exp_dict.keys()))}
    group_map = {group["id"]: group["name"] for group in get_grp_by_id_list(groups_list)}

    user_copy = dict(user)
    user_copy["friends"] = [{"id": f, "name": user_map.get(str(f), "User")} for f in friends_list]
    user_copy["in_grp"] = [{"id": g, "name": group_map.get(str(g), "Group")} for g in groups_list]
    user_copy["exp_frnd"] = [{"id": f, "name": user_map.get(str(f), "User"), "amount": amt} for f, amt in exp_dict.items()]

    return user_copy

@home.get("/", response_model=DashboardResponse)
def dashboard(current_user: UserResponse = Depends(get_current_user)):
    user = get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return DashboardResponse(**format_user_dashboard(user))

@home.put("/update", response_model=DashboardResponse)
def update_profile(update_paras: UpdateProfileRequest, current_user: UserResponse = Depends(get_current_user)):
    user = get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_user(current_user.id, update_paras.display_name, update_paras.phone)
    updated_user = get_user_by_id(current_user.id)
    return DashboardResponse(**format_user_dashboard(updated_user))

@home.get("/friend/{friend_id}", response_model=FriendDashboardResponse)
def get_friend_transactions(friend_id: uuid.UUID, current_user: UserResponse = Depends(get_current_user)):
    friend = get_user_by_id(str(friend_id))
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")

    if not (is_friend(str(current_user.id), str(friend_id)) or is_friend(str(friend_id), str(current_user.id))):
        raise HTTPException(status_code=403, detail="You are not friends with this user")

    curr_user_transaction = get_user_exp(str(current_user.id))
    friend_transaction = []
    for records in curr_user_transaction:
        if str(records.get("paid_by")) == str(friend_id) or str(records.get("u_pay")) == str(friend_id) or str(records.get("g_pay")) == str(friend_id):
            friend_transaction.append(records)
    total_owed = 0.0
    total_lend = 0.0
    for record in friend_transaction:
        if str(record["paid_by"]) == str(current_user.id):
            if str(record["u_pay"]) == str(friend_id):
                total_owed += record["amt"]
            elif str(record["g_pay"]) == str(friend_id):
                total_owed += record["amt"]
        elif str(record["u_pay"]) == str(current_user.id):
            if str(record["paid_by"]) == str(friend_id):
                total_lend += record["amt"]
        elif str(record["g_pay"]) == str(current_user.id):
            if str(record["paid_by"]) == str(friend_id):
                total_lend += record["amt"]

    balance = total_lend - total_owed

    return FriendDashboardResponse(
        id=friend["id"],
        name=friend.get("name"),
        phone=friend.get("phone"),
        email=friend.get("email"),
        tot_owe=int(total_owed),
        tot_lend=int(total_lend),
        balance=int(balance),
        created_at=friend.get("created_at"),
        activities=friend_transaction
    )

@home.get("/groups/{group_id}", response_model=GroupDashboardResponse)
def get_group_transactions(group_id: uuid.UUID, current_user: UserResponse = Depends(get_current_user)):
    try:
        group = grp_info_by_id(str(group_id))
    except Exception:
        group = None
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    members_list = group.get("members") or []
    if str(current_user.id) not in [str(m) for m in members_list]:
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    group_transactions = get_grp_exp(str(group_id))
    total_owed = 0.0
    total_lend = 0.0

    for record in group_transactions:
        paid_by = str(record.get("paid_by"))
        amt = float(record.get("amt", 0.0))
        split = record.get("split") or {}

        if paid_by == str(current_user.id):
            if split and isinstance(split, dict):
                my_share = float(split.get(str(current_user.id), 0.0))
                total_owed += (amt - my_share)
            else:
                total_owed += amt
        elif split and isinstance(split, dict) and str(current_user.id) in split:
            my_share = float(split.get(str(current_user.id), 0.0))
            total_lend += my_share

    balance = total_lend - total_owed

    created_by_id = str(group.get("created_by") or "")
    user_map = {user["id"]: user["name"] for user in get_user_by_id_list(members_list + ([created_by_id] if created_by_id else []))}

    enriched_members = [{"id": m, "name": user_map.get(str(m), "User")} for m in members_list]
    created_by_name = user_map.get(created_by_id, "User")

    return GroupDashboardResponse(
        id=group["id"],
        name=group.get("name"),
        members=enriched_members,
        created_by=group.get("created_by"),
        created_by_name=created_by_name,
        tot_owe=int(total_owed),
        tot_lend=int(total_lend),
        balance=int(balance),
        created_at=group.get("created_at"),
        activities=group_transactions
    )


