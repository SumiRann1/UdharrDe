import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


try:
    SUPABASE_URL=os.getenv("SUPABASE_URL")
    SUPABASE_KEY=os.getenv("SUPABASE_KEY")
    if SUPABASE_KEY and SUPABASE_URL:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase connected")
    else:
        supabase=None
        print("Supabase not connected")
except:
    supabase=None
    print("supabase not found")

#USERS

def create_user(user_uid, name, phone, email=None):
    now = datetime.now().strftime("%b-%d-%Y %H:%M:%S")

    try:
        user_data={
            "id": user_uid,
            "name": name,
            "email": email,
            "phone": phone,
            "friends": [],
            "in_grp": [],
            "exp_frnd": {},
            "tot_owe": 0,
            "tot_lend": 0,
            "created_at": now
        }
        response= supabase.table("users").insert(user_data).execute()
        print("user created successfully")
        return user_uid
    except Exception as e:
        print(f"Error: {e}")
        raise e

def update_user(uid, new_name=True, new_phone=True):
    response= supabase.table("users").select("*").eq("id", uid).single().execute()
    if new_name:
        new_name=response.data["name"]
    if new_phone:
        new_phone=response.data["phone"]


def get_user_by_id(uid):
    response= supabase.table("users").select("*").eq("id", uid).single().execute()
    if not response.data:
        return None
    return response.data

def add_friends(uid1, uid2):
    # when we add friend for one user we want mutual friendship from both side so when we do so call this function twice with friend 1 first and friend 2 in the second arg. while running for the second time call friend 2 as first arg and then friend 1 as second arg
    response=(supabase.table("users").select("friends").eq("id",uid1).single().execute())
    friends=response.data["friends"]
    friends.append(uid2)
    supabase.table("users").update({"friends": friends}).eq("id", uid1).execute()


#GROUPS
