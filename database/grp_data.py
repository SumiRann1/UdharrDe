from .client import supabase #.removed before client for local checking
from datetime import datetime

#GROUPS
def create_grp(name, creator_uid):
    # group create karne ke liye group name decide karna padega and then supabase khud ek uid allot kar dega
    # creator_uid tokens se lenge as current user uid de dega
    try:
        grp_data={
            "name": name,
            "created_by": creator_uid,
            "members": []
        }
        supabase.table("groups").insert(grp_data).execute()
        print("group created")
        add_mem(name, [str(creator_uid)])
    except Exception as e:
        print(f"Error: {e}")
        raise e

def grpid_by_name(name):
    try:
        response=supabase.table("groups").select("*").eq("name", name).single().execute()
        return response.data["id"]
    except Exception as e:
        print(f"Error: {e}")
        raise e

def grp_info_by_id(gid):
    '''get all grp info using grp id
    if u don't have grp id and have grp name then use grpid_by_name(name) and get the id and then call this function'''
    try:
        response=supabase.table("groups").select("*").eq("id", gid).execute()
        return response.data[0]
    except Exception as e:
        print(f"Error: {e}")
        raise e

def add_in_grp(uid, grp_id):
    try:
        response=supabase.table("users").select("in_grp").eq("id", uid).single().execute()
        grp_list=response.data["in_grp"]
        if(grp_id not in grp_list):
            grp_list.append(grp_id)
            supabase.table("users").update({"in_grp": grp_list}).eq("id", uid).execute()
            print(f"{grp_id} added in user {uid}")
        else:
            print(f"{grp_id} already in user {uid} list")
    except Exception as e:
        print(f"Error: {e}")
        raise e

def rm_in_grp(uid, grp_id):
    try:
        response=supabase.table("users").select("in_grp").eq("id", uid).execute()
        grp_list=response.data[0]["in_grp"]
        if(grp_id in grp_list):
            grp_list.remove(grp_id)
            supabase.table("users").update({"in_grp": grp_list}).eq("id", uid).execute()
            print(f"{grp_id} rm from user {uid}")
        else:
            print(f"{grp_id} doesn't exist in user {uid} list")
    except Exception as e:
        print(f"Error: e")
        raise e

def add_mem(grp_name, arr_name):
    #member uids ka ek list pass hoga jispe iterate karke group members me user uids add karnge

    # remember: abhi users.in_grp me grp uids nahi ja rahi wo bhejna hai for each user

    try:
        response=supabase.table("groups").select("members", "id").eq("name", grp_name).single().execute()
        mem_list=response.data["members"]
        grp_id=response.data["id"]
        for items in arr_name:
            add_in_grp(str(items), grp_id)
            if items not in mem_list:
                mem_list.append(items)
                print(f"{items} added")
            else:
                print(f"{items} already in grp")
        supabase.table("groups").update({"members": mem_list}).eq("name", grp_name).execute()
        print(f"users added {arr_name} in grp {grp_name}")
    except Exception as e:
        print(f"Error: {e}")
        raise e

def rm_member(grp_name, uid):
    try:
        response=supabase.table("groups").select("members", "id").eq("name", grp_name).execute()
        mem_list=response.data[0]["members"]
        grp_id=response.data[0]["id"]
        rm_in_grp(uid, grp_id)
        if(uid in mem_list):
            mem_list.remove(uid)
            print(f"user {uid} removed from grp {grp_name}")
        else:
            print(f"user {uid} not in grp {grp_name}")
        supabase.table("groups").update({"members": mem_list}).eq("name", grp_name).execute()
        print(f"user {uid} removed from grp {grp_name}")
    except Exception as e:
        print(f"Error: {e}")
        raise e
    



#---------------------------------------------------------------------
# create_grp("group1", "6c1363ba-ae17-43e4-82e2-89894e651e89")
# print(grpid_by_name("group1"))
# add_mem("group1", ["7c1363ba-ae17-43e4-82e2-89894e651e89"])
