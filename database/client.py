import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

try:
    SUPABASE_URL=os.getenv("SUPABASE_URL")
    SUPABASE_KEY=os.getenv("SUPABASE_KEY")
    if SUPABASE_KEY and SUPABASE_URL:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase connected")
    else:
        supabase=None
        print("Supabase not connected")
except:
    supabase=None
    print("Supabase not found")