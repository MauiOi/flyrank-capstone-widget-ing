## Multi-tenant isolation
Created widget as user 1 (id: feb26ccb-9729-4f96-8afc-cda4bfd85627).
Attempted GET /widgets/feb26ccb-9729-4f96-8afc-cda4bfd85627 authenticated as user 2.

Result: 404 Not Found
{"error":"Widget not found"}

User 2 was authenticated successfully (no 401) but correctly denied access
to user 1's widget — isolation enforced via owner_id filter on every query.