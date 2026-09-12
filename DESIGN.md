# Design Doc — Embeddable Widget & Lead-Capture Platform

## Problem
Let a customer (widget owner) create embeddable widgets (signup form / CTA / popover),
embed them on any external website with one <script> tag, and safely capture
submissions from visitors on sites we don't control — validated, spam-filtered,
enriched with geo data, and viewable in a dashboard.

## Data model

### widgets
| field       | type      | notes                                  |
|-------------|-----------|-----------------------------------------|
| id          | uuid      | primary key                            |
| owner_id    | uuid      | Supabase auth user id — acts as tenant_id |
| type        | text      | signup_form / cta / popover            |
| title       | text      |                                         |
| description | text      | nullable                               |
| fields      | jsonb     | form field definitions                 |
| button_text | text      |                                         |
| version     | int       | bumped on script-affecting changes     |
| created_at  | timestamp |                                         |

### submissions
| field       | type      | notes                                  |
|-------------|-----------|-----------------------------------------|
| id          | uuid      | primary key                            |
| widget_id   | uuid      | FK -> widgets.id                       |
| owner_id    | uuid      | denormalized from widget, for fast tenant-scoped queries |
| data        | jsonb     | submitted form values                  |
| ip_address  | text      | for rate limiting + geo lookup         |
| country     | text      | nullable — from enrichment             |
| city        | text      | nullable — from enrichment             |
| created_at  | timestamp |                                         |

Tenant isolation: every widgets/submissions query filters by owner_id == current
authenticated user's id. No shared reads across owners.

## API surface

**Path A — Widget owner (authenticated, Bearer token)**
- POST   /widgets
- GET    /widgets
- GET    /widgets/{id}
- PATCH  /widgets/{id}
- DELETE /widgets/{id}
- GET    /dashboard/{widget_id}       (stats: counts, geo breakdown)

**Path B — Customer site (public, cached, CORS-open)**
- GET /widgets/{id}/config            (cache-control: short-lived)
- GET /widget.js                      (cache-control: long, versioned URL)

**Path C — Website visitor (public, CORS, protected)**
- POST /submissions                   (rate-limited, spam-checked, validated)

## Layer sketch