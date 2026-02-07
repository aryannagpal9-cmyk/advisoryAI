-- Migration: 005_action_items.sql
-- Track commitments, follow-ups, and action items

CREATE TYPE action_status_enum AS ENUM (
    'PENDING', 'IN_PROGRESS', 'COMPLETED', 'OVERDUE', 'CANCELLED'
);

CREATE TYPE action_owner_enum AS ENUM (
    'ADVISOR', 'CLIENT', 'PROVIDER', 'PARAPLANNER', 'ADMIN'
);

CREATE TYPE action_priority_enum AS ENUM (
    'LOW', 'MEDIUM', 'HIGH', 'URGENT'
);

CREATE TABLE IF NOT EXISTS action_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id),
    case_id UUID REFERENCES cases(id),
    meeting_id UUID REFERENCES meetings(id),
    request_id UUID REFERENCES requests(id),
    
    -- Action Details
    title TEXT NOT NULL,
    description TEXT,
    
    -- Ownership and Status
    owner action_owner_enum NOT NULL DEFAULT 'ADVISOR',
    assigned_to TEXT, -- Specific person name
    status action_status_enum DEFAULT 'PENDING',
    priority action_priority_enum DEFAULT 'MEDIUM',
    
    -- Timing
    due_date TIMESTAMPTZ,
    reminder_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Tracking
    promised_at TIMESTAMPTZ, -- When was this promised to client
    promise_context TEXT, -- What was said
    
    -- Categorization
    category TEXT, -- 'DOCUMENT', 'EMAIL', 'CALL', 'RESEARCH', 'ADMIN'
    
    -- Automation
    auto_generated BOOLEAN DEFAULT FALSE,
    source_type TEXT, -- 'MEETING', 'EMAIL', 'CHASE', 'MANUAL'
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_action_items_client ON action_items(client_id);
CREATE INDEX idx_action_items_status ON action_items(status);
CREATE INDEX idx_action_items_due ON action_items(due_date);
CREATE INDEX idx_action_items_owner ON action_items(owner);
CREATE INDEX idx_action_items_overdue ON action_items(status, due_date) 
    WHERE status IN ('PENDING', 'IN_PROGRESS');

-- Trigger for updated_at and auto-overdue
CREATE TRIGGER action_items_updated
    BEFORE UPDATE ON action_items
    FOR EACH ROW
    EXECUTE FUNCTION update_client_profile_timestamp();

-- Function to mark overdue items
CREATE OR REPLACE FUNCTION mark_overdue_actions()
RETURNS void AS $$
BEGIN
    UPDATE action_items 
    SET status = 'OVERDUE'
    WHERE status IN ('PENDING', 'IN_PROGRESS')
    AND due_date < NOW();
END;
$$ LANGUAGE plpgsql;
