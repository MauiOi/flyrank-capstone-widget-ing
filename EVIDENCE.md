## Multi-tenant isolation
Created widget as user 1 (id: feb26ccb-9729-4f96-8afc-cda4bfd85627).
Attempted GET /widgets/feb26ccb-9729-4f96-8afc-cda4bfd85627 authenticated as user 2.

Result: 404 Not Found
{"error":"Widget not found"}

User 2 was authenticated successfully (no 401) but correctly denied access
to user 1's widget — isolation enforced via owner_id filter on every query.

## Cached widget delivery
GET /widgets/{id}/config -> Cache-Control: public, max-age=60
GET /widget.js -> Cache-Control: public, max-age=31536000, immutable

Config is short-lived (owner can update widget settings), script is cached
long-term since it's a versioned bundle that only changes on release.

## Widget renders on second origin
Served customer test page from http://localhost:5500 (separate from API at :8000).
Widget script loaded via <script src="http://localhost:8000/widget.js?id=...">,
fetched config, and rendered a form with the widget's title and button text.
No CORS errors in browser console.

## Public submission endpoint

**Preflight (CORS):**
OPTIONS /submissions with Origin: http://localhost:5500
-> Access-Control-Allow-Origin: *

**Valid submission:**
POST /submissions {"widget_id":"feb26ccb...","data":{"value":"test@example.com"}}
-> 201, row stored with owner_id auto-filled from widget, ip_address captured

**Malformed payload (missing widget_id):**
POST /submissions {"data":{"value":"x"}}
-> 422, not 500

**Oversized payload (6000 bytes):**
POST /submissions with large data field
-> 413, not 500

**Invalid widget_id (well-formed but doesn't exist):**
POST /submissions {"widget_id":"00000000-0000-0000-0000-000000000000",...}
-> 400, not 500

## Abuse protection — rate limiting
Fired 6 rapid POST /submissions from same IP (limit: 5/minute).
Requests 1-5: 201 success. Request 6: 429.
(Verified in isolation after quota reset: single request after 65s wait -> 201 success,
confirming limiter resets correctly per window.)

## Abuse protection — honeypot
POST /submissions with hp_field populated (simulating a bot filling every field)
-> 400, submission rejected, not stored.

## Geo enrichment — provider fallback chain
Both providers up: country=United States, city=Ashburn (real ip-api.com lookup for 8.8.8.8)
Provider A forced down: country=Canada, city=Toronto (fallback provider B)
Both providers down: country=null, city=null, still 201 (graceful degradation, never fails)

Note: ipapi.co (originally planned provider B) blocks automated requests via
Cloudflare bot challenge, confirmed via direct curl-equivalent test. Provider B
is mocked per the capstone brief's guidance to keep the fallback proof
deterministic; provider A (ip-api.com) is the live, real lookup.

## Safe side effects — email failure isolation
EMAIL_FORCE_FAIL=true forced send_confirmation() to raise.
Result: submission still returned 201 and was stored normally.
Server log showed no unhandled traceback — exception caught and swallowed
in the try/except around the notification call.

## Dashboard API
GET /dashboard/{widget_id} authenticated as owner
-> 200, total_submissions, counts_by_day, geo_breakdown correctly aggregated

Attempted same request authenticated as a different user
-> 404 Not Found (tenant isolation holds on dashboard endpoint too)