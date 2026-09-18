import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, AuthApiError

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Dedicated to database operations only. Never call supabase.auth.sign_in_* or
# sign_up on this instance — doing so swaps its session and silently breaks
# the service_role bypass on every query made afterward.
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

bearer_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    try:
        res = supabase.auth.get_user(token)
    except AuthApiError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if res.user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return res.user