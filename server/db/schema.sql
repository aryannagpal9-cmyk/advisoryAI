-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- 1. Owners (Polymorphic: Clients or Providers)
-- Using a single table or separate? Separate is cleaner for strict typing, but 'owner_id' on requests needs to be flexible.
-- Let's use separate tables and an 'owner_type' enum on requests.

create type owner_type_enum as enum ('CLIENT', 'PROVIDER', 'ADVISOR');
create type request_status_enum as enum ('PENDING', 'WAITING', 'PARTIAL', 'INVALID', 'FULFILLED', 'ESCALATED', 'PAUSED', 'CLOSED');
create type request_priority_enum as enum ('STANDARD', 'HIGH', 'CRITICAL');

create table if not exists clients (
  id uuid primary key default uuid_generate_v4(),
  name text not null,
  email text not null,
  phone text,
  created_at timestamptz default now()
);

create table if not exists providers (
  id uuid primary key default uuid_generate_v4(),
  name text not null,
  email text not null, -- For receiving LOAs
  portal_url text,
  standard_response_days int default 10, -- Default delay profile
  created_at timestamptz default now()
);

create table if not exists cases (
  id uuid primary key default uuid_generate_v4(),
  advisor_id uuid not null, -- Assumes auth.users
  client_id uuid references clients(id),
  title text not null, -- e.g. "Pension Consolidation"
  description text,
  status text default 'ACTIVE',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists requests (
  id uuid primary key default uuid_generate_v4(),
  case_id uuid references cases(id) on delete cascade,
  
  -- The "First Class" Request
  title text not null, -- e.g. "Passport Copy" or "Aviva LOA"
  description text,
  
  -- Ownership
  owner_type owner_type_enum not null,
  client_owner_id uuid references clients(id),
  provider_owner_id uuid references providers(id),
  
  -- State Machine
  status request_status_enum default 'PENDING',
  priority request_priority_enum default 'STANDARD',
  
  -- Time & Policy
  created_at timestamptz default now(),
  next_action_at timestamptz default now(), -- Trigger for the Agent
  last_action_at timestamptz,
  retry_count int default 0,
  max_retries int default 3,
  
  -- Secure Uploads
  upload_token uuid default uuid_generate_v4(), -- For magic links
  upload_expires_at timestamptz,
  
  -- Check constraints to ensure one owner
  constraint one_owner check (
    (owner_type = 'CLIENT' and client_owner_id is not null and provider_owner_id is null) or
    (owner_type = 'PROVIDER' and provider_owner_id is not null and client_owner_id is null)
  )
);

create table if not exists audit_logs (
  id uuid primary key default uuid_generate_v4(),
  request_id uuid references requests(id),
  case_id uuid references cases(id),
  action text not null, -- e.g. "EMAIL_SENT", "STATUS_CHANGE"
  actor text not null, -- "AGENT" or "ADVISOR"
  reason text, -- "Policy Rule #3: Time Elapsed > 7 days"
  metadata jsonb,
  created_at timestamptz default now()
);

-- Policy Rules Configuration (Optional, can be hardcoded in Python too)
create table if not exists policy_rules (
  id serial primary key,
  name text not null,
  condition_json jsonb, -- Flexible rule definition
  action_type text not null,
  created_at timestamptz default now()
);
