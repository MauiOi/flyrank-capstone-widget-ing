from fastapi import APIRouter, Depends, HTTPException
from collections import defaultdict
from app.auth import get_current_user, supabase

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{widget_id}")
def get_dashboard(widget_id: str, user=Depends(get_current_user)):
    widget_res = supabase.table("widgets").select("id").eq("id", widget_id).eq("owner_id", user.id).execute()
    if not widget_res.data:
        raise HTTPException(status_code=404, detail="Widget not found")

    subs_res = supabase.table("submissions").select("*").eq("widget_id", widget_id).eq("owner_id", user.id).execute()
    submissions = subs_res.data

    counts_by_day = defaultdict(int)
    geo_breakdown = defaultdict(int)

    for s in submissions:
        created = s.get("created_at", "")
        day = created[:10] if created else "unknown"
        counts_by_day[day] += 1

        country = s.get("country") or "unknown"
        geo_breakdown[country] += 1

    return {
        "widget_id": widget_id,
        "total_submissions": len(submissions),
        "counts_by_day": dict(counts_by_day),
        "geo_breakdown": dict(geo_breakdown),
    }