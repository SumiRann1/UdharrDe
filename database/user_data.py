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

def create_user(user_uid, name, phone, mail):
    # summi apne auth ke file se complete profile ke bad ye function  call karega jo public.user me user info store karega
    now = datetime.now().strftime("%b-%d-%Y %H:%M:%S")

    try:
        user_data={
            "id": user_uid,
            "name": name,
            "phone": phone,
            "friends": [],
            "in_grp": [],
            "exp_frnd": {},
            "tot_owe": 0,
            "tot_lend": 0,
            "created_at": now,
            "email": mail
        }
        response= supabase.table("users").insert(user_data).execute()
        print("user created successfully")
        return user_uid
    except Exception as e:
        print(f"Error: {e}")
        raise e

def update_user(uid, new_name=False, new_phone=False):
    # ye uid use karke user name and phone ko change kar sakta hai
    # current user ka uid front end tokens se aiga mostly
    try:
        response= supabase.table("users").select("*").eq("id", uid).single().execute()
        if not new_name:
            new_name=response.data["name"]
        if not new_phone:
            new_phone=response.data["phone"]
        supabase.table("users").update({"name":new_name, "phone": new_phone}).eq("id", uid).execute()
        print("user data updated")
    except Exception as e:
        print(f"Error: {e}")
        raise e

def get_user_by_id(uid):
    # current user ka data extract karne ke liye use karenge
    # same last time jaise tokens se uid leke apan current user uid pass karenge
    response= supabase.table("users").select("*").eq("id", uid).single().execute()
    if not response.data:
        return None
    return response.data

def add_f_helper(uid1, uid2):
    # helper function friends ko mutually add karne ke liye
    response=(supabase.table("users").select("friends").eq("id",uid1).single().execute())
    friends=response.data["friends"]
    if uid2 not in friends:
        friends.append(uid2)
        supabase.table("users").update({"friends": friends}).eq("id", uid1).execute()
        print("friend added")
    else:
        print("friend already exists")


def add_friends(uid1, uid2):
    # helper funct use karke both side relation form karke apan friends list me add kar denge
    try:
        add_f_helper(uid1, uid2)
        add_f_helper(uid2, uid1)
    except Exception as e:
        print(f"Error: e")
        raise e

#-------------------
# create_user
# create_user("6c1363ba-ae17-43e4-82e2-89894e651e89", "asdf", '9876543210', "mail@mail.com")
# update_user
# update_user("6c1363ba-ae17-43e4-82e2-89894e651e89", "qwerdf", '5432109876')
#add_friends
# add_friends("6c1363ba-ae17-43e4-82e2-89894e651e89", "7c1363ba-ae17-43e4-82e2-89894e651e89")