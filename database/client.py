import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
logger = logging.getLogger(__name__)

load_dotenv()

try:
    SUPABASE_URL=os.getenv("SUPABASE_URL")
    SUPABASE_KEY=os.getenv("SUPABASE_KEY")
    if SUPABASE_KEY and SUPABASE_URL:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase connected")
    else:
        supabase=None
        logger.warning("Supabase not connected, Set correct APIs")
except Exception as e:
    supabase=None
    logger.error(f"Supabase not found, Server Error: {e}")