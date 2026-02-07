-- Migration: 004_meetings.sql
-- Meeting tracking for compliance and relationship management

CREATE TYPE meeting_type_enum AS ENUM (
    'INITIAL_CONSULTATION', 'FACT_FIND', 'RECOMMENDATION',
    'ANNUAL_REVIEW', 'AD_HOC', 'PHONE_CALL', 'VIDEO_CALL'
);

CREATE TYPE meeting_status_enum AS ENUM (
    'SCHEDULED', 'CONFIRMED', 'COMPLETED', 'CANCELLED', 'NO_SHOW'
);

CREATE TABLE IF NOT EXISTS meetings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    case_id UUID REFERENCES cases(id),
    
    -- Meeting Details
    meeting_type meeting_type_enum NOT NULL,
    status meeting_status_enum DEFAULT 'SCHEDULED',
    title TEXT,
    
    -- Timing
    scheduled_at TIMESTAMPTZ NOT NULL,
    duration_minutes INT DEFAULT 60,
    completed_at TIMESTAMPTZ,
    
    -- Location/Method
    location TEXT,
    is_virtual BOOLEAN DEFAULT FALSE,
    meeting_link TEXT,
    
    -- Content
    agenda JSONB, -- Pre-meeting agenda items
    notes TEXT, -- Post-meeting notes
    summary TEXT, -- AI-generated summary
    
    -- Key Discussion Points (for compliance searching)
    topics_discussed JSONB, -- Array: ['retirement', 'risk', 'protection']
    risk_discussions TEXT, -- Specific risk discussion content for compliance
    recommendations_made JSONB, -- Structured recommendations
    client_concerns JSONB, -- Array of concerns raised
    
    -- Follow-up
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_notes TEXT,
    
    -- Pre-meeting Pack
    pack_sent_at TIMESTAMPTZ,
    pack_documents JSONB, -- List of documents sent
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_meetings_client ON meetings(client_id);
CREATE INDEX idx_meetings_scheduled ON meetings(scheduled_at);
CREATE INDEX idx_meetings_status ON meetings(status);
CREATE INDEX idx_meetings_type ON meetings(meeting_type);

-- Full text search on notes and discussions
CREATE INDEX idx_meetings_notes_fts ON meetings USING gin(to_tsvector('english', COALESCE(notes, '') || ' ' || COALESCE(risk_discussions, '')));

-- Trigger for updated_at
CREATE TRIGGER meetings_updated
    BEFORE UPDATE ON meetings
    FOR EACH ROW
    EXECUTE FUNCTION update_client_profile_timestamp();
