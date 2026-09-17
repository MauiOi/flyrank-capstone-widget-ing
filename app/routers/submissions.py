from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Dict, Any
from app.auth import supabase

router = APIRouter(tags=["submissions"])

MAX_PAYLOAD_BYTES = 5000


class SubmissionInput(BaseModel):
    widget_id: str
    data: Dict[str, Any] = Field(default_factory=dict)


@router.post("/submissions", status_code=201)
def create_submission(payload: SubmissionInput, request: Request):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_PAYLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Payload too large")

    if not payload.data:
        raise HTTPException(status_code=400, detail="Submission data required")

    widget_res = supabase.table("widgets").select("id, owner_id").eq("id", payload.widget_id).execute()
    if not widget_res.data:
        raise HTTPException(status_code=400, detail="Invalid widget_id")

    owner_id = widget_res.data[0]["owner_id"]
    client_ip = request.client.host if request.client else None

    row = {
        "widget_id": payload.widget_id,
        "owner_id": owner_id,
        "data": payload.data,
        "ip_address": client_ip,
    }
    res = supabase.table("submissions").insert(row).execute()
    return res.data[0]