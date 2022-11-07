from supabase import create_client, Client
from core.config import settings




class DB: 
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)



db = DB