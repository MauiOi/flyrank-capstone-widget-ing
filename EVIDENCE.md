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