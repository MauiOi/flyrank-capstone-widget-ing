import os
from dotenv import load_dotenv
from supabase import create_client, AuthApiError

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Same client-isolation rule as app/auth.py and app/routers/auth.py:
# auth_client only ever does login/signup, db_client only ever does table
# queries. Never let the two mix — see BUILDLOG.md for why.
auth_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
db_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demopassword123"


def get_or_create_demo_user():
    try:
        res = auth_client.auth.sign_up({"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
        if res.user:
            return res.user.id
    except AuthApiError:
        pass  # user already exists — fall through to login instead

    res = auth_client.auth.sign_in_with_password({"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
    return res.user.id


def seed():
    owner_id = get_or_create_demo_user()
    print(f"Demo user id: {owner_id}")

    widget = db_client.table("widgets").insert({
        "owner_id": owner_id,
        "type": "signup_form",
        "title": "Demo Signup Widget",
        "description": "Seeded demo widget for evaluation",
        "fields": [],
        "button_text": "Subscribe",
    }).execute().data[0]
    print(f"Created widget: {widget['id']}")

    sample_submissions = [
        {"value": "alice@example.com", "country": "United States", "city": "Ashburn"},
        {"value": "bob@example.com", "country": "Canada", "city": "Toronto"},
        {"value": "carol@example.com", "country": None, "city": None},
    ]
    for s in sample_submissions:
        db_client.table("submissions").insert({
            "widget_id": widget["id"],
            "owner_id": owner_id,
            "data": {"value": s["value"]},
            "ip_address": "0.0.0.0",
            "country": s["country"],
            "city": s["city"],
        }).execute()

    print("\nSeed complete.")
    print(f"Demo login -> email: {DEMO_EMAIL}  password: {DEMO_PASSWORD}")
    print(f"Demo widget id: {widget['id']}")
    print(f"Try after logging in as demo user: GET /dashboard/{widget['id']}")


if __name__ == "__main__":
    seed()