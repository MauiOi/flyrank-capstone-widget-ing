from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Dict, Any
from app.auth import supabase
from app.rate_limit import limiter
from app.services.geo import enrich_ip
from app.services.notify import send_confirmation

router = APIRouter(tags=["submissions"])

MAX_PAYLOAD_BYTES = 5000
HONEYPOT_FIELD = "hp_field"


class SubmissionInput(BaseModel):
    widget_id: str
    data: Dict[str, Any] = Field(default_factory=dict)


@router.post("/submissions", status_code=201)
@limiter.limit("5/minute")
def create_submission(payload: SubmissionInput, request: Request):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_PAYLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Payload too large")

    if not payload.data:
        raise HTTPException(status_code=400, detail="Submission data required")

    if payload.data.get(HONEYPOT_FIELD):
        raise HTTPException(status_code=400, detail="Submission rejected")

    widget_res = supabase.table("widgets").select("id, owner_id").eq("id", payload.widget_id).execute()
    if not widget_res.data:
        raise HTTPException(status_code=400, detail="Invalid widget_id")

    owner_id = widget_res.data[0]["owner_id"]
    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else None)
    geo = enrich_ip(client_ip)

    row = {
        "widget_id": payload.widget_id,
        "owner_id": owner_id,
        "data": payload.data,
        "ip_address": client_ip,
        "country": geo.get("country"),
        "city": geo.get("city"),
    }
    res = supabase.table("submissions").insert(row).execute()
    stored = res.data[0]

    try:
        send_confirmation(stored)
    except Exception:
        pass

    return stored