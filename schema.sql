create table widgets (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id),
  type text not null check (type in ('signup_form', 'cta', 'popover')),
  title text not null,
  description text,
  fields jsonb not null default '[]',
  button_text text not null default 'Submit',
  version int not null default 1,
  created_at timestamptz not null default now()
);

create table submissions (
  id uuid primary key default gen_random_uuid(),
  widget_id uuid not null references widgets(id) on delete cascade,
  owner_id uuid not null,
  data jsonb not null,
  ip_address text,
  country text,
  city text,
  created_at timestamptz not null default now()
);

create index on widgets (owner_id);
create index on submissions (widget_id);
create index on submissions (owner_id);