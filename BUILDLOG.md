## Session N — shared Supabase client bug
- I was wrong about: initial code had login/signup and database queries
  sharing one Supabase client instance. Logging in silently swapped that
  client's session, causing every database query afterward to run under
  RLS instead of the intended service_role bypass — returned empty results
  with no error, hard to diagnose.
- What I changed: split into two separate clients — one dedicated to
  auth (login/signup) using the anon key, one dedicated to database
  queries using the service_role key. Documented in app/auth.py to
  prevent regression.