from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.auth import get_current_user, supabase

router = APIRouter(prefix="/widgets", tags=["widgets"])


class WidgetInput(BaseModel):
    type: str
    title: str
    description: Optional[str] = None
    fields: list = []
    button_text: str = "Submit"


@router.post("", status_code=201)
def create_widget(data: WidgetInput, user=Depends(get_current_user)):
    row = {
        "owner_id": user.id,
        "type": data.type,
        "title": data.title,
        "description": data.description,
        "fields": data.fields,
        "button_text": data.button_text,
    }
    res = supabase.table("widgets").insert(row).execute()
    return res.data[0]


@router.get("")
def list_widgets(user=Depends(get_current_user)):
    res = supabase.table("widgets").select("*").eq("owner_id", user.id).execute()
    return res.data


@router.get("/{widget_id}")
def get_widget(widget_id: str, user=Depends(get_current_user)):
    res = supabase.table("widgets").select("*").eq("id", widget_id).eq("owner_id", user.id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Widget not found")
    return res.data[0]


@router.patch("/{widget_id}")
def update_widget(widget_id: str, data: WidgetInput, user=Depends(get_current_user)):
    existing = supabase.table("widgets").select("id").eq("id", widget_id).eq("owner_id", user.id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Widget not found")
    res = supabase.table("widgets").update(data.model_dump()).eq("id", widget_id).eq("owner_id", user.id).execute()
    return res.data[0]


@router.delete("/{widget_id}", status_code=204)
def delete_widget(widget_id: str, user=Depends(get_current_user)):
    existing = supabase.table("widgets").select("id").eq("id", widget_id).eq("owner_id", user.id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Widget not found")
    supabase.table("widgets").delete().eq("id", widget_id).eq("owner_id", user.id).execute()