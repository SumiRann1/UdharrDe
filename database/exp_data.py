from client import supabase #.removed before client for local checking

def create_exp_user(name: str, p_uid: str, amt: float, u_uid: str, comment=None):
    try:
        data={
            "name":name,
            "paid_by": p_uid,
            "amt": amt,
            "u_pay": u_uid,
            "g_pay": None,
            "split": {},
            "diff": 0,
            "comment": comment
        }
        supabase.table("expenses").insert(data).execute()
        print(f"{name} expense added")
    except Exception as e:
        print(f"Error: {e}")
        raise e

# def create_exp_grp(name, p_uid, amt, g_uid, split, comment):


# def create_exp_grp(name, p_uid, amt, g_uid, split, comment):


create_exp_user("exp1", "6c1363ba-ae17-43e4-82e2-89894e651e89", 100, "7c1363ba-ae17-43e4-82e2-89894e651e89", "world world")