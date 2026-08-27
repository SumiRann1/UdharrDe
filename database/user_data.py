from datetime import datetime
from .client import supabase #.removed before client for local checking
from grp_data import grp_info_by_id

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
        response = supabase.table("users").select("*").eq("id", uid).execute()
        if not response.data or len(response.data) == 0:
            print("User not found for update")
            return
        curr_data = response.data[0]
        if not new_name:
            new_name = curr_data["name"]
        if not new_phone:
            new_phone = curr_data["phone"]
        supabase.table("users").update({"name": new_name, "phone": new_phone}).eq("id", uid).execute()
        print("user data updated")
    except Exception as e:
        print(f"Error: {e}")
        raise e

def get_user_by_id(uid):
    # current user ka data extract karne ke liye use karenge
    # same last time jaise tokens se uid leke apan current user uid pass karenge
    try:
        response = supabase.table("users").select("*").eq("id", uid).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error fetching user by id {uid}: {e}")
        return None

def get_user_by_name(name):
    #user data denge when name is entered
    try:
        response= supabase.table("users").select("*").eq("name", name).single().execute()
        if not response.data:
            return ("User doesn't exist")
        return response.data
    except Exception as e:
        print(f"Error: {e}")
        raise e

def get_user_by_mail(mail):
    #user data denge when email is entered
    try:
        response= supabase.table("users").select("*").eq("email", mail).single().execute()
        if not response.data:
            return ("User doesn't exist")
        return response.data
    except Exception as e:
        print(f"Error: {e}")
        raise e

def is_friend(uid1, uid2):
    response=(supabase.table("users").select("friends").eq("id",uid1).single().execute())
    friends=response.data["friends"]
    if uid2 in friends:
        return True
    else:
        return False

def add_f_helper(uid1, uid2):
    # helper function friends ko mutually add karne ke liye
    response=(supabase.table("users").select("friends").eq("id",uid1).single().execute())
    friends=response.data["friends"]
    if not is_friend(uid1, uid2):
        friends.append(uid2)
        supabase.table("users").update({"friends": friends}).eq("id", uid1).execute()
        print("friend added")
    else:
        print("friend already exists")

def rm_f_helper(uid1, uid2):
    # helper function friends ko mutually rm karne ke liye
        response=(supabase.table("users").select("friends").eq("id",uid1).single().execute())
        friends=response.data["friends"]
        if is_friend(uid1, uid2):
            friends.remove(uid2)
            supabase.table("users").update({"friends": friends}).eq("id", uid1).execute()
            print("friend removed")
        else:
            print("not friends")

def add_friends(uid1, uid2):
    # helper funct use karke both side relation form karke apan friends list me add kar denge
    try:
        add_f_helper(uid1, uid2)
        add_f_helper(uid2, uid1)
    except Exception as e:
        print(f"Error: e")
        raise e

def rm_friends(uid1, uid2):
    try:
        rm_f_helper(uid1, uid2)
        rm_f_helper(uid2, uid1)
    except Exception as e:
        print(f"Error: e")
        raise e

def get_user_grps(uid):
    try:
        response=supabase.table("users").select("in_grp").eq("id", uid).execute()
        return response.data[0]["in_grp"]
    except Exception as e:
        print(f"Error: {e}")
        raise e

#-------------------
# create_user
# create_user("6c1363ba-ae17-43e4-82e2-89894e651e89", "asdf", '9876543210', "mail@mail.com")
# update_user
# update_user("6c1363ba-ae17-43e4-82e2-89894e651e89", "qwerdf", '5432109876')
#add_friends
# add_friends("6c1363ba-ae17-43e4-82e2-89894e651e89", "7c1363ba-ae17-43e4-82e2-89894e651e89")
# print(get_user_by_id("6c1363ba-ae17-43e4-82e2-89894e651e89"))
# print("------------------")
# print(get_user_by_name("asdf"))
# print("------------------")
# print(get_user_by_mail("mail@mail.com"))
# print(is_friend("6c1363ba-ae17-43e4-82e2-89894e651e89", "7c1363ba-ae17-43e4-82e2-89894e651e89"))
# rm_friends("7c1363ba-ae17-43e4-82e2-89894e651e89", "6c1363ba-ae17-43e4-82e2-89894e651e89")
# rm_friends("6c1363ba-ae17-43e4-82e2-89894e651e89", "7c1363ba-ae17-43e4-82e2-89894e651e89")
# hello=(get_user_grps("6c1363ba-ae17-43e4-82e2-89894e651e89"))
# print(grp_info_by_id(hello[0]))