import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase import create_client, AuthApiError

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY")

# Separate client, dedicated to login/signup only. Kept isolated from the
# service_role client in app/auth.py so logging in never mutates the
# session used for database queries elsewhere in the app.
auth_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


class AuthInput(BaseModel):
    email: str
    password: str


@router.post("/signup", status_code=201)
def signup(data: AuthInput):
    if not data.email or not data.password:
        raise HTTPException(status_code=400, detail="Missing email or password")
    try:
        res = auth_client.auth.sign_up({"email": data.email, "password": data.password})
    except AuthApiError as e:
        raise HTTPException(status_code=400, detail=e.message)
    if res.user is None:
        raise HTTPException(status_code=400, detail="Signup failed")
    return {"user": res.user}


@router.post("/login")
def login(data: AuthInput):
    if not data.email or not data.password:
        raise HTTPException(status_code=400, detail="Missing email or password")
    try:
        res = auth_client.auth.sign_in_with_password({"email": data.email, "password": data.password})
    except AuthApiError:
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    if res.session is None:
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    return {"access_token": res.session.access_token, "refresh_token": res.session.refresh_token}