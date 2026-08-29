from .client import supabase
from datetime import datetime

#GROUPS
def create_grp(name, creator_uid):
    # group create karne ke liye group name decide karna padega and then supabase khud ek uid allot kar dega
    # creator_uid tokens se lenge as current user uid de dega
    try:
        grp_data={
            "name": name,
            "created_by": creator_uid,
            "members": [creator_uid]
        }
        supabase.table("groups").insert(grp_data).execute()
        print("group created")
    except Exception as e:
        print(f"Error: {e}")
        raise e

def add_mem(grp_name, arr_name):
    #member uids ka ek list pass hoga jispe iterate karke group members me user uids add karnge

    # remember: abhi users.in_grp me grp uids nahi ja rahi wo bhejna hai for each user

    try:
        response=supabase.table("groups").select("members").eq("name", grp_name).single().execute()
        mem_list=response.data["members"]
        for items in arr_name:
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




#######################
def get_group_by_id(id):
    try:
        response=supabase.table("groups").select("*").eq("id", id).execute()
        if not response.data:
            raise Exception("Group not found")
        return response.data[0]
    except Exception as e:
        print(f"Error: {e}")
        raise e

def get_groupnames_from_ids(ids):
    try:
        if not ids:
            return {}
        str_ids = [str(i) for i in ids]
        response = supabase.table("groups").select("id", "name").in_("id", str_ids).execute()
        return {str(row["id"]): row["name"] for row in response.data}
    except Exception as e:
        print(f"Error fetching group names by ids: {e}")
        return {}