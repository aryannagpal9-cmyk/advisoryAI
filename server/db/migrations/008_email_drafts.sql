-- Migration: 008_email_drafts.sql
-- AI-generated email drafts

CREATE TYPE draft_status_enum AS ENUM (
    'GENERATED', 'EDITED', 'APPROVED', 'SENT', 'DISCARDED'
);

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
    
    -- Generation Metadata
    prompt_used TEXT,
    model_used TEXT,
    
    -- Editing
    original_body TEXT, -- Before edits
    edited_at TIMESTAMPTZ,
    
    -- Sending
    sent_at TIMESTAMPTZ,
    message_id TEXT, -- Email provider message ID
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_drafts_client ON email_drafts(client_id);
CREATE INDEX idx_drafts_status ON email_drafts(status);
CREATE INDEX idx_drafts_created ON email_drafts(created_at DESC);
