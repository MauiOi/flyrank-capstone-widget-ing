# Embeddable Widget & Lead-Capture Platform

FlyRank Internship — Backend Track Capstone

A platform for creating embeddable widgets (signup forms, CTAs, popovers) that
customers can install on any website with a single `<script>` tag. Submissions
from visitors are validated, rate-limited, spam-checked, enriched with
geolocation, and viewable in an owner dashboard.

## Architecture

````
Widget Owner (authenticated, Bearer token)
  -> Widget Management API -> Supabase (tenant-isolated by owner_id)
  -> Dashboard API (stats: counts, geo breakdown)

Customer Website (any origin)
  <script src="widget.js?id=...">
  -> GET /widgets/:id/config   (public, cached, CORS)
  -> renders widget form

Website Visitor
  -> POST /submissions          (public, CORS)
     | Pydantic validation      -> 422 on malformed
     | size check                -> 413 on oversized
     | honeypot check            -> 400 if bot-filled
     | rate limit (5/min/IP)     -> 429 on burst
     | geo enrichment: ip-api.com -> mock fallback -> stored without geo
     | store submission
     | email side effect (failure never blocks the response)
````

Backend: FastAPI (Python) + Supabase (Postgres + Auth).

## Setup

1. Clone this repo and `cd` into it
2. `py -m pip install -r requirements.txt`
3. Copy `.env.example` to `.env`
4. Fill in `SUPABASE_URL`, `SUPABASE_KEY` (anon key), and `SUPABASE_SERVICE_KEY` (service_role key) from your Supabase project's Settings -> API Keys and Settings -> Data API
5. Run the SQL in `schema.sql` (Supabase dashboard -> SQL Editor) to create the `widgets` and `submissions` tables
6. `py -m uvicorn app.main:app --reload`
7. Seed demo data: `py app\seed.py`
8. Open `http://localhost:8000/docs` to explore the API

### Try the embed flow

```
cd test-site
py -m http.server 5500
```

Open `http://localhost:5500` — the widget renders from a different origin than the API (port 5500 vs 8000), proving the cross-origin embed works.

## API overview

**Auth (public)**
- `POST /auth/signup`
- `POST /auth/login`

**Widget management (authenticated, tenant-isolated)**
- `POST /widgets`, `GET /widgets`, `GET /widgets/{id}`, `PATCH /widgets/{id}`, `DELETE /widgets/{id}`
- `GET /dashboard/{widget_id}` — submission stats

**Widget delivery (public, cached)**
- `GET /widgets/{id}/config` — short cache
- `GET /widget.js` — long cache, versioned

**Public submission (rate-limited, validated, CORS)**
- `POST /submissions`

## Limitations

- Backend uses the Supabase `service_role` key to bypass Row-Level Security; tenant isolation is enforced entirely at the application layer via `owner_id` filters on every query, not by database policies.
- The second geo provider (ipapi.co) blocks automated/non-browser requests via a Cloudflare bot challenge — confirmed during development. It's mocked deterministically per the capstone brief's guidance, so the fallback chain proof doesn't depend on a flaky third-party's uptime. The primary provider (ip-api.com) is live and real.
- Email confirmation is a console log, not a real send — its failure-handling is what's graded, not actual delivery.
- Only one widget type is exercised end-to-end (`signup_form`); the data model supports `cta` and `popover` but they're not separately tested.
- No real CDN, hosting, or custom domain — everything runs locally, per the capstone's stated scope.