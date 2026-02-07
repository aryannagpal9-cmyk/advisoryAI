-- Migration: 006_insights.sql
-- Proactive insights and recommendations storage

CREATE TYPE insight_category_enum AS ENUM (
    'INVESTMENT', 'TAX_PLANNING', 'RETIREMENT', 'PROTECTION',
    'COMPLIANCE', 'RELATIONSHIP', 'BUSINESS', 'OPPORTUNITY',
    'RISK_ALERT', 'FOLLOW_UP'
);

CREATE TYPE insight_priority_enum AS ENUM (
    'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
);

CREATE TABLE IF NOT EXISTS insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id),
    
    -- Insight Content
    category insight_category_enum NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    recommendation TEXT,
    
    -- Priority and Urgency
    priority insight_priority_enum DEFAULT 'MEDIUM',
    expires_at TIMESTAMPTZ, -- Some insights are time-sensitive
    
    -- Source and Query
    query_type TEXT, -- The original query that generated this
    source_agent TEXT, -- Which agent generated it
    
    -- Metrics/Data Points
    metrics JSONB, -- Relevant numbers/data
    affected_value DECIMAL(14, 2), -- e.g., potential tax saving
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    is_dismissed BOOLEAN DEFAULT FALSE,
    is_actioned BOOLEAN DEFAULT FALSE,
    actioned_at TIMESTAMPTZ,
    action_taken TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_insights_client ON insights(client_id);
CREATE INDEX idx_insights_category ON insights(category);
CREATE INDEX idx_insights_priority ON insights(priority);
CREATE INDEX idx_insights_unread ON insights(is_read, is_dismissed) 
    WHERE is_read = FALSE AND is_dismissed = FALSE;
CREATE INDEX idx_insights_created ON insights(created_at DESC);
