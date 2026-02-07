-- Create email_drafts table
DROP TYPE IF EXISTS draft_status_enum CASCADE;
CREATE TYPE draft_status_enum AS ENUM (
    'GENERATED', 'EDITED', 'APPROVED', 'SENT', 'DISCARDED'
);

DROP TYPE IF EXISTS email_tone_enum CASCADE;
CREATE TYPE email_tone_enum AS ENUM (
    'FORMAL', 'FRIENDLY', 'EMPATHETIC', 'URGENT', 'FOLLOW_UP'
);

CREATE TABLE IF NOT EXISTS email_drafts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id),
    case_id UUID REFERENCES cases(id),
    meeting_id UUID REFERENCES meetings(id),
    
    -- Email Content
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    tone email_tone_enum DEFAULT 'FORMAL',
    
    -- Recipients
    to_email TEXT NOT NULL,
    to_name TEXT,
    cc_emails JSONB,
    
    -- Status
    status draft_status_enum DEFAULT 'GENERATED',
    
    -- Context
    context_type TEXT, -- 'CHASE', 'FOLLOW_UP', 'MEETING_SUMMARY', 'INTRODUCTION'
    context_summary TEXT, -- What this email is about
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create action_items table
CREATE TABLE IF NOT EXISTS action_items (
  id uuid primary key default uuid_generate_v4(),
  client_id uuid references clients(id),
  case_id uuid references cases(id),
  meeting_id uuid references meetings(id),
  
  title text not null,
  owner text, -- 'ADVISOR', 'AGENT', 'CLIENT'
  status text default 'PENDING', -- 'PENDING', 'COMPLETED', 'IN_PROGRESS'
  priority text default 'STANDARD',
  due_date timestamptz,
  created_at timestamptz default now()
);

-- Enable RLS
alter table email_drafts enable row level security;
alter table action_items enable row level security;

-- Create policies (open for now)
DROP POLICY IF EXISTS "Enable all access for all users" ON email_drafts;
create policy "Enable all access for all users" on email_drafts for all using (true) with check (true);

DROP POLICY IF EXISTS "Enable all access for all users" ON action_items;
create policy "Enable all access for all users" on action_items for all using (true) with check (true);
